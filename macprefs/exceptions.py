from __future__ import annotations


class PropertyListConversionError(Exception):
    """Exception raised when a property list conversion fails."""
    def __init__(self, filename: str | None = None) -> None:
        super().__init__(f'Property list {filename} failed to convert'
                         if filename else 'Property list conversion failed')


class ConfigTypeError(RuntimeError):
    """Configuration error."""
    def __init__(self, key: str, expected_type: str) -> None:
        super().__init__(f'Config key {key} must be of type {expected_type}.')
