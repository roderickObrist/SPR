from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from .models import Action, Move, Player

@dataclass
class Game(ABC):
    """Rules and state for a two-player, turn-based game."""

    name: str
    players: list[Player]
    rounds: list[list[Move]] = field(default_factory=list)

    def do_round(self) -> list[Move]:
        actions = self.get_action_space()
        moves = [Move(player, player.play(actions), 0) for player in self.players]

        self.assign_payoffs(moves)
        self.rounds.append(moves)

        return moves

    @abstractmethod
    def get_action_space(self) -> list[Action]:
        pass

    @abstractmethod
    def assign_payoffs(self, round: list[Move]) -> None:
        pass
