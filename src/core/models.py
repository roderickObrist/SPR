from enum import Enum
from typing import NamedTuple
from random import choices
from dataclasses import dataclass


class Action(NamedTuple):
    name: str
    shortcut: str


class PlayerType(Enum):
    HUMAN = "HUMAN"
    COMPUTER = "COMPUTER"


@dataclass
class Strategy:
    def probabilities_for_actions(self, actions: list[Action]) -> list[float]:
        return [1 / len(actions) for _ in actions]


@dataclass
class Player:
    type: PlayerType
    name: str
    strategy: Strategy

    def play(self, actions: list[Action]) -> Action:
        p = self.strategy.probabilities_for_actions(actions)
        (action,) = choices(actions, weights=p)
        return action

@dataclass
class Move():
    player: Player
    action: Action
    payoff: int

