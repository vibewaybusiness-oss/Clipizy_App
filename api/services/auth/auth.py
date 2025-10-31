"""
Unified Authentication Service
Complete authentication system in a single file
"""

import json
import logging
import os
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

import httpx
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from api.config.logging import get_auth_logger
import os
from api.models import User
from api.models.pricing import CreditsTransactionType
from api.schemas import UserCreate
from api.services.business.pricing_service import credits_service
from api.services.database import get_db

logger = get_auth_logger()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 30

# Security scheme for dependency injection
security = HTTPBearer()


# UTILITY FUNCTIONS
def generate_email_based_uuid(email: str) -> str:
    """Generate a deterministic UUID based on email address"""
    namespace = uuid.UUID("6ba7b810-9dad-11d1-80b4-00c04fd430c8")  # DNS namespace
    return str(uuid.uuid5(namespace, email.lower().strip()))


def create_user_storage_structure(user_id: str) -> bool:
    """Create user-specific storage structure in S3/local storage"""
    try:
        from api.services.storage import backend_storage_service
        
        # Use backend storage service
        # Note: User storage structure creation is handled automatically by the database
        result = True  # Backend storage doesn't need explicit user structure creation
        logger.info(f"User storage structure creation result for {user_id}: {result}")
        return result

    except Exception as e:
        logger.error(f"Failed to create user storage structure: {str(e)}")
        logger.warning("Continuing without storage structure creation")
        return False


# CORE AUTHENTICATION CLASS
class AuthService:
    def __init__(self):
        logger.info("AuthService initialized")

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        try:
            result = pwd_context.verify(plain_password, hashed_password)
            logger.debug(f"Password verification {'successful' if result else 'failed'}")
            return result
        except Exception as e:
            logger.error(f"Password verification error: {str(e)}")
            return False

    def get_password_hash(self, password: str) -> str:
        """Hash a password"""
        try:
            hashed = pwd_context.hash(password)
            logger.debug("Password hashed successfully")
            return hashed
        except Exception as e:
            logger.error(f"Password hashing error: {str(e)}")
            raise

    def authenticate_user(self, db: Session, email: str, password: str) -> Optional[User]:
        """Authenticate a user with email and password"""
        logger.info(f"Attempting to authenticate user: {email}")
        try:
            user = db.query(User).filter(User.email == email).first()
            if not user:
                logger.warning(f"User not found: {email}")
                return None

            if not self.verify_password(password, user.hashed_password):
                logger.warning(f"Invalid password for user: {email}")
                return None

            logger.info(f"User authenticated successfully: {email}")
            return user
        except Exception as e:
            logger.error(f"Authentication error for user {email}: {str(e)}")
            return None

    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None):
        """Create a JWT access token"""
        try:
            to_encode = data.copy()
            if expires_delta:
                expire = datetime.utcnow() + expires_delta
            else:
                expire = datetime.utcnow() + timedelta(days=7)  # 7 days for access token
            to_encode.update({"exp": expire, "type": "access"})
            encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
            logger.info(f"Access token created for user: {data.get('sub', 'unknown')}")
            return encoded_jwt
        except Exception as e:
            logger.error(f"Token creation error: {str(e)}")
            raise

    def create_refresh_token(self, data: dict, expires_delta: Optional[timedelta] = None):
        """Create a JWT refresh token"""
        try:
            to_encode = data.copy()
            if expires_delta:
                expire = datetime.utcnow() + expires_delta
            else:
                expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
            to_encode.update({"exp": expire, "type": "refresh"})
            encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
            logger.info(f"Refresh token created for user: {data.get('sub', 'unknown')}")
            return encoded_jwt
        except Exception as e:
            logger.error(f"Refresh token creation error: {str(e)}")
            raise

    def verify_refresh_token(self, token: str) -> Optional[dict]:
        """Verify a refresh token"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            if payload.get("type") != "refresh":
                return None
            return payload
        except JWTError:
            return None

    def verify_token(self, token: str) -> Optional[dict]:
        """Verify and decode a JWT token"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            logger.debug(f"Token verified for user: {payload.get('sub', 'unknown')}")
            return payload
        except JWTError as e:
            logger.warning(f"Token verification failed: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Token verification error: {str(e)}")
            return None

    def get_user_by_id(self, db: Session, user_id: str) -> Optional[User]:
        """Get user by ID"""
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if user:
                logger.debug(f"User found: {user.email}")
            else:
                logger.warning(f"User not found with ID: {user_id}")
            return user
        except Exception as e:
            logger.error(f"Error getting user by ID {user_id}: {str(e)}")
            return None

    def update_user_last_login(self, db: Session, user_id: str) -> bool:
        """Update user's last login timestamp"""
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if user:
                user.last_login = datetime.utcnow()
                db.commit()
                logger.debug(f"Updated last login for user: {user.email}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error updating last login for user {user_id}: {str(e)}")
            return False


# USER CREATION SERVICE
class UserCreationService:
    def __init__(self):
        logger.info("UserCreationService initialized")

    def create_complete_user_profile(
        self,
        db: Session,
        email: str,
        name: Optional[str] = None,
        password: Optional[str] = None,
        oauth_provider: Optional[str] = None,
        oauth_data: Optional[Dict[str, Any]] = None,
        custom_user_id: Optional[str] = None,
    ) -> User:
        """Create a complete user profile with database record, directory structure, and initial credits"""
        logger.info(f"Creating complete user profile for: {email}")

        try:
            # 1. Check if user already exists
            existing_user = db.query(User).filter(User.email == email).first()
            if existing_user:
                logger.info(f"User already exists, updating info: {email}")
                return self._update_existing_user(db, existing_user, name, oauth_provider, oauth_data)

            # 2. Generate user ID
            user_id = custom_user_id or generate_email_based_uuid(email)
            logger.info(f"Generated user ID: {user_id}")

            # 3. Create user in database with initial credits
            user = self._create_database_user_with_credits(
                db, email, name, password, oauth_provider, oauth_data, user_id
            )
            if not user:
                raise Exception("Failed to create database user")

            # 4. Create user directory structure
            self._create_user_directory_structure(str(user.id))

            # 5. Initialize user profile files
            self._initialize_user_profile_files(str(user.id), user)

            # 6. Create user-specific storage structure
            create_user_storage_structure(str(user.id))

            # 7. Initialize user settings in database
            self._initialize_user_settings(db, user)

            # 8. Create initial credits transaction record
            self._create_initial_credits_transaction(db, user)

            logger.info(
                f"✅ Complete user profile created successfully for: {user.email} (ID: {user.id}) with {user.credits_balance} credits"
            )
            return user

        except Exception as e:
            logger.error(f"❌ Complete user profile creation failed for {email}: {str(e)}")
            db.rollback()
            raise

    def _create_database_user_with_credits(
        self,
        db: Session,
        email: str,
        name: Optional[str],
        password: Optional[str],
        oauth_provider: Optional[str],
        oauth_data: Optional[Dict[str, Any]],
        user_id: str,
    ) -> Optional[User]:
        """Create user in database with initial credits"""
        try:
            # Hash password if provided
            hashed_password = None
            if password:
                hashed_password = auth_service.get_password_hash(password)

            # Build user settings
            settings = {
                "created_via": "oauth" if oauth_provider else "email",
                "preferences": {"theme": "system", "notifications": True, "language": "en"},
            }

            if oauth_provider:
                settings["oauth_provider"] = oauth_provider

                # Store provider-specific data
                if oauth_data:
                    if oauth_provider == "google" and oauth_data.get("google_id"):
                        settings["google_id"] = oauth_data["google_id"]
                    elif oauth_provider == "github" and oauth_data.get("github_id"):
                        settings["github_id"] = oauth_data["github_id"]

            # Create user with initial credits
            db_user = User(
                id=user_id,
                email=email,
                hashed_password=hashed_password,
                username=name,
                is_active=True,
                is_verified=oauth_provider is not None,  # OAuth users are pre-verified
                avatar_url=oauth_data.get("picture") if oauth_data else None,
                settings=settings,
                credits_balance=1000,  # Initial credits
                total_credits_earned=1000,  # Initial credits earned
                total_credits_spent=0,  # No credits spent yet
            )

            db.add(db_user)
            db.commit()
            db.refresh(db_user)

            logger.info(f"Database user created with 1000 initial credits: {email} (ID: {db_user.id})")
            return db_user

        except Exception as e:
            logger.error(f"Database user creation failed: {str(e)}")
            db.rollback()
            return None

    def _create_initial_credits_transaction(self, db: Session, user: User):
        """Create initial credits transaction record"""
        try:
            transaction = credits_service.add_credits(
                db=db,
                user_id=str(user.id),
                amount=1000,
                transaction_type=CreditsTransactionType.EARNED,
                description="Welcome bonus - Initial credits for new users",
                reference_id=None,
                reference_type="welcome_bonus",
            )
            logger.info(f"Created initial credits transaction for user {user.email}: {transaction.id}")
        except Exception as e:
            logger.error(f"Failed to create initial credits transaction for user {user.email}: {str(e)}")
            # Don't raise as this is not critical for user creation

    def _update_existing_user(
        self,
        db: Session,
        user: User,
        name: Optional[str],
        oauth_provider: Optional[str],
        oauth_data: Optional[Dict[str, Any]],
    ) -> User:
        """Update existing user with new information"""
        try:
            updated = False

            # Update name if provided and not set
            if name and not user.username:
                user.username = name
                updated = True

            # Update OAuth provider info
            if oauth_provider:
                if not user.settings:
                    user.settings = {}

                user.settings["oauth_provider"] = oauth_provider
                user.settings["created_via"] = "oauth"
                updated = True

                # Store provider-specific data
                if oauth_data:
                    if oauth_provider == "google" and oauth_data.get("google_id"):
                        user.settings["google_id"] = oauth_data["google_id"]
                    elif oauth_provider == "github" and oauth_data.get("github_id"):
                        user.settings["github_id"] = oauth_data["github_id"]

                    # Update avatar if provided
                    if oauth_data.get("picture") and not user.avatar_url:
                        user.avatar_url = oauth_data["picture"]
                        updated = True

            # Ensure user has initial credits if they don't have any
            if user.credits_balance == 0 and user.total_credits_earned == 0:
                user.credits_balance = 1000
                user.total_credits_earned = 1000
                updated = True
                logger.info(f"Added initial credits to existing user: {user.email}")

                # Create transaction record
                self._create_initial_credits_transaction(db, user)

            if updated:
                db.commit()
                logger.info(f"Updated existing user: {user.email}")

            return user

        except Exception as e:
            logger.error(f"Failed to update existing user {user.email}: {str(e)}")
            db.rollback()
            raise

    def _create_user_directory_structure(self, user_id: str):
        """Create user directory structure (SQL-only system - no directories needed)"""
        try:
            # No longer creating user directories - all data is managed in SQL database
            logger.info(f"User directory structure skipped for {user_id} (SQL-only system)")

        except Exception as e:
            logger.error(f"Failed to process user directory structure for {user_id}: {str(e)}")
            raise

    def _initialize_user_profile_files(self, user_id: str, user: User):
        """Initialize user profile files (SQL-only system - no JSON files needed)"""
        try:
            # No longer creating JSON files - all data is managed in SQL database
            logger.info(f"User profile initialized in SQL database for {user_id}")

        except Exception as e:
            logger.error(f"Failed to initialize user profile for {user_id}: {str(e)}")
            raise

    def _initialize_user_settings(self, db: Session, user: User):
        """Initialize user settings in database"""
        try:
            # Update user with default settings if not already set
            if not user.settings:
                user.settings = {
                    "notifications": {"email": True, "push": True, "marketing": False},
                    "privacy": {"profile_public": False, "show_email": False},
                    "security": {"two_factor_enabled": False, "login_notifications": True},
                    "preferences": {"theme": "system", "language": "en", "timezone": "UTC"},
                    "billing": {"plan": "free", "payment_method": None},
                }
            db.commit()
            logger.info(f"User settings initialized for: {user.email}")

        except Exception as e:
            logger.error(f"Failed to initialize user settings: {str(e)}")
            # Don't raise as this is not critical

    def create_user(self, db: Session, user: UserCreate) -> User:
        """Create a new user with complete setup using centralized profile service"""
        logger.info(f"Creating new user: {user.email}")
        try:
            # Use centralized profile service for email users
            db_user = self.create_complete_user_profile(
                db=db, email=user.email, name=user.name, password=user.password, oauth_provider=None  # Email user
            )
            logger.info(
                f"User created successfully with centralized profile service: {user.email} (ID: {db_user.id}) with {db_user.credits_balance} credits"
            )
            return db_user
        except ValueError as e:
            # Re-raise ValueError (email already exists) without logging as error
            logger.warning(f"User creation validation failed for {user.email}: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"User creation error for {user.email}: {str(e)}")
            db.rollback()
            raise

    def create_token_pair(self, user: User) -> tuple[str, str]:
        """Create access and refresh token pair for user"""
        access_token = auth_service.create_access_token(
            data={"sub": str(user.id), "email": user.email, "name": user.username}
        )
        refresh_token = auth_service.create_refresh_token(data={"sub": str(user.id)})
        return access_token, refresh_token


# OAUTH SERVICE
class OAuthService:
    def __init__(self):
        # Load Google OAuth credentials from JSON file
        try:
            with open("api/config/json/client_secret_google_api.json", "r") as f:
                google_creds = json.load(f)
                self.GOOGLE_CLIENT_ID = google_creds["web"]["client_id"]
                self.google_client_secret = google_creds["web"]["client_secret"]
        except (FileNotFoundError, KeyError) as e:
            logger.error(f"Failed to load Google OAuth credentials: {e}")
            self.GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
            self.google_client_secret = os.getenv("GOOGLE_CLIENT_SECRET")

        # GitHub OAuth credentials from environment variables
        self.OAUTH_GITHUB_CLIENT_ID = os.getenv("OAUTH_GITHUB_CLIENT_ID")
        self.github_client_secret = os.getenv("GITHUB_CLIENT_SECRET")
        # Use centralized frontend URL from settings
        frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
        self.redirect_uri = os.getenv("OAUTH_REDIRECT_URI", f"{frontend_url}/auth/callback")

    async def get_google_user_info(self, code: str) -> Optional[Dict[str, Any]]:
        """Get user info from Google OAuth"""
        try:
            import time
            start_time = time.time()
            print(f"🚨 [CRITICAL] Google OAuth STARTED at {time.time()}")
            
            # Use instance variables instead of reading environment variables dynamically
            GOOGLE_CLIENT_ID = self.GOOGLE_CLIENT_ID
            google_client_secret = self.google_client_secret
            redirect_uri = self.redirect_uri

            logger.info(f"🔵 [GOOGLE] Starting Google OAuth user info retrieval...")
            print(f"🚨 [CRITICAL] Google OAuth LOGGED at {time.time()}")
            logger.info(f"Google OAuth - Client ID: {GOOGLE_CLIENT_ID[:10]}...")
            logger.info(
                f"Google OAuth - Client Secret: {google_client_secret[:10] if google_client_secret else 'None'}..."
            )
            logger.info(f"Google OAuth - Redirect URI: {redirect_uri}")
            logger.info(f"Google OAuth - Code: {code[:10]}...")

            # Exchange code for access token
            token_url = "https://oauth2.googleapis.com/token"
            token_data = {
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": google_client_secret,
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": redirect_uri,
            }

            async with httpx.AsyncClient(timeout=5.0) as client:
                step_start = time.time()
                logger.info(f"Making token exchange request to: {token_url}")
                token_response = await client.post(token_url, data=token_data)
                logger.info(f"⏱️ [GOOGLE] Token exchange took {time.time() - step_start:.2f}s")
                logger.info(f"Google token response status: {token_response.status_code}")
                if not token_response.is_success:
                    error_text = token_response.text
                    logger.error(f"Google token exchange failed: {error_text}")
                    logger.error(f"Request data: {token_data}")
                    raise Exception(f"Google token exchange failed: {error_text}")
                token_response.raise_for_status()
                token_info = token_response.json()

                access_token = token_info["access_token"]
                logger.info(f"Successfully obtained access token: {access_token[:10]}...")

                # Get user info
                user_info_url = "https://www.googleapis.com/oauth2/v2/userinfo"
                headers = {"Authorization": f"Bearer {access_token}"}
                logger.info(f"Making user info request to: {user_info_url}")

                step_start = time.time()
                user_response = await client.get(user_info_url, headers=headers)
                logger.info(f"⏱️ [GOOGLE] User info request took {time.time() - step_start:.2f}s")
                user_response.raise_for_status()
                user_info = user_response.json()
                logger.info(f"Successfully obtained user info: {user_info.get('email', 'no email')}")

                # Generate email-based UUID instead of using Google's numeric ID
                email_based_uuid = generate_email_based_uuid(user_info["email"])

                logger.info(f"✅ [GOOGLE] Total Google OAuth took {time.time() - start_time:.2f}s")
                return {
                    "id": email_based_uuid,  # Use email-based UUID instead of Google ID
                    "email": user_info["email"],
                    "name": user_info.get("name"),
                    "picture": user_info.get("picture"),
                    "provider": "google",
                    "google_id": user_info["id"],  # Store original Google ID for reference
                }

        except Exception as e:
            logger.error(f"Google OAuth error: {str(e)}")
            print(f"DEBUG: Google OAuth error: {str(e)}")
            return None

    async def get_google_tokens(self, code: str) -> Optional[Dict[str, Any]]:
        """Get access and refresh tokens from Google OAuth"""
        try:
            GOOGLE_CLIENT_ID = self.GOOGLE_CLIENT_ID
            google_client_secret = self.google_client_secret
            redirect_uri = self.redirect_uri

            # Exchange code for access token
            token_url = "https://oauth2.googleapis.com/token"
            token_data = {
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": google_client_secret,
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": redirect_uri,
            }

            async with httpx.AsyncClient(timeout=5.0) as client:
                token_response = await client.post(token_url, data=token_data)
                token_response.raise_for_status()
                token_info = token_response.json()

                return {
                    "access_token": token_info["access_token"],
                    "refresh_token": token_info.get("refresh_token"),
                    "expires_in": token_info.get("expires_in", 3600),
                    "token_type": token_info.get("token_type", "Bearer")
                }

        except Exception as e:
            logger.error(f"Google token exchange error: {str(e)}")
            return None

    async def get_github_user_info(self, code: str) -> Optional[Dict[str, Any]]:
        """Get user info from GitHub OAuth"""
        try:
            # Use instance variables instead of reading environment variables dynamically
            OAUTH_GITHUB_CLIENT_ID = self.OAUTH_GITHUB_CLIENT_ID
            github_client_secret = self.github_client_secret

            # Exchange code for access token
            token_url = "https://github.com/login/oauth/access_token"
            token_data = {
                "client_id": OAUTH_GITHUB_CLIENT_ID,
                "client_secret": github_client_secret,
                "code": code,
            }

            async with httpx.AsyncClient() as client:
                token_response = await client.post(token_url, data=token_data, headers={"Accept": "application/json"})
                token_response.raise_for_status()
                token_info = token_response.json()

                access_token = token_info["access_token"]

                # Get user info
                user_info_url = "https://api.github.com/user"
                headers = {"Authorization": f"Bearer {access_token}"}

                user_response = await client.get(user_info_url, headers=headers)
                user_response.raise_for_status()
                user_info = user_response.json()

                # Get user email if not public
                email = user_info.get("email")
                if not email:
                    email_response = await client.get("https://api.github.com/user/emails", headers=headers)
                    if email_response.status_code == 200:
                        emails = email_response.json()
                        primary_email = next((e["email"] for e in emails if e.get("primary")), None)
                        if primary_email:
                            email = primary_email

                # Generate email-based UUID instead of using GitHub's numeric ID
                user_email = email or f"{user_info['login']}@github.local"
                email_based_uuid = generate_email_based_uuid(user_email)

                return {
                    "id": email_based_uuid,  # Use email-based UUID instead of GitHub ID
                    "email": user_email,
                    "name": user_info.get("name") or user_info.get("login"),
                    "picture": user_info.get("avatar_url"),
                    "provider": "github",
                    "github_id": str(user_info["id"]),  # Store original GitHub ID for reference
                }

        except Exception as e:
            logger.error(f"GitHub OAuth error: {str(e)}")
            return None

    def get_or_create_user(self, db: Session, oauth_user_info: Dict[str, Any]) -> Optional[User]:
        """Get existing user or create new one from OAuth info - optimized for fast OAuth response"""
        try:
            import time
            start_time = time.time()
            logger.info(f"🔵 [USER] Starting get_or_create_user for: {oauth_user_info['email']}")
            
            # Check if user already exists
            step_start = time.time()
            existing_user = db.query(User).filter(User.email == oauth_user_info["email"]).first()
            logger.info(f"⏱️ [USER] User lookup took {time.time() - step_start:.2f}s")
            
            if existing_user:
                logger.info(f"OAuth user already exists: {existing_user.email}")
                logger.info(f"✅ [USER] Total get_or_create_user took {time.time() - start_time:.2f}s")
                return existing_user

            # Create new OAuth user without storage structure (will be created during onboarding)
            user_id = generate_email_based_uuid(oauth_user_info["email"])
            logger.info(f"Creating new OAuth user: {oauth_user_info['email']} (ID: {user_id})")

            # Build user settings
            settings = {
                "created_via": "oauth",
                "preferences": {"theme": "system", "notifications": True, "language": "en"},
                "oauth_provider": oauth_user_info["provider"],
            }

            # Add provider-specific data
            if oauth_user_info["provider"] == "google" and oauth_user_info.get("google_id"):
                settings["google_id"] = oauth_user_info["google_id"]
            elif oauth_user_info["provider"] == "github" and oauth_user_info.get("github_id"):
                settings["github_id"] = oauth_user_info["github_id"]

            # Create user with initial credits but without storage structure
            step_start = time.time()
            db_user = User(
                id=user_id,
                email=oauth_user_info["email"],
                username=oauth_user_info.get("name", oauth_user_info["email"].split("@")[0]),
                hashed_password=None,  # OAuth users don't have passwords
                is_active=True,
                is_admin=False,
                credits_balance=1000,  # Initial credits
                total_credits_earned=1000,
                total_credits_spent=0,
                settings=settings,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                last_login=datetime.utcnow()
            )

            db.add(db_user)
            db.commit()
            db.refresh(db_user)
            logger.info(f"⏱️ [USER] User creation + commit took {time.time() - step_start:.2f}s")

            logger.info(
                f"OAuth user created successfully: {db_user.email} (ID: {db_user.id}) with {db_user.credits_balance} credits"
            )
            logger.info(f"✅ [USER] Total get_or_create_user took {time.time() - start_time:.2f}s")
            return db_user

        except Exception as e:
            logger.error(f"Error processing OAuth user: {str(e)}")
            db.rollback()
            return None

    def get_google_auth_url(self) -> str:
        """Generate Google OAuth URL"""
        # Use instance variables instead of reading environment variables dynamically
        GOOGLE_CLIENT_ID = self.GOOGLE_CLIENT_ID
        redirect_uri = self.redirect_uri

        if not GOOGLE_CLIENT_ID:
            raise HTTPException(
                status_code=503,
                detail={
                    "error_code": "OAUTH_NOT_CONFIGURED",
                    "message": "Google OAuth is not configured",
                    "details": "Please set GOOGLE_CLIENT_ID environment variable or provide client_secret_google_api.json file in config/json/ directory."
                }
            )

        params = {
            "client_id": GOOGLE_CLIENT_ID,
            "redirect_uri": redirect_uri,
            "scope": "openid email profile",
            "response_type": "code",
            "access_type": "offline",
        }

        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"https://accounts.google.com/o/oauth2/v2/auth?{query_string}"

    def get_github_auth_url(self) -> str:
        """Generate GitHub OAuth URL"""
        # Use instance variables instead of reading environment variables dynamically
        OAUTH_GITHUB_CLIENT_ID = self.OAUTH_GITHUB_CLIENT_ID
        redirect_uri = self.redirect_uri

        if not OAUTH_GITHUB_CLIENT_ID:
            raise HTTPException(
                status_code=503,
                detail={
                    "error_code": "OAUTH_NOT_CONFIGURED",
                    "message": "GitHub OAuth is not configured",
                    "details": "Please set OAUTH_GITHUB_CLIENT_ID environment variable."
                }
            )

        params = {
            "client_id": OAUTH_GITHUB_CLIENT_ID,
            "redirect_uri": redirect_uri,
            "scope": "user:email",
            "response_type": "code",
        }

        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"https://github.com/login/oauth/authorize?{query_string}"

    def get_youtube_auth_url(self) -> str:
        """Generate YouTube OAuth URL"""
        GOOGLE_CLIENT_ID = self.GOOGLE_CLIENT_ID
        redirect_uri = self.redirect_uri

        if not GOOGLE_CLIENT_ID:
            raise HTTPException(
                status_code=503,
                detail={
                    "error_code": "OAUTH_NOT_CONFIGURED",
                    "message": "YouTube OAuth is not configured",
                    "details": "Please set GOOGLE_CLIENT_ID environment variable or provide client_secret_google_api.json file in config/json/ directory."
                }
            )

        params = {
            "client_id": GOOGLE_CLIENT_ID,
            "redirect_uri": redirect_uri,
            "scope": "https://www.googleapis.com/auth/youtube.upload https://www.googleapis.com/auth/youtube.readonly",
            "response_type": "code",
            "access_type": "offline",
            "prompt": "consent",
            "state": "youtube"
        }

        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"https://accounts.google.com/o/oauth2/v2/auth?{query_string}"


# AUTHENTICATION DEPENDENCIES
class AuthDependencies:
    """Centralized authentication dependencies"""
    
    @staticmethod
    def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(security), 
        db: Session = Depends(get_db)
    ) -> User:
        """
        Get the current authenticated user from JWT token with full database validation
        
        Returns:
            User: The authenticated user object
            
        Raises:
            HTTPException: 401 if authentication fails
        """
        try:
            token = credentials.credentials
            payload = auth_service.verify_token(token)
            
            if not payload:
                logger.warning("Invalid token provided")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication token",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            user_id = payload.get("sub")
            if not user_id:
                logger.warning("No user ID in token payload")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token payload",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            user = auth_service.get_user_by_id(db, user_id)
            if not user:
                logger.warning(f"User not found for ID: {user_id}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not found",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            if not user.is_active:
                logger.warning(f"Inactive user attempted access: {user_id}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User account is inactive",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            logger.debug(f"User authenticated successfully: {user.email}")
            return user
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    @staticmethod
    def get_current_user_simple(
        credentials: HTTPAuthorizationCredentials = Depends(security)
    ) -> dict:
        """
        Get current user token data without database validation (for performance-critical endpoints)
        
        Returns:
            dict: Token payload data
            
        Raises:
            HTTPException: 401 if token is invalid
        """
        try:
            token = credentials.credentials
            payload = auth_service.verify_token(token)
            
            if not payload:
                logger.warning("Invalid token provided (simple auth)")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication token",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            user_id = payload.get("sub")
            if not user_id:
                logger.warning("No user ID in token payload (simple auth)")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token payload",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            logger.debug(f"User token validated successfully: {user_id}")
            return payload
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Simple authentication error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    @staticmethod
    def get_admin_user(
        credentials: HTTPAuthorizationCredentials = Depends(security),
        db: Session = Depends(get_db)
    ) -> User:
        """
        Get current user and verify admin privileges
        
        Returns:
            User: The authenticated admin user
            
        Raises:
            HTTPException: 401 if not authenticated, 403 if not admin
        """
        user = AuthDependencies.get_current_user(credentials, db)
        
        if not user.is_admin:
            logger.warning(f"Non-admin user attempted admin access: {user.email}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin privileges required",
            )
        
        logger.debug(f"Admin user authenticated: {user.email}")
        return user


# Convenience functions for backward compatibility and ease of use
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get the current authenticated user (full validation)"""
    return AuthDependencies.get_current_user(credentials, db)


def get_current_user_simple(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """Get current user token data (no database validation)"""
    return AuthDependencies.get_current_user_simple(credentials)


def get_admin_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get current user with admin privileges"""
    return AuthDependencies.get_admin_user(credentials, db)


# USER MANAGEMENT SERVICE
class UserManagementService:
    def __init__(self):
        logger.info("UserManagementService initialized")

    def create_auth_response(self, user: User, access_token: str, refresh_token: str) -> dict:
        """Create standardized authentication response"""
        return {
            "user": {
                "id": str(user.id),
                "email": user.email,
                "name": user.username,
                "avatar": user.avatar_url,
                "is_active": user.is_active,
                "is_admin": user.is_admin,
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "last_login": user.last_login.isoformat() if user.last_login else None,
            },
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }

    def create_token_pair(self, user: User) -> tuple[str, str]:
        """Create access and refresh token pair for user"""
        access_token = auth_service.create_access_token(
            data={"sub": str(user.id), "email": user.email, "name": user.username}
        )
        refresh_token = auth_service.create_refresh_token(data={"sub": str(user.id)})
        return access_token, refresh_token

    def get_user_profile_data(self, user: User) -> dict:
        """Get formatted user profile data"""
        return {
            "user_id": str(user.id),
            "email": user.email,
            "username": user.username,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "profile": {
                "display_name": user.username,
                "bio": getattr(user, 'bio', ''),
                "avatar_url": user.avatar_url or "",
                "website": "",
                "location": "",
                "timezone": "UTC",
            },
            "preferences": {
                "theme": "system",
                "language": "en",
                "notifications": {"email": True, "push": True, "marketing": False},
                "privacy": {"profile_public": False, "show_activity": True},
            },
            "billing": {"plan": "free", "payment_method": None, "billing_address": None, "invoices": []},
            "security": {"two_factor_enabled": False, "login_history": [], "api_keys": []},
        }

    def update_user_profile(self, db: Session, user: User, profile_data: dict) -> bool:
        """Update user profile information"""
        try:
            if "profile" in profile_data:
                profile = profile_data["profile"]
                if "display_name" in profile:
                    user.username = profile["display_name"]
                if "bio" in profile:
                    user.bio = profile["bio"]
            
            user.updated_at = datetime.utcnow()
            db.commit()
            return True
        except Exception as e:
            logger.error(f"Error updating user profile: {str(e)}")
            db.rollback()
            return False

    def get_user_settings_formatted(self, user: User) -> dict:
        """Get formatted user settings for frontend"""
        db_settings = user.settings or {}
        
        return {
            "profile": {
                "name": user.username or "",
                "email": user.email,
                "bio": getattr(user, 'bio', ''),
                "avatar": user.avatar_url or "",
                "website": "",
                "location": "",
            },
            "notifications": {
                "emailNotifications": db_settings.get("notifications", {}).get("email", True),
                "pushNotifications": db_settings.get("notifications", {}).get("push", True),
                "marketingEmails": db_settings.get("notifications", {}).get("marketing", False),
                "weeklyDigest": db_settings.get("notifications", {}).get("weekly_digest", True),
                "projectUpdates": db_settings.get("notifications", {}).get("project_updates", True),
            },
            "privacy": {
                "profileVisibility": "public" if db_settings.get("privacy", {}).get("profile_public", False) else "private",
                "showEmail": db_settings.get("privacy", {}).get("show_email", False),
                "allowComments": db_settings.get("privacy", {}).get("allow_comments", True),
                "dataSharing": db_settings.get("privacy", {}).get("data_sharing", False),
                "analyticsTracking": db_settings.get("privacy", {}).get("analytics_tracking", True),
                "marketingEmails": db_settings.get("privacy", {}).get("marketing_emails", False),
                "profileDiscovery": db_settings.get("privacy", {}).get("profile_discovery", False),
                "activityVisibility": db_settings.get("privacy", {}).get("activity_visibility", "followers"),
            },
            "security": {
                "twoFactorEnabled": db_settings.get("security", {}).get("two_factor_enabled", False),
                "loginNotifications": db_settings.get("security", {}).get("login_notifications", True),
                "sessionTimeout": db_settings.get("security", {}).get("session_timeout", 30),
                "apiAccess": db_settings.get("security", {}).get("api_access", False),
                "dataExport": db_settings.get("security", {}).get("data_export", True),
                "accountDeletion": db_settings.get("security", {}).get("account_deletion", False),
            },
            "preferences": {
                "theme": db_settings.get("preferences", {}).get("theme", "system"),
                "language": db_settings.get("preferences", {}).get("language", "en"),
                "timezone": db_settings.get("preferences", {}).get("timezone", "UTC"),
                "autoSave": db_settings.get("preferences", {}).get("auto_save", True),
                "highQuality": db_settings.get("preferences", {}).get("high_quality", True),
            },
            "billing": {
                "plan": getattr(user, 'plan', 'free'),
                "payment_methods": [],
                "billing_address": None,
                "next_billing_date": None,
                "subscription_status": "active",
            },
        }

    def update_user_settings(self, db: Session, user: User, settings_data: dict) -> bool:
        """Update user settings in database"""
        try:
            if user.settings is None:
                user.settings = {}

            # Update profile information
            if "profile" in settings_data:
                profile = settings_data["profile"]
                if "name" in profile:
                    user.username = profile["name"]
                if "bio" in profile:
                    user.bio = profile["bio"]

            # Update settings in database
            db_settings = user.settings.copy()

            # Map frontend settings to database format
            if "notifications" in settings_data:
                db_settings["notifications"] = {
                    "email": settings_data["notifications"].get("emailNotifications", True),
                    "push": settings_data["notifications"].get("pushNotifications", True),
                    "marketing": settings_data["notifications"].get("marketingEmails", False),
                    "weekly_digest": settings_data["notifications"].get("weeklyDigest", True),
                    "project_updates": settings_data["notifications"].get("projectUpdates", True),
                }

            if "privacy" in settings_data:
                db_settings["privacy"] = {
                    "profile_public": settings_data["privacy"].get("profileVisibility") == "public",
                    "show_email": settings_data["privacy"].get("showEmail", False),
                    "allow_comments": settings_data["privacy"].get("allowComments", True),
                    "data_sharing": settings_data["privacy"].get("dataSharing", False),
                    "analytics_tracking": settings_data["privacy"].get("analyticsTracking", True),
                    "marketing_emails": settings_data["privacy"].get("marketingEmails", False),
                    "profile_discovery": settings_data["privacy"].get("profileDiscovery", False),
                    "activity_visibility": settings_data["privacy"].get("activityVisibility", "followers"),
                }

            if "security" in settings_data:
                db_settings["security"] = {
                    "two_factor_enabled": settings_data["security"].get("twoFactorEnabled", False),
                    "login_notifications": settings_data["security"].get("loginNotifications", True),
                    "session_timeout": settings_data["security"].get("sessionTimeout", 30),
                    "api_access": settings_data["security"].get("apiAccess", False),
                    "data_export": settings_data["security"].get("dataExport", True),
                    "account_deletion": settings_data["security"].get("accountDeletion", False),
                }

            if "preferences" in settings_data:
                db_settings["preferences"] = {
                    "theme": settings_data["preferences"].get("theme", "system"),
                    "language": settings_data["preferences"].get("language", "en"),
                    "timezone": settings_data["preferences"].get("timezone", "UTC"),
                    "auto_save": settings_data["preferences"].get("autoSave", True),
                    "high_quality": settings_data["preferences"].get("highQuality", True),
                }

            # Update database
            user.settings = db_settings
            user.updated_at = datetime.utcnow()
            db.commit()
            return True
        except Exception as e:
            logger.error(f"Error updating user settings: {str(e)}")
            db.rollback()
            return False

    def get_user_billing_data(self, user: User) -> dict:
        """Get formatted user billing data"""
        return {
            "user_id": str(user.id),
            "current_plan": "free",
            "billing_info": {"payment_methods": [], "billing_address": None, "tax_id": None},
            "subscription": {"status": "active", "next_billing_date": None, "cancel_at_period_end": False},
            "usage": {"projects_created": 0, "storage_used_mb": 0, "api_calls_made": 0},
        }

    def get_user_storage_usage(self, user: User) -> dict:
        """Get user storage usage information"""
        return {
            "total_size_bytes": 0,
            "total_size_mb": 0.0,
            "file_count": 0,
            "storage_limit_mb": 1000,  # 1GB limit
            "storage_used_percent": 0.0,
        }

    def get_app_settings(self, user: User) -> dict:
        """Get application settings for the user"""
        db_settings = user.settings or {}
        
        return {
            "theme": db_settings.get("preferences", {}).get("theme", "system"),
            "language": db_settings.get("preferences", {}).get("language", "en"),
            "timezone": db_settings.get("preferences", {}).get("timezone", "UTC"),
            "soundEnabled": db_settings.get("preferences", {}).get("sound_enabled", True),
            "soundVolume": db_settings.get("preferences", {}).get("sound_volume", 70),
            "animationsEnabled": db_settings.get("preferences", {}).get("animations_enabled", True),
            "reducedMotion": db_settings.get("preferences", {}).get("reduced_motion", False),
            "autoPlay": db_settings.get("preferences", {}).get("auto_play", False),
            "quality": db_settings.get("preferences", {}).get("quality", "1080p"),
            "maxVideoLength": db_settings.get("preferences", {}).get("max_video_length", 10),
            "moderateLyrics": db_settings.get("preferences", {}).get("moderate_lyrics", False),
            "dataSaving": db_settings.get("preferences", {}).get("data_saving", False),
            "developerMode": db_settings.get("preferences", {}).get("developer_mode", False),
        }

    def update_app_settings(self, db: Session, user: User, settings_data: dict) -> bool:
        """Update application settings for the user"""
        try:
            if user.settings is None:
                user.settings = {}

            db_settings = user.settings.copy()

            # Update preferences in database
            if "preferences" not in db_settings:
                db_settings["preferences"] = {}

            db_settings["preferences"].update({
                "theme": settings_data.get("theme", "system"),
                "language": settings_data.get("language", "en"),
                "timezone": settings_data.get("timezone", "UTC"),
                "sound_enabled": settings_data.get("soundEnabled", True),
                "sound_volume": settings_data.get("soundVolume", 70),
                "animations_enabled": settings_data.get("animationsEnabled", True),
                "reduced_motion": settings_data.get("reducedMotion", False),
                "auto_play": settings_data.get("autoPlay", False),
                "quality": settings_data.get("quality", "1080p"),
                "max_video_length": settings_data.get("maxVideoLength", 10),
                "moderate_lyrics": settings_data.get("moderateLyrics", False),
                "data_saving": settings_data.get("dataSaving", False),
                "developer_mode": settings_data.get("developerMode", False),
            })

            user.settings = db_settings
            user.updated_at = datetime.utcnow()
            db.commit()
            return True
        except Exception as e:
            logger.error(f"Error updating app settings: {str(e)}")
            db.rollback()
            return False

    def get_social_settings(self, user: User) -> dict:
        """Get social media settings for the user"""
        db_settings = user.settings or {}
        
        return {
            "autoTagClipizi": db_settings.get("social", {}).get("auto_tag_clipizi", True),
            "includeWatermark": db_settings.get("social", {}).get("include_watermark", True),
            "autoPost": db_settings.get("social", {}).get("auto_post", False),
            "postDelay": db_settings.get("social", {}).get("post_delay", 5),
            "includeHashtags": db_settings.get("social", {}).get("include_hashtags", True),
            "customHashtags": db_settings.get("social", {}).get("custom_hashtags", "#music #clipizy #ai"),
            "tagFriends": db_settings.get("social", {}).get("tag_friends", False),
            "crossPost": db_settings.get("social", {}).get("cross_post", False),
        }

    def update_social_settings(self, db: Session, user: User, settings_data: dict) -> bool:
        """Update social media settings for the user"""
        try:
            if user.settings is None:
                user.settings = {}

            db_settings = user.settings.copy()

            # Update social settings in database
            if "social" not in db_settings:
                db_settings["social"] = {}

            db_settings["social"].update({
                "auto_tag_clipizi": settings_data.get("autoTagClipizi", True),
                "include_watermark": settings_data.get("includeWatermark", True),
                "auto_post": settings_data.get("autoPost", False),
                "post_delay": settings_data.get("postDelay", 5),
                "include_hashtags": settings_data.get("includeHashtags", True),
                "custom_hashtags": settings_data.get("customHashtags", "#music #clipizy #ai"),
                "tag_friends": settings_data.get("tagFriends", False),
                "cross_post": settings_data.get("crossPost", False),
            })

            user.settings = db_settings
            user.updated_at = datetime.utcnow()
            db.commit()
            return True
        except Exception as e:
            logger.error(f"Error updating social settings: {str(e)}")
            db.rollback()
            return False

    def get_subscription_info(self, user: User) -> dict:
        """Get user subscription information"""
        subscription_info = {
            "tier": user.plan or "free",
            "status": "active",
            "renewsAt": None,
            "billingCycle": None,
            "price": 0,
            "currency": "USD",
        }

        # Add pricing based on tier
        if user.plan == "plus":
            subscription_info["price"] = 6
            subscription_info["billingCycle"] = "monthly"
        elif user.plan == "pro":
            subscription_info["price"] = 18
            subscription_info["billingCycle"] = "monthly"
        elif user.plan == "enterprise":
            subscription_info["price"] = 48
            subscription_info["billingCycle"] = "monthly"

        return subscription_info

    def process_avatar_upload(self, db: Session, user: User, file_content: bytes, filename: str) -> dict:
        """Process avatar upload and update user record"""
        try:
            # Generate unique filename
            file_extension = filename.split(".")[-1] if "." in filename else "jpg"
            avatar_filename = f"avatar_{uuid.uuid4().hex[:8]}.{file_extension}"
            avatar_url = f"/api/auth/avatar/{user.id}/{avatar_filename}"

            # Update database user record
            user.avatar_url = avatar_url
            user.updated_at = datetime.utcnow()
            db.commit()

            logger.info(f"Avatar uploaded successfully for user {user.id}: {avatar_filename}")

            return {
                "avatar_url": avatar_url,
                "filename": avatar_filename,
            }
        except Exception as e:
            logger.error(f"Error processing avatar upload: {str(e)}")
            db.rollback()
            raise

    def export_user_data(self, user: User) -> dict:
        """Export user data as structured dictionary"""
        return {
            "user_id": str(user.id),
            "email": user.email,
            "username": user.username,
            "bio": getattr(user, 'bio', ''),
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "last_login": user.last_login.isoformat() if user.last_login else None,
            "settings": user.settings or {},
            "exported_at": datetime.utcnow().isoformat(),
        }

    def delete_user_account(self, db: Session, user: User) -> bool:
        """Delete user account and all associated data"""
        try:
            user_id = str(user.id)
            db.delete(user)
            db.commit()
            logger.info(f"Deleted user account: {user.email}")
            return True
        except Exception as e:
            logger.error(f"Error deleting user account: {str(e)}")
            db.rollback()
            return False


# Create service instances
auth_service = AuthService()
user_creation_service = UserCreationService()
oauth_service = OAuthService()
user_management_service = UserManagementService()
