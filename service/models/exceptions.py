class InternalServerException(Exception):
    """Raised when an unexpected error occurs in the server"""
    pass


class OrderNotFoundException(Exception):
    """Raised when trying to access an order that doesn't exist"""
    pass


class DynamicConfigurationException(Exception):
    """Raised when AppConfig fails to return configuration data"""
    pass
