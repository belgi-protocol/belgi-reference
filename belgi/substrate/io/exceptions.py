from __future__ import annotations

__all__ = [
    "AtomicWriteBatchRollbackError",
    "RootedAtomicCapabilityError",
    "RootedPathSymlinkError",
    "WindowsReparsePointError",
]


class AtomicWriteBatchRollbackError(OSError):
    def __init__(
        self,
        *,
        original_error: BaseException,
        recovery_actions: tuple[str, ...],
    ) -> None:
        self.original_error = original_error
        self.recovery_actions = recovery_actions
        recovery = "; ".join(recovery_actions)
        super().__init__(
            "atomic text batch rollback incomplete after "
            f"{type(original_error).__name__}: {original_error}; "
            f"manual recovery required: {recovery}"
        )


class RootedPathSymlinkError(OSError):
    """Raised when a rooted snapshot encounters a symlink component."""


class RootedAtomicCapabilityError(OSError):
    """Raised when the host cannot provide rooted atomic filesystem operations."""


class WindowsReparsePointError(OSError):
    """Raised when a rooted Windows operation encounters a reparse point."""
