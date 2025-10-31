# Unified Authentication Service

## Overview

All authentication functionality has been consolidated into a single file: `auth.py`

## Structure

### Single File: `auth.py` (650+ lines)

Contains all authentication functionality:

1. **Utility Functions**
   - `generate_email_based_uuid()` - Email-based UUID generation
   - `create_user_storage_structure()` - Storage setup

2. **AuthService Class**
   - Password hashing/verification
   - JWT token creation/verification
   - User authentication
   - Basic user management

3. **UserCreationService Class**
   - Complete user profile creation
   - Initial credits setup
   - User settings initialization
   - Storage structure creation

4. **OAuthService Class**
   - Google/GitHub OAuth integration
   - OAuth user creation/management

5. **AuthDependencies Class**
   - FastAPI dependency functions
   - User authentication middleware
   - Admin user validation

6. **Convenience Functions**
   - `get_current_user()` - Full user validation
   - `get_current_user_simple()` - Token-only validation
   - `get_admin_user()` - Admin user validation

## Usage

### Import Everything from One Place
```python
from api.services.auth import (
    auth_service,
    user_creation_service,
    oauth_service,
    get_current_user,
    get_admin_user,
    generate_email_based_uuid
)
```

### User Creation
```python
# Create email user
user = user_creation_service.create_complete_user_profile(
    db=db,
    email="user@example.com",
    name="John Doe",
    password="password123",
    oauth_provider=None
)

# Create OAuth user
user = oauth_service.get_or_create_user(db, oauth_user_info)
```

### Authentication Dependencies
```python
# In FastAPI routes
@router.get("/protected")
async def protected_route(current_user: User = Depends(get_current_user)):
    return {"user": current_user.email}

@router.get("/admin")
async def admin_route(admin_user: User = Depends(get_admin_user)):
    return {"admin": admin_user.email}
```

### OAuth
```python
# Get OAuth user info
user_info = await oauth_service.get_google_user_info(code)
user = oauth_service.get_or_create_user(db, user_info)
```

## Benefits

1. **Single Source of Truth** - All auth logic in one file
2. **No Import Confusion** - Everything comes from one place
3. **Easier Maintenance** - All related code is together
4. **Better Performance** - No circular imports or complex dependencies
5. **Simplified Testing** - Test one file instead of multiple
6. **Clear Architecture** - Easy to understand the complete auth flow

## File Structure

```
api/services/auth/
├── auth.py          # Complete authentication system (650+ lines)
├── __init__.py      # Clean exports (30 lines)
└── README.md        # This file
```

## Migration Complete

All authentication functionality is now in a single, unified file. The system is clean, efficient, and maintainable.
