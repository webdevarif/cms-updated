"""
Service registry for centralized service management.
"""
from typing import Any, Dict, Type


class ServiceRegistry:
    """Registry for managing centralized services"""

    _services: Dict[str, Dict[str, Any]] = {}

    @classmethod
    def register_service(cls, module_name: str, service_name: str, service_class: Type[Any]):
        """Register a service"""
        if module_name not in cls._services:
            cls._services[module_name] = {}

        cls._services[module_name][service_name] = service_class

    @classmethod
    def get_service(cls, module_name: str, service_name: str) -> Type[Any]:
        """Get a registered service"""
        if module_name not in cls._services:
            raise ValueError(f"Module '{module_name}' not registered")

        if service_name not in cls._services[module_name]:
            raise ValueError(f"Service '{service_name}' not found in module '{module_name}'")

        return cls._services[module_name][service_name]

    @classmethod
    def get_module_services(cls, module_name: str) -> Dict[str, Type[Any]]:
        """Get all services for a module"""
        return cls._services.get(module_name, {})

    @classmethod
    def list_services(cls) -> Dict[str, Dict[str, Type[Any]]]:
        """List all registered services"""
        return cls._services.copy()

    @classmethod
    def unregister_service(cls, module_name: str, service_name: str):
        """Unregister a service"""
        if module_name in cls._services and service_name in cls._services[module_name]:
            del cls._services[module_name][service_name]

            # Clean up empty modules
            if not cls._services[module_name]:
                del cls._services[module_name]
