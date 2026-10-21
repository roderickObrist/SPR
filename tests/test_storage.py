import tempfile
import unittest
from pathlib import Path

from src.core import Action, Move, Player, PlayerType, Storage, Strategy
from src.games.scissors_paper_rock import ScissorsPaperRockGame
from src.storage import FileSystemStorage


def make_game() -> ScissorsPaperRockGame:
    return ScissorsPaperRockGame(
        [
            Player(PlayerType.HUMAN, "Human", Strategy()),
            Player(PlayerType.COMPUTER, "Computer", Strategy()),
        ]
    )


class FileSystemStorageTests(unittest.TestCase):
    def test_storage_is_abstract(self) -> None:
        with self.assertRaises(TypeError):
            Storage()

    def test_round_trip(self) -> None:
        game = make_game()
        game.rounds = [[
            Move(game.players[0], Action("Scissors", "s"), 1),
            Move(game.players[1], Action("Paper", "p"), -1),
        ]]
        self.assertEqual(game.rounds[0][0].__json__(), ("s", 1))

        with tempfile.TemporaryDirectory() as directory:
            storage = FileSystemStorage(Path(directory) / "game.json")
            storage.save_state(game)
            restored = make_game()
            storage.load_state(restored)

        self.assertEqual(
            [(move.action.name, move.payoff) for move in restored.rounds[0]],
            [("Scissors", 1), ("Paper", -1)],
        )
        self.assertIs(restored.rounds[0][0].player, restored.players[0])

    def test_missing_save(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            storage = FileSystemStorage(Path(directory) / "game.json")
            with self.assertRaises(FileNotFoundError):
                storage.load_state(make_game())

if __name__ == "__main__":
    unittest.main()
