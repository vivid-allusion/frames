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


class RecoverableAPIError(Exception):
    """Raised for model-level errors where retrying with next prompt may succeed.

    Examples: content policy rejection, NSFW filter, prompt format errors.
    Script should generate an error image and continue.
    """

    pass


class FatalAPIError(Exception):
    """Raised for infrastructure errors where retrying is pointless.

    Examples: authentication failure, network unreachable, rate limit exhausted.
    Script should stop immediately.
    """

    pass
