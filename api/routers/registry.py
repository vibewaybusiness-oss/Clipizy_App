"""
Router Registry System
Manages router registration and organization
"""

import logging
from typing import Dict, List, Optional, Type, Any
from fastapi import APIRouter, FastAPI

from .architecture import RouterConfig, RouterCategory, RouterPriority, get_router_architecture
from .base_router import BaseRouter

logger = logging.getLogger(__name__)


class RouterRegistry:
    """Registry for managing router registration"""
    
    def __init__(self):
        self.registered_routers: Dict[str, APIRouter] = {}
        self.registered_base_routers: Dict[str, BaseRouter] = {}
        self.router_configs: Dict[str, RouterConfig] = {}
        self.architecture = get_router_architecture()
    
    def register_router(self, name: str, router: APIRouter, config: Optional[RouterConfig] = None) -> None:
        """
        Register a router with the registry
        
        Args:
            name: Router name
            router: FastAPI router instance
            config: Router configuration (optional, will use default if not provided)
        """
        if config is None:
            config = self.architecture.get_router_config(name)
            if config is None:
                logger.warning(f"No configuration found for router '{name}', using default")
                config = RouterConfig(
                    name=name,
                    category=RouterCategory.SYSTEM,
                    priority=RouterPriority.LOW,
                    prefix=f"/api/{name}",
                    tags=[name.title()],
                )
        
        self.registered_routers[name] = router
        self.router_configs[name] = config
        
        logger.info(f"Registered router '{name}' with prefix '{config.prefix}'")
    
    def register_base_router(self, name: str, base_router: BaseRouter, config: Optional[RouterConfig] = None) -> None:
        """
        Register a base router with the registry
        
        Args:
            name: Router name
            base_router: BaseRouter instance
            config: Router configuration (optional, will use default if not provided)
        """
        if config is None:
            config = RouterConfig(
                name=name,
                category=RouterCategory.SYSTEM,
                priority=RouterPriority.LOW,
                prefix=base_router.prefix,
                tags=base_router.tags,
            )
        
        self.registered_base_routers[name] = base_router
        self.registered_routers[name] = base_router.router
        self.router_configs[name] = config
        
        logger.info(f"Registered base router '{name}' with prefix '{config.prefix}'")
    
    def get_router(self, name: str) -> Optional[APIRouter]:
        """Get registered router by name"""
        return self.registered_routers.get(name)
    
    def get_base_router(self, name: str) -> Optional[BaseRouter]:
        """Get registered base router by name"""
        return self.registered_base_routers.get(name)
    
    def get_router_config(self, name: str) -> Optional[RouterConfig]:
        """Get router configuration by name"""
        return self.router_configs.get(name)
    
    def get_routers_by_category(self, category: RouterCategory) -> Dict[str, APIRouter]:
        """Get all routers in a category"""
        return {
            name: router for name, router in self.registered_routers.items()
            if self.router_configs.get(name, {}).category == category
        }
    
    def get_routers_by_priority(self, priority: RouterPriority) -> Dict[str, APIRouter]:
        """Get all routers with a specific priority"""
        return {
            name: router for name, router in self.registered_routers.items()
            if self.router_configs.get(name, {}).priority == priority
        }
    
    def get_registration_order(self) -> List[tuple[str, APIRouter, RouterConfig]]:
        """Get routers in registration order (by priority)"""
        sorted_routers = sorted(
            self.router_configs.items(),
            key=lambda x: x[1].priority.value
        )
        
        return [
            (name, self.registered_routers[name], config)
            for name, config in sorted_routers
            if name in self.registered_routers
        ]
    
    def register_all_routers_with_app(self, app: FastAPI) -> None:
        """Register all routers with the FastAPI app in proper order"""
        registration_order = self.get_registration_order()
        
        for name, router, config in registration_order:
            try:
                # Check if router already has a prefix set
                router_prefix = getattr(router, 'prefix', None)
                if router_prefix and router_prefix != "":
                    # Router already has a prefix, don't override it
                    app.include_router(router, tags=config.tags)
                    logger.info(f"Registered router '{name}' with existing prefix '{router_prefix}'")
                else:
                    # Router doesn't have a prefix, use the config prefix
                    app.include_router(
                        router,
                        prefix=config.prefix if config.prefix else "",
                        tags=config.tags
                    )
                    logger.info(f"Registered router '{name}' with prefix '{config.prefix}'")
            except Exception as e:
                logger.error(f"Failed to register router '{name}': {e}")
    
    def validate_registry(self) -> Dict[str, List[str]]:
        """Validate all registered routers"""
        issues = {}
        
        for name, config in self.router_configs.items():
            if name not in self.registered_routers:
                issues[name] = ["Router not registered but has configuration"]
                continue
            
            # Validate configuration
            config_issues = self.architecture.validate_router_config(config)
            if config_issues:
                issues[name] = config_issues
        
        # Check for unregistered routers
        for name in self.registered_routers:
            if name not in self.router_configs:
                if name not in issues:
                    issues[name] = []
                issues[name].append("Router registered but has no configuration")
        
        return issues
    
    def get_registry_summary(self) -> Dict[str, Any]:
        """Get summary of registered routers"""
        return {
            "total_registered": len(self.registered_routers),
            "total_configs": len(self.router_configs),
            "categories": {
                category.value: len(self.get_routers_by_category(category))
                for category in RouterCategory
            },
            "priorities": {
                priority.name: len(self.get_routers_by_priority(priority))
                for priority in RouterPriority
            },
            "routers": {
                name: {
                    "prefix": config.prefix,
                    "tags": config.tags,
                    "category": config.category.value,
                    "priority": config.priority.name,
                    "requires_auth": config.requires_auth,
                    "requires_admin": config.requires_admin,
                }
                for name, config in self.router_configs.items()
            }
        }


# Global router registry instance
router_registry = RouterRegistry()


def get_router_registry() -> RouterRegistry:
    """Get the global router registry instance"""
    return router_registry


def register_router(name: str, router: APIRouter, config: Optional[RouterConfig] = None) -> None:
    """Register a router with the global registry"""
    router_registry.register_router(name, router, config)


def get_router(name: str) -> Optional[APIRouter]:
    """Get registered router by name"""
    return router_registry.get_router(name)


def register_all_routers_with_app(app: FastAPI) -> None:
    """Register all routers with the FastAPI app"""
    router_registry.register_all_routers_with_app(app)


def validate_router_registry() -> Dict[str, List[str]]:
    """Validate all registered routers"""
    return router_registry.validate_registry()


def get_router_registry_summary() -> Dict[str, Any]:
    """Get summary of registered routers"""
    return router_registry.get_registry_summary()
