"""Custom exceptions for fail-fast error handling."""


class AuthenticationError(Exception):
    """Raised when authentication fails."""

    pass


class ConfigurationError(Exception):
    """Raised when configuration is invalid or missing."""

    pass


class ValidationError(Exception):
    """Raised when input validation fails."""

    pass
