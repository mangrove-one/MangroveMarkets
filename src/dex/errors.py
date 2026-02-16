"""DEX domain-specific errors."""


class DexError(Exception):
    """Base error for DEX operations."""

    def __init__(self, code: str, message: str, suggestion: str = ""):
        super().__init__(message)
        self.code = code
        self.message = message
        self.suggestion = suggestion


class VenueNotSupportedError(DexError):
    """Raised when a venue is present but does not support an operation."""

    def __init__(self, message: str = "Venue does not yet support this operation"):
        super().__init__("VENUE_NOT_SUPPORTED", message, "Try another venue or check back later")


class VenueNotFoundError(DexError):
    """Raised when a venue id is unknown."""

    def __init__(self, venue_id: str):
        super().__init__("VENUE_NOT_FOUND", f"Unknown venue_id '{venue_id}'", "Use dex_supported_venues to list options")


class NoQuotesAvailableError(DexError):
    """Raised when no quotes can be produced for a request."""

    def __init__(self, input_token: str, output_token: str):
        super().__init__(
            "NO_QUOTES_AVAILABLE",
            f"No quotes available for {input_token}->{output_token}",
            "Try a different pair or specify a venue",
        )
