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


class MarkdownImageNotFoundError(ValueError):
    """Raised when no image URL found in markdown file."""

    pass


class MarkdownPromptNotFoundError(ValueError):
    """Raised when no code block found in markdown file."""

    pass


class EmptyPromptError(ValueError):
    """Raised when code block in markdown is empty."""

    pass
