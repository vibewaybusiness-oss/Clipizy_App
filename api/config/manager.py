"""
Configuration Manager
Centralized configuration management system for the Clipizy application
Uses services and data layers for storage and database operations
"""

import json
import logging
import os
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, validator
from pydantic_settings import BaseSettings

# Import from services and data layers
from api.services.di import BaseService, ServiceConfig, get_container
from api.services.database import get_db
from api.services.storage import backend_storage_service
from api.config.settings import settings

logger = logging.getLogger(__name__)


class Environment(Enum):
    """Application environments"""
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"


class LogLevel(Enum):
    """Logging levels"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


@dataclass
class DatabaseConfig:
    """Database configuration"""
    url: str = "postgresql://postgres:postgres@localhost:5432/clipizy"
    echo: bool = False
    pool_size: int = 10
    max_overflow: int = 20
    pool_timeout: int = 30
    pool_recycle: int = 3600
    pool_pre_ping: bool = True


@dataclass
class StorageConfig:
    """Storage configuration"""
    s3_bucket: str = "clipizy"
    s3_endpoint_url: str = "http://localhost:9000"
    s3_access_key: str = "admin"
    s3_secret_key: str = "admin123"
    s3_region: str = "us-east-1"
    local_storage_path: str = "./storage"


@dataclass
class SecurityConfig:
    """Security configuration"""
    secret_key: str = "your-secret-key-here-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    password_min_length: int = 8
    max_login_attempts: int = 5
    lockout_duration_minutes: int = 15


@dataclass
class APIConfig:
    """API configuration"""
    backend_url: str = "http://localhost:8000"
    frontend_url: str = "http://localhost:3000"
    cors_origins: List[str] = field(default_factory=lambda: [
        "http://localhost:3000",
        "http://localhost:3001",
        "https://clipizy.com",
        "https://www.clipizy.com",
    ])
    max_request_size: int = 100 * 1024 * 1024  # 100MB
    request_timeout: int = 300  # 5 minutes


@dataclass
class LoggingConfig:
    """Logging configuration"""
    level: LogLevel = LogLevel.INFO
    file_max_size: int = 10 * 1024 * 1024  # 10MB
    file_backup_count: int = 5
    log_file_path: str = "./logs"
    enable_console_logging: bool = True
    enable_file_logging: bool = True
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


@dataclass
class ProducerAIConfig:
    """ProducerAI configuration"""
    urls: Dict[str, str] = field(default_factory=lambda: {
        "home": "https://www.producer.ai/",
        "create": "https://www.producer.ai/create"
    })
    prompt_selector: str = 'textarea[placeholder="Ask Producer..."]'
    page_load_timeout: int = 30000
    element_wait_timeout: int = 15000
    generation_timeout: int = 120000
    min_delay: float = 0.5
    max_delay: float = 2.0
    max_windows: int = 5
    window_creation_delay: float = 2.0
    anti_bot_delay_min: float = 1.0
    anti_bot_delay_max: float = 3.0


@dataclass
class FileProcessingConfig:
    """File processing configuration"""
    max_file_size: int = 100 * 1024 * 1024  # 100MB
    allowed_audio_formats: List[str] = field(default_factory=lambda: [".mp3", ".wav", ".flac", ".aac", ".m4a"])
    allowed_video_formats: List[str] = field(default_factory=lambda: [".mp4", ".avi", ".mov", ".mkv"])
    allowed_image_formats: List[str] = field(default_factory=lambda: [".jpg", ".jpeg", ".png", ".gif", ".webp"])
    temp_directory: str = "./temp"
    cleanup_temp_files: bool = True
    temp_file_retention_hours: int = 24


@dataclass
class PerformanceConfig:
    """Performance configuration"""
    async_operation_timeout: int = 300
    retry_attempts: int = 3
    retry_delay: float = 1.0
    max_concurrent_operations: int = 10
    memory_limit_mb: int = 1024
    cpu_limit_percent: int = 80


@dataclass
class ExternalServicesConfig:
    """External services configuration"""
    gemini_api_key: Optional[str] = None
    runpod_api_key: Optional[str] = None
    stripe_secret_key: Optional[str] = None
    stripe_publishable_key: Optional[str] = None
    stripe_webhook_secret: Optional[str] = None
    suno_api_key: Optional[str] = None
    llm_api_key: Optional[str] = None


@dataclass
class BusinessConfig:
    """Business logic configuration"""
    credits_rate: int = 20
    free_credits_on_signup: int = 100
    max_projects_per_user: int = 50
    max_tracks_per_project: int = 20
    max_videos_per_project: int = 10
    project_retention_days: int = 365
    auto_cleanup_enabled: bool = True


class ConfigurationManager(BaseService):
    """Centralized configuration manager with service integration"""
    
    def __init__(self, environment: Optional[Environment] = None):
        # Initialize as a service
        config = ServiceConfig(name="configuration_manager")
        super().__init__(config)
        
        self.environment = environment or Environment(os.getenv("ENVIRONMENT", "development"))
        self._config_cache: Dict[str, Any] = {}
        self._config_files: Dict[str, str] = {}
        self._storage_service = None
        self._db_session = None
        
        # Initialize configuration
        self._load_configuration()
    
    async def _service_health_check(self) -> Dict[str, Any]:
        """Configuration service health check"""
        try:
            # Test database connection
            if self._db_session:
                self._db_session.execute("SELECT 1")
                db_status = "connected"
            else:
                db_status = "not_initialized"
            
            # Test storage service
            if self._storage_service:
                storage_status = "available"
            else:
                storage_status = "not_initialized"
            
            return {
                "database_status": db_status,
                "storage_status": storage_status,
                "config_cache_size": len(self._config_cache),
                "config_files_loaded": len(self._config_files)
            }
        except Exception as e:
            return {
                "database_status": "error",
                "storage_status": "error", 
                "error": str(e)
            }
    
    def _load_configuration(self):
        """Load configuration from environment variables and config files"""
        
        # Initialize data layer connections
        self._initialize_data_connections()
        
        # Load from environment variables
        self.database = self._load_database_config()
        self.storage = self._load_storage_config()
        self.security = self._load_security_config()
        self.api = self._load_api_config()
        self.logging = self._load_logging_config()
        self.producer_ai = self._load_producer_ai_config()
        self.file_processing = self._load_file_processing_config()
        self.performance = self._load_performance_config()
        self.external_services = self._load_external_services_config()
        self.business = self._load_business_config()
        
        # Load from config files if they exist
        self._load_config_files()
        
        # Load from database if available
        self._load_database_config_from_db()
        
        logger.info(f"Configuration loaded for environment: {self.environment.value}")
    
    def _initialize_data_connections(self):
        """Initialize connections to data layer services"""
        try:
            # Get database session
            self._db_session = get_db()
            
            # Get storage service
            self._storage_service = backend_storage_service
            
            logger.info("Data layer connections initialized")
        except Exception as e:
            logger.warning(f"Could not initialize data layer connections: {e}")
    
    def _load_database_config_from_db(self):
        """Load configuration from database if available"""
        if not self._db_session:
            return
        
        try:
            # This would load configuration from a database table
            # For now, we'll just log that it's available
            logger.info("Database configuration loading available")
        except Exception as e:
            logger.warning(f"Could not load database configuration: {e}")
    
    def _load_database_config(self) -> DatabaseConfig:
        """Load database configuration"""
        return DatabaseConfig(
            url=os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/clipizy"),
            echo=os.getenv("DATABASE_ECHO", "false").lower() == "true",
            pool_size=int(os.getenv("DB_POOL_SIZE", "10")),
            max_overflow=int(os.getenv("DB_MAX_OVERFLOW", "20")),
            pool_timeout=int(os.getenv("DB_POOL_TIMEOUT", "30")),
            pool_recycle=int(os.getenv("DB_POOL_RECYCLE", "3600")),
            pool_pre_ping=os.getenv("DB_POOL_PRE_PING", "true").lower() == "true"
        )
    
    def _load_storage_config(self) -> StorageConfig:
        """Load storage configuration"""
        return StorageConfig(
            s3_bucket=os.getenv("S3_BUCKET", "clipizy-dev"),
            s3_endpoint_url=os.getenv("S3_ENDPOINT_URL", "https://s3.amazonaws.com"),
            s3_access_key=os.getenv("S3_ACCESS_KEY"),
            s3_secret_key=os.getenv("S3_SECRET_KEY"),
            s3_region=os.getenv("S3_REGION", "us-east-1"),
            local_storage_path=os.getenv("LOCAL_STORAGE_PATH", "./storage")
        )
    
    def _load_security_config(self) -> SecurityConfig:
        """Load security configuration"""
        return SecurityConfig(
            secret_key=os.getenv("SECRET_KEY", "your-secret-key-here-change-in-production"),
            algorithm=os.getenv("JWT_ALGORITHM", "HS256"),
            access_token_expire_minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")),
            refresh_token_expire_days=int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7")),
            password_min_length=int(os.getenv("PASSWORD_MIN_LENGTH", "8")),
            max_login_attempts=int(os.getenv("MAX_LOGIN_ATTEMPTS", "5")),
            lockout_duration_minutes=int(os.getenv("LOCKOUT_DURATION_MINUTES", "15"))
        )
    
    def _load_api_config(self) -> APIConfig:
        """Load API configuration"""
        cors_origins = os.getenv("CORS_ORIGINS", "").split(",") if os.getenv("CORS_ORIGINS") else [
            "http://localhost:3000",
            "http://localhost:3001",
            "https://clipizy.com",
            "https://www.clipizy.com",
        ]
        
        return APIConfig(
            backend_url=os.getenv("BACKEND_URL", "http://localhost:8000"),
            frontend_url=os.getenv("FRONTEND_URL", "http://localhost:3000"),
            cors_origins=cors_origins,
            max_request_size=int(os.getenv("MAX_REQUEST_SIZE", str(100 * 1024 * 1024))),
            request_timeout=int(os.getenv("REQUEST_TIMEOUT", "300"))
        )
    
    def _load_logging_config(self) -> LoggingConfig:
        """Load logging configuration"""
        return LoggingConfig(
            level=LogLevel(os.getenv("LOG_LEVEL", "INFO")),
            file_max_size=int(os.getenv("LOG_FILE_MAX_SIZE", str(10 * 1024 * 1024))),
            file_backup_count=int(os.getenv("LOG_FILE_BACKUP_COUNT", "5")),
            log_file_path=os.getenv("LOG_FILE_PATH", "./logs"),
            enable_console_logging=os.getenv("ENABLE_CONSOLE_LOGGING", "true").lower() == "true",
            enable_file_logging=os.getenv("ENABLE_FILE_LOGGING", "true").lower() == "true",
            log_format=os.getenv("LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        )
    
    def _load_producer_ai_config(self) -> ProducerAIConfig:
        """Load ProducerAI configuration"""
        return ProducerAIConfig(
            page_load_timeout=int(os.getenv("PRODUCER_AI_PAGE_LOAD_TIMEOUT", "30000")),
            element_wait_timeout=int(os.getenv("PRODUCER_AI_ELEMENT_WAIT_TIMEOUT", "15000")),
            generation_timeout=int(os.getenv("PRODUCER_AI_GENERATION_TIMEOUT", "120000")),
            min_delay=float(os.getenv("PRODUCER_AI_MIN_DELAY", "0.5")),
            max_delay=float(os.getenv("PRODUCER_AI_MAX_DELAY", "2.0")),
            max_windows=int(os.getenv("PRODUCER_AI_MAX_WINDOWS", "5")),
            window_creation_delay=float(os.getenv("PRODUCER_AI_WINDOW_CREATION_DELAY", "2.0")),
            anti_bot_delay_min=float(os.getenv("PRODUCER_AI_ANTI_BOT_DELAY_MIN", "1.0")),
            anti_bot_delay_max=float(os.getenv("PRODUCER_AI_ANTI_BOT_DELAY_MAX", "3.0"))
        )
    
    def _load_file_processing_config(self) -> FileProcessingConfig:
        """Load file processing configuration"""
        return FileProcessingConfig(
            max_file_size=int(os.getenv("MAX_FILE_SIZE", str(100 * 1024 * 1024))),
            allowed_audio_formats=os.getenv("ALLOWED_AUDIO_FORMATS", ".mp3,.wav,.flac,.aac,.m4a").split(","),
            allowed_video_formats=os.getenv("ALLOWED_VIDEO_FORMATS", ".mp4,.avi,.mov,.mkv").split(","),
            allowed_image_formats=os.getenv("ALLOWED_IMAGE_FORMATS", ".jpg,.jpeg,.png,.gif,.webp").split(","),
            temp_directory=os.getenv("TEMP_DIRECTORY", "./temp"),
            cleanup_temp_files=os.getenv("CLEANUP_TEMP_FILES", "true").lower() == "true",
            temp_file_retention_hours=int(os.getenv("TEMP_FILE_RETENTION_HOURS", "24"))
        )
    
    def _load_performance_config(self) -> PerformanceConfig:
        """Load performance configuration"""
        return PerformanceConfig(
            async_operation_timeout=int(os.getenv("ASYNC_OPERATION_TIMEOUT", "300")),
            retry_attempts=int(os.getenv("RETRY_ATTEMPTS", "3")),
            retry_delay=float(os.getenv("RETRY_DELAY", "1.0")),
            max_concurrent_operations=int(os.getenv("MAX_CONCURRENT_OPERATIONS", "10")),
            memory_limit_mb=int(os.getenv("MEMORY_LIMIT_MB", "1024")),
            cpu_limit_percent=int(os.getenv("CPU_LIMIT_PERCENT", "80"))
        )
    
    def _load_external_services_config(self) -> ExternalServicesConfig:
        """Load external services configuration"""
        return ExternalServicesConfig(
            gemini_api_key=os.getenv("GEMINI_API_KEY"),
            runpod_api_key=os.getenv("RUNPOD_API_KEY"),
            stripe_secret_key=os.getenv("STRIPE_SECRET_KEY"),
            stripe_publishable_key=os.getenv("STRIPE_PUBLISHABLE_KEY"),
            stripe_webhook_secret=os.getenv("STRIPE_WEBHOOK_SECRET"),
            suno_api_key=os.getenv("SUNO_API_KEY"),
            llm_api_key=os.getenv("LLM_API_KEY")
        )
    
    def _load_business_config(self) -> BusinessConfig:
        """Load business configuration"""
        return BusinessConfig(
            credits_rate=int(os.getenv("CREDITS_RATE", "20")),
            free_credits_on_signup=int(os.getenv("FREE_CREDITS_ON_SIGNUP", "100")),
            max_projects_per_user=int(os.getenv("MAX_PROJECTS_PER_USER", "50")),
            max_tracks_per_project=int(os.getenv("MAX_TRACKS_PER_PROJECT", "20")),
            max_videos_per_project=int(os.getenv("MAX_VIDEOS_PER_PROJECT", "10")),
            project_retention_days=int(os.getenv("PROJECT_RETENTION_DAYS", "365")),
            auto_cleanup_enabled=os.getenv("AUTO_CLEANUP_ENABLED", "true").lower() == "true"
        )
    
    def _load_config_files(self):
        """Load configuration from JSON files"""
        config_dir = Path("./api/config/json")
        
        # Load environment-specific config files
        env_config_file = config_dir / f"{self.environment.value}.json"
        if env_config_file.exists():
            self._load_config_file(env_config_file, f"{self.environment.value}_config")
        
        # Load general config files
        general_config_files = [
            "database.json",
            "storage.json",
            "security.json",
            "api.json",
            "logging.json",
            "producer_ai.json",
            "file_processing.json",
            "performance.json",
            "external_services.json",
            "business.json"
        ]
        
        for config_file in general_config_files:
            file_path = config_dir / config_file
            if file_path.exists():
                self._load_config_file(file_path, config_file.replace(".json", ""))
    
    def _load_config_file(self, file_path: Path, config_name: str):
        """Load configuration from a JSON file"""
        try:
            with open(file_path, 'r') as f:
                config_data = json.load(f)
            
            self._config_files[config_name] = str(file_path)
            self._merge_config(config_data)
            
            logger.info(f"Loaded configuration from {file_path}")
            
        except Exception as e:
            logger.warning(f"Failed to load config file {file_path}: {e}")
    
    def _merge_config(self, config_data: Dict[str, Any]):
        """Merge configuration data into existing config"""
        # This would merge the JSON config data into the appropriate config objects
        # Implementation depends on the structure of the JSON files
        pass
    
    def get_config(self, config_type: str) -> Any:
        """Get configuration by type"""
        config_map = {
            "database": self.database,
            "storage": self.storage,
            "security": self.security,
            "api": self.api,
            "logging": self.logging,
            "producer_ai": self.producer_ai,
            "file_processing": self.file_processing,
            "performance": self.performance,
            "external_services": self.external_services,
            "business": self.business
        }
        
        return config_map.get(config_type)
    
    def get_value(self, config_path: str, default: Any = None) -> Any:
        """Get a specific configuration value using dot notation"""
        parts = config_path.split(".")
        if len(parts) < 2:
            return default
        
        config_type = parts[0]
        config_obj = self.get_config(config_type)
        
        if not config_obj:
            return default
        
        # Navigate through the config object
        current = config_obj
        for part in parts[1:]:
            if hasattr(current, part):
                current = getattr(current, part)
            else:
                return default
        
        return current
    
    def set_value(self, config_path: str, value: Any):
        """Set a specific configuration value using dot notation"""
        parts = config_path.split(".")
        if len(parts) < 2:
            return
        
        config_type = parts[0]
        config_obj = self.get_config(config_type)
        
        if not config_obj:
            return
        
        # Navigate to the parent object
        current = config_obj
        for part in parts[1:-1]:
            if hasattr(current, part):
                current = getattr(current, part)
            else:
                return
        
        # Set the value
        if hasattr(current, parts[-1]):
            setattr(current, parts[-1], value)
    
    def validate_configuration(self) -> List[str]:
        """Validate the current configuration"""
        issues = []
        
        # Validate database configuration
        if not self.database.url:
            issues.append("Database URL is required")
        
        # Validate security configuration
        if self.security.secret_key == "your-secret-key-here-change-in-production":
            issues.append("Default secret key detected - change in production")
        
        # Validate external services
        if self.environment == Environment.PRODUCTION:
            if not self.external_services.stripe_secret_key:
                issues.append("Stripe secret key is required in production")
        
        # Validate file processing
        if self.file_processing.max_file_size <= 0:
            issues.append("Max file size must be positive")
        
        return issues
    
    def get_configuration_summary(self) -> Dict[str, Any]:
        """Get a summary of the current configuration"""
        return {
            "environment": self.environment.value,
            "database": {
                "url": self.database.url.split("@")[-1] if "@" in self.database.url else "hidden",
                "pool_size": self.database.pool_size,
                "echo": self.database.echo
            },
            "storage": {
                "s3_bucket": self.storage.s3_bucket,
                "s3_endpoint": self.storage.s3_endpoint_url,
                "local_path": self.storage.local_storage_path
            },
            "security": {
                "algorithm": self.security.algorithm,
                "token_expire_minutes": self.security.access_token_expire_minutes,
                "secret_key_set": self.security.secret_key != "your-secret-key-here-change-in-production"
            },
            "api": {
                "backend_url": self.api.backend_url,
                "frontend_url": self.api.frontend_url,
                "cors_origins_count": len(self.api.cors_origins)
            },
            "logging": {
                "level": self.logging.level.value,
                "file_logging": self.logging.enable_file_logging,
                "console_logging": self.logging.enable_console_logging
            },
            "producer_ai": {
                "page_load_timeout": self.producer_ai.page_load_timeout,
                "generation_timeout": self.producer_ai.generation_timeout,
                "max_windows": self.producer_ai.max_windows
            },
            "file_processing": {
                "max_file_size_mb": self.file_processing.max_file_size // (1024 * 1024),
                "allowed_audio_formats": self.file_processing.allowed_audio_formats,
                "temp_directory": self.file_processing.temp_directory
            },
            "performance": {
                "async_timeout": self.performance.async_operation_timeout,
                "retry_attempts": self.performance.retry_attempts,
                "max_concurrent": self.performance.max_concurrent_operations
            },
            "business": {
                "credits_rate": self.business.credits_rate,
                "free_credits": self.business.free_credits_on_signup,
                "max_projects": self.business.max_projects_per_user
            },
            "config_files_loaded": list(self._config_files.keys())
        }
    
    def reload_configuration(self):
        """Reload configuration from environment variables and files"""
        self._config_cache.clear()
        self._config_files.clear()
        self._load_configuration()
        logger.info("Configuration reloaded")
    
    def export_configuration(self, file_path: str):
        """Export current configuration to a JSON file"""
        config_data = {
            "environment": self.environment.value,
            "database": self._dataclass_to_dict(self.database),
            "storage": self._dataclass_to_dict(self.storage),
            "security": self._dataclass_to_dict(self.security),
            "api": self._dataclass_to_dict(self.api),
            "logging": self._dataclass_to_dict(self.logging),
            "producer_ai": self._dataclass_to_dict(self.producer_ai),
            "file_processing": self._dataclass_to_dict(self.file_processing),
            "performance": self._dataclass_to_dict(self.performance),
            "external_services": self._dataclass_to_dict(self.external_services),
            "business": self._dataclass_to_dict(self.business)
        }
        
        with open(file_path, 'w') as f:
            json.dump(config_data, f, indent=2, default=str)
        
        logger.info(f"Configuration exported to {file_path}")
    
    def _dataclass_to_dict(self, obj) -> Dict[str, Any]:
        """Convert dataclass to dictionary"""
        if hasattr(obj, '__dict__'):
            return {k: v for k, v in obj.__dict__.items() if not k.startswith('_')}
        return obj


# Global configuration manager instance
_config_manager: Optional[ConfigurationManager] = None


def get_config_manager() -> ConfigurationManager:
    """Get the global configuration manager"""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigurationManager()
    return _config_manager


def get_config(config_type: str) -> Any:
    """Get configuration by type"""
    return get_config_manager().get_config(config_type)


def get_config_value(config_path: str, default: Any = None) -> Any:
    """Get a specific configuration value"""
    return get_config_manager().get_value(config_path, default)


def set_config_value(config_path: str, value: Any):
    """Set a specific configuration value"""
    get_config_manager().set_value(config_path, value)


def validate_configuration() -> List[str]:
    """Validate the current configuration"""
    return get_config_manager().validate_configuration()


def get_configuration_summary() -> Dict[str, Any]:
    """Get configuration summary"""
    return get_config_manager().get_configuration_summary()


def reload_configuration():
    """Reload configuration"""
    get_config_manager().reload_configuration()
