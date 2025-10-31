"""
Router Factory
Creates routers with consistent configuration and structure
"""

import logging
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse

from .architecture import RouterConfig, RouterCategory, RouterPriority, get_router_architecture
from .base_router import (
    BaseRouter, AuthRouter, AdminRouter, BusinessRouter, 
    MediaRouter, AIRouter, create_standard_response
)

logger = logging.getLogger(__name__)


class RouterFactory:
    """Factory for creating consistent routers"""
    
    def __init__(self):
        self.architecture = get_router_architecture()
    
    def create_router(
        self,
        name: str,
        prefix: str,
        tags: List[str],
        category: RouterCategory = RouterCategory.SYSTEM,
        priority: RouterPriority = RouterPriority.MEDIUM,
        requires_auth: bool = True,
        requires_admin: bool = False,
        description: Optional[str] = None,
        version: str = "1.0.0",
        enable_caching: bool = False,
        cache_expiration: int = 300
    ) -> BaseRouter:
        """
        Create a router with consistent configuration
        
        Args:
            name: Router name
            prefix: URL prefix
            tags: OpenAPI tags
            category: Router category
            priority: Router priority
            requires_auth: Whether router requires authentication
            requires_admin: Whether router requires admin access
            description: Router description
            version: Router version
            
        Returns:
            Configured APIRouter instance
        """
        # If prefix is empty, use architecture configuration
        if prefix == "":
            arch_config = self.architecture.get_router_config(name)
            if arch_config:
                prefix = arch_config.prefix
                category = arch_config.category
                priority = arch_config.priority
                requires_auth = arch_config.requires_auth
                requires_admin = arch_config.requires_admin
                if not description:
                    description = arch_config.description
        
        # Create router configuration
        config = RouterConfig(
            name=name,
            category=category,
            priority=priority,
            prefix=prefix,
            tags=tags,
            requires_auth=requires_auth,
            requires_admin=requires_admin,
            description=description,
            version=version
        )
        
        # Validate configuration
        issues = self.architecture.validate_router_config(config)
        if issues:
            logger.warning(f"Router '{name}' configuration issues: {issues}")
        
        # Create appropriate router type based on category
        if category == RouterCategory.AUTH:
            router = AuthRouter(prefix=prefix, tags=tags)
        elif category == RouterCategory.ADMIN:
            router = AdminRouter(prefix=prefix, tags=tags)
        elif category == RouterCategory.BUSINESS:
            router = BusinessRouter(prefix=prefix, tags=tags)
        elif category == RouterCategory.MEDIA:
            router = MediaRouter(prefix=prefix, tags=tags)
        elif category == RouterCategory.AI:
            router = AIRouter(prefix=prefix, tags=tags)
        else:
            router = BaseRouter(
                prefix=prefix,
                tags=tags,
                requires_auth=requires_auth,
                requires_admin=requires_admin,
                enable_caching=enable_caching,
                cache_expiration=cache_expiration
            )
        
        logger.info(f"Created {category.value} router '{name}' with prefix '{prefix}'")
        return router
    
    def create_auth_router(self, name: str, prefix: str, tags: List[str]) -> AuthRouter:
        """Create authentication router"""
        return self.create_router(
            name=name,
            prefix=prefix,
            tags=tags,
            category=RouterCategory.AUTH,
            priority=RouterPriority.HIGH,
            requires_auth=False,
            description="Authentication and authorization endpoints"
        )
    
    def create_business_router(self, name: str, prefix: str, tags: List[str]) -> BusinessRouter:
        """Create business logic router"""
        return self.create_router(
            name=name,
            prefix=prefix,
            tags=tags,
            category=RouterCategory.BUSINESS,
            priority=RouterPriority.HIGH,
            requires_auth=True,
            description="Business logic and core functionality"
        )
    
    def create_media_router(self, name: str, prefix: str, tags: List[str]) -> MediaRouter:
        """Create media processing router"""
        return self.create_router(
            name=name,
            prefix=prefix,
            tags=tags,
            category=RouterCategory.MEDIA,
            priority=RouterPriority.HIGH,
            requires_auth=True,
            description="Media processing and management"
        )
    
    def create_ai_router(self, name: str, prefix: str, tags: List[str]) -> AIRouter:
        """Create AI service router"""
        return self.create_router(
            name=name,
            prefix=prefix,
            tags=tags,
            category=RouterCategory.AI,
            priority=RouterPriority.MEDIUM,
            requires_auth=True,
            description="AI service integration and management"
        )
    
    def create_admin_router(self, name: str, prefix: str, tags: List[str]) -> AdminRouter:
        """Create admin router"""
        return self.create_router(
            name=name,
            prefix=prefix,
            tags=tags,
            category=RouterCategory.ADMIN,
            priority=RouterPriority.LOW,
            requires_auth=True,
            requires_admin=True,
            description="Administrative functions and management"
        )
    
    def create_analytics_router(self, name: str, prefix: str, tags: List[str]) -> APIRouter:
        """Create analytics router"""
        return self.create_router(
            name=name,
            prefix=prefix,
            tags=tags,
            category=RouterCategory.ANALYTICS,
            priority=RouterPriority.MEDIUM,
            requires_auth=True,
            description="Analytics and reporting"
        )
    
    def create_content_router(self, name: str, prefix: str, tags: List[str]) -> APIRouter:
        """Create content generation router"""
        return self.create_router(
            name=name,
            prefix=prefix,
            tags=tags,
            category=RouterCategory.CONTENT,
            priority=RouterPriority.MEDIUM,
            requires_auth=True,
            description="Content generation and management"
        )
    
    def create_social_router(self, name: str, prefix: str, tags: List[str]) -> APIRouter:
        """Create social media router"""
        return self.create_router(
            name=name,
            prefix=prefix,
            tags=tags,
            category=RouterCategory.SOCIAL,
            priority=RouterPriority.MEDIUM,
            requires_auth=True,
            description="Social media integration and automation"
        )
    
    def create_system_router(self, name: str, prefix: str, tags: List[str]) -> APIRouter:
        """Create system router"""
        return self.create_router(
            name=name,
            prefix=prefix,
            tags=tags,
            category=RouterCategory.SYSTEM,
            priority=RouterPriority.SYSTEM,
            requires_auth=True,
            description="System operations and workflows"
        )
    
    # Note: Error handling and health checks are now handled by BaseRouter


# Global router factory instance
router_factory = RouterFactory()


def get_router_factory() -> RouterFactory:
    """Get the global router factory instance"""
    return router_factory


def create_router(
    name: str,
    prefix: str,
    tags: List[str],
    category: RouterCategory = RouterCategory.SYSTEM,
    priority: RouterPriority = RouterPriority.MEDIUM,
    requires_auth: bool = True,
    requires_admin: bool = False,
    description: Optional[str] = None,
    enable_caching: bool = False,
    cache_expiration: int = 300
) -> BaseRouter:
    """Create a router using the global factory"""
    return router_factory.create_router(
        name=name,
        prefix=prefix,
        tags=tags,
        category=category,
        priority=priority,
        requires_auth=requires_auth,
        requires_admin=requires_admin,
        description=description,
        enable_caching=enable_caching,
        cache_expiration=cache_expiration
    )


def create_auth_router(name: str, prefix: str, tags: List[str]) -> AuthRouter:
    """Create authentication router"""
    return router_factory.create_auth_router(name, prefix, tags)


def create_business_router(name: str, prefix: str, tags: List[str]) -> BusinessRouter:
    """Create business logic router"""
    return router_factory.create_business_router(name, prefix, tags)


def create_media_router(name: str, prefix: str, tags: List[str]) -> MediaRouter:
    """Create media processing router"""
    return router_factory.create_media_router(name, prefix, tags)


def create_ai_router(name: str, prefix: str, tags: List[str]) -> AIRouter:
    """Create AI service router"""
    return router_factory.create_ai_router(name, prefix, tags)


def create_admin_router(name: str, prefix: str, tags: List[str]) -> AdminRouter:
    """Create admin router"""
    return router_factory.create_admin_router(name, prefix, tags)


def create_analytics_router(name: str, prefix: str, tags: List[str]) -> BaseRouter:
    """Create analytics router"""
    return router_factory.create_analytics_router(name, prefix, tags)


def create_content_router(name: str, prefix: str, tags: List[str]) -> BaseRouter:
    """Create content generation router"""
    return router_factory.create_content_router(name, prefix, tags)


def create_social_router(name: str, prefix: str, tags: List[str]) -> BaseRouter:
    """Create social media router"""
    return router_factory.create_social_router(name, prefix, tags)


def create_system_router(name: str, prefix: str, tags: List[str]) -> BaseRouter:
    """Create system router"""
    return router_factory.create_system_router(name, prefix, tags)
