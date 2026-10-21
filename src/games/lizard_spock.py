from src.core import Action, Move
from src.games.scissors_paper_rock import ScissorsPaperRockGame


class LizardSpockGame(ScissorsPaperRockGame):
    name = "Scissors Paper Rock Lizard Spock"

    def get_action_space(self) -> list[Action]:
        return super().get_action_space() + [
            Action("Lizard", "l"),
            Action("Spock", "v"),
        ]

    def assign_payoffs(self, round: list[Move]) -> None:
        first, second = round
        if first.action == second.action:
            return

        beats = {
            "Scissors": {"Paper", "Lizard"},
            "Paper": {"Rock", "Spock"},
            "Rock": {"Scissors", "Lizard"},
            "Lizard": {"Paper", "Spock"},
            "Spock": {"Scissors", "Rock"},
        }
        first.payoff = 1 if second.action.name in beats[first.action.name] else -1
        second.payoff = -first.payoff
