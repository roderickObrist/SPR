import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import run
from src.core import Action, Player, PlayerType, Strategy
from src.games.scissors_paper_rock import ScissorsPaperRockGame
from src.interfaces import Cli
from src.interfaces.cli import _style
from src.storage import FileSystemStorage


class RockStrategy(Strategy):
    def probabilities_for_actions(self, actions):
        return [float(action.name == "Rock") for action in actions]


class FirstActionStrategy(Strategy):
    def probabilities_for_actions(self, actions):
        return [1.0] + [0.0] * (len(actions) - 1)


def game(cli):
    return ScissorsPaperRockGame([
        Player(PlayerType.HUMAN, "Human", cli.get_user_strategy()),
        Player(PlayerType.COMPUTER, "Computer", RockStrategy()),
    ])


class CliTests(unittest.TestCase):
    def setUp(self):
        self.enterContext(patch("src.interfaces.cli.sys.stdout.isatty", return_value=False))

    def session(self, answers):
        prompts, output = [], []
        choices = iter(answers)

        def ask(prompt):
            prompts.append(prompt)
            return next(choices)

        for name, replacement in (("input", ask), ("print", output.append)):
            mocked = patch(f"builtins.{name}", replacement)
            mocked.start()
            self.addCleanup(mocked.stop)
        return Cli(), prompts, output

    def test_prompt_uses_actions(self):
        cli, prompts, _ = self.session(["v"])
        actions = [Action("Lizard", "l"), Action("Spock", "v")]
        self.assertEqual(cli.get_user_strategy().probabilities_for_actions(actions), [0.0, 1.0])
        self.assertEqual(len(prompts), 1)
        for option in ("Lizard (L)", "Spock (V)", "SAVE", "EXIT"):
            self.assertIn(option, prompts[0])

    def test_overridden_io_handles_moves_results_and_saving(self):
        choices = iter(["bad", "paper", "maybe", "yes"])
        output = []

        class ScriptedCli(Cli):
            def _read(self, prompt):
                return next(choices)

            def _write(self, text):
                output.append(text)

        with tempfile.TemporaryDirectory() as directory:
            storage = FileSystemStorage(Path(directory) / "game.json")
            cli = ScriptedCli()
            with patch("builtins.input", side_effect=AssertionError("Unexpected console input")), \
                 patch("builtins.print", side_effect=AssertionError("Unexpected console output")):
                cli.load_game(game(cli), storage)
                self.assertTrue(cli.play_round())
                cli.finish()

            self.assertEqual(len(json.loads(storage.path.read_text())), 1)
        self.assertIn("Invalid choice. Try again.", output)
        self.assertTrue(any("You played: Paper" in message for message in output))
        self.assertIn("Please enter yes or no.", output)
        self.assertIn("Game saved.", output)

    def test_choices_and_results(self):
        cli, prompts, output = self.session(["bad", " S ", "paper", "R"])
        with tempfile.TemporaryDirectory() as directory:
            current = game(cli)
            cli.load_game(current, FileSystemStorage(Path(directory) / "game.json"))
            self.assertEqual([cli.play_round() for _ in range(3)], [True] * 3)
        self.assertEqual([round_[0].action.name for round_ in current.rounds],
                         ["Scissors", "Paper", "Rock"])
        self.assertIn("Invalid choice. Try again.", output)
        for number, (message, action, result) in enumerate(
            zip(output[-3:], ("Scissors", "Paper", "Rock"), ("LOSS", "WIN", "TIE")),
            start=1,
        ):
            with self.subTest(round=number):
                self.assertIn(f"ROUND {number}", message)
                self.assertIn(f"You played: {action}", message)
                self.assertIn("Computer played: Rock", message)
                self.assertIn(result, message)
        self.assertEqual(len(prompts), 4)

    def test_save_then_exit(self):
        cli, _, output = self.session(["p", "SAVE", "s", "exit"])
        with tempfile.TemporaryDirectory() as directory:
            storage = FileSystemStorage(Path(directory) / "game.json")
            current = game(cli)
            cli.load_game(current, storage)
            self.assertTrue(cli.play_round())
            self.assertTrue(cli.play_round())
            self.assertFalse(cli.play_round())
            self.assertEqual(len(current.rounds), 2)
            self.assertEqual(len(json.loads(storage.path.read_text())), 1)
        self.assertEqual(output.count("Game saved."), 1)

    def test_resume_decline_and_missing_file(self):
        with tempfile.TemporaryDirectory() as directory:
            storage = FileSystemStorage(Path(directory) / "game.json")
            cli, prompts, _ = self.session([])
            cli.load_game(game(cli), storage)
            self.assertEqual(prompts, [])
            cli, _, _ = self.session(["p"])
            original = game(cli)
            cli.load_game(original, storage)
            cli.play_round()
            cli.save_state()

            cli, prompts, _ = self.session(["YES"])
            resumed = game(cli)
            cli.load_game(resumed, storage)
            self.assertEqual(len(resumed.rounds), 1)
            self.assertEqual(len(prompts), 1)

            cli, _, _ = self.session(["no"])
            fresh = game(cli)
            cli.load_game(fresh, storage)
            self.assertEqual(fresh.rounds, [])

    def test_load_errors_remain_visible(self):
        with tempfile.TemporaryDirectory() as directory:
            storage = FileSystemStorage(Path(directory) / "game.json")
            storage.path.write_text("broken json")
            cli, _, _ = self.session([])
            with self.assertRaises(json.JSONDecodeError):
                cli.load_game(game(cli), storage)

    def test_main_counts_new_rounds_and_offers_final_save(self):
        with tempfile.TemporaryDirectory() as directory:
            storage = FileSystemStorage(Path(directory) / "game.json")
            original = run.Game([
                Player(PlayerType.HUMAN, "Human", FirstActionStrategy()),
                Player(PlayerType.COMPUTER, "Computer", FirstActionStrategy()),
            ])
            original.do_round()
            storage.save_state(original)
            actions = original.get_action_space()
            new_actions = [actions[-1], actions[0]]

            cli, _, _ = self.session(["y", new_actions[0].shortcut, new_actions[1].name, "y"])
            with patch.object(run, "Cli", return_value=cli), \
                 patch.object(run, "FileSystemStorage", return_value=storage), \
                 patch.object(run, "Strategy", FirstActionStrategy), \
                 patch.object(run, "getuser", return_value="Human"), \
                 patch("sys.argv", ["run.py", "--rounds", "2"]):
                run.main()

            restored = run.Game(original.players)
            storage.load_state(restored)
            self.assertEqual(len(cli.game.rounds), 3)
            self.assertEqual(
                [round_[0].action for round_ in restored.rounds],
                [actions[0], *new_actions],
            )

    def test_main_exit_skips_final_save(self):
        cli, prompts, _ = self.session(["exit"])
        with tempfile.TemporaryDirectory() as directory:
            storage = FileSystemStorage(Path(directory) / "game.json")
            with patch.object(run, "Cli", return_value=cli), \
                 patch.object(run, "FileSystemStorage", return_value=storage), \
                 patch("sys.argv", ["run.py", "--rounds", "5"]):
                run.main()
            self.assertFalse(storage.path.exists())
            self.assertEqual(len(prompts), 1)


class StyleTests(unittest.TestCase):
    def test_terminal_output_has_ansi_formatting(self):
        with patch("src.interfaces.cli.sys.stdout.isatty", return_value=True):
            self.assertEqual(_style("ROUND 1"), "\033[1mROUND 1\033[0m")
            self.assertEqual(_style("WIN", "1;32"), "\033[1;32mWIN\033[0m")

    def test_redirected_output_has_no_ansi_formatting(self):
        with patch("src.interfaces.cli.sys.stdout.isatty", return_value=False):
            self.assertEqual(_style("ROUND 1"), "ROUND 1")
            self.assertEqual(_style("WIN", "1;32"), "WIN")


if __name__ == "__main__":
    unittest.main()
