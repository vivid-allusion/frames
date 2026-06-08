"""Custom exceptions for fail-fast error handling."""


class AuthenticationError(Exception):
    """Raised when authentication with 1Password fails."""

    pass


class ConfigurationError(Exception):
    """Raised when configuration is invalid or missing."""

    pass


class ValidationError(Exception):
    """Raised when input validation fails."""

    pass
