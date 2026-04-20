"""Shared exceptions for the SSR application."""


class CancelledError(Exception):
    """Raised when a chat request is cancelled by the user."""
    pass
