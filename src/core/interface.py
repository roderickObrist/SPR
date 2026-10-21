from abc import ABC, abstractmethod

from .game import Game
from .models import Strategy
from .storage import Storage


class Interface(ABC):
    """User-facing session for playing and persisting a game."""

    @abstractmethod
    def get_user_strategy(self) -> Strategy:
        """Create the strategy used to collect the human player's actions."""

    @abstractmethod
    def load_game(self, game: Game, storage: Storage) -> None:
        """Attach a game and its storage to this session."""

    @abstractmethod
    def play_round(self) -> None:
        """Play and present one round of the attached game."""

    @abstractmethod
    def save_state(self) -> None:
        """Save the attached game's state using its storage."""

    @abstractmethod
    def load_state(self) -> None:
        """Restore the attached game's state using its storage."""
