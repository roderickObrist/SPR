import json
from pathlib import Path

from src.core import Game, Move, Storage


class FileSystemStorage(Storage):
    def __init__(self, path: str | Path = ".saves/game.json") -> None:
        self.path = Path(path)

    def save_state(self, game: Game) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(game.rounds, default=Move.__json__))

    def load_state(self, game: Game) -> None:
        rounds = json.loads(self.path.read_text())
        actions = {action.shortcut: action for action in game.get_action_space()}
        game.rounds = [
            [Move(player, actions[action], payoff) for player, (action, payoff) in zip(game.players, moves)]
            for moves in rounds
        ]
