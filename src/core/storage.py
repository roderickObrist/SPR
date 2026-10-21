from abc import ABC, abstractmethod

from .game import Game


class Storage(ABC):
    """Persist the state of an existing game."""

    @abstractmethod
    def save_state(self, game: Game) -> None:
        """Save the game's completed rounds."""

    @abstractmethod
    def load_state(self, game: Game) -> None:
        """Restore completed rounds into the game."""
