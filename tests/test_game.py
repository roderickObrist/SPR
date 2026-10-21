import unittest
from unittest.mock import patch

from src.core import Action, Move, Player, PlayerType, Strategy
from src.games.scissors_paper_rock import ScissorsPaperRockGame


class ScissorsPaperRockGameTests(unittest.TestCase):
    def setUp(self):
        self.players = [
            Player(PlayerType.HUMAN, "Human", Strategy()),
            Player(PlayerType.COMPUTER, "Computer", Strategy()),
        ]
        self.game = ScissorsPaperRockGame(self.players)
        self.actions = {
            action.name: action for action in self.game.get_action_space()
        }

    def test_action_space(self):
        self.assertCountEqual(
            self.game.get_action_space(),
            [Action("Rock", "r"), Action("Paper", "p"), Action("Scissors", "s")],
        )

    def test_payoffs_for_all_matchups(self):
        cases = [
            ("Rock", "Rock", (0, 0)),
            ("Rock", "Paper", (-1, 1)),
            ("Rock", "Scissors", (1, -1)),
            ("Paper", "Rock", (1, -1)),
            ("Paper", "Paper", (0, 0)),
            ("Paper", "Scissors", (-1, 1)),
            ("Scissors", "Rock", (-1, 1)),
            ("Scissors", "Paper", (1, -1)),
            ("Scissors", "Scissors", (0, 0)),
        ]
        for first, second, expected in cases:
            with self.subTest(first=first, second=second):
                moves = [
                    Move(self.players[0], self.actions[first], 0),
                    Move(self.players[1], self.actions[second], 0),
                ]

                self.game.assign_payoffs(moves)

                self.assertEqual(tuple(move.payoff for move in moves), expected)

    def test_requires_exactly_two_players(self):
        for count in (0, 1, 3):
            with self.subTest(player_count=count):
                players = [
                    Player(PlayerType.COMPUTER, f"Player {index}", Strategy())
                    for index in range(count)
                ]
                with self.assertRaisesRegex(ValueError, "exactly two players"):
                    ScissorsPaperRockGame(players)

    def test_rounds_return_scored_moves_and_preserve_history(self):
        rock = self.actions["Rock"]
        paper = self.actions["Paper"]
        scissors = self.actions["Scissors"]
        expected_first = [
            Move(self.players[0], paper, 1),
            Move(self.players[1], rock, -1),
        ]
        expected_second = [
            Move(self.players[0], scissors, 0),
            Move(self.players[1], scissors, 0),
        ]
        self.assertEqual(self.game.rounds, [])

        with (
            patch.object(self.players[0], "play", side_effect=[paper, scissors]),
            patch.object(self.players[1], "play", side_effect=[rock, scissors]),
        ):
            first = self.game.do_round()
            self.assertEqual(first, expected_first)
            self.assertEqual(self.game.rounds, [expected_first])

            second = self.game.do_round()

        self.assertEqual(second, expected_second)
        self.assertEqual(first, expected_first)
        self.assertEqual(self.game.rounds, [expected_first, expected_second])

    def test_games_have_independent_histories(self):
        other_game = ScissorsPaperRockGame(self.players)
        rock = self.actions["Rock"]
        with (
            patch.object(self.players[0], "play", return_value=rock),
            patch.object(self.players[1], "play", return_value=rock),
        ):
            self.game.do_round()

        self.assertEqual(len(self.game.rounds), 1)
        self.assertEqual(other_game.rounds, [])


if __name__ == "__main__":
    unittest.main()
