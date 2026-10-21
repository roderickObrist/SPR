from src.core import Action, Game, Move, Player


class ScissorsPaperRockGame(Game):
    name = "Scissors Paper Rock"

    def __init__(self, players: list[Player]):
        if len(players) != 2:
            raise ValueError("Scissors Paper Rock requires exactly two players")

        super().__init__(self.name, players)

    def get_action_space(self) -> list[Action]:
        return [
            Action("Scissors", "s"),
            Action("Paper", "p"),
            Action("Rock", "r"),
        ]

    def assign_payoffs(self, round: list[Move]) -> None:
        first, second = round

        if first.action == second.action:
            return

        beats = {"Scissors": "Paper", "Paper": "Rock", "Rock": "Scissors"}

        # First wins?
        if beats[first.action.name] == second.action.name:
            first.payoff = 1
            second.payoff = -1
        else:
            first.payoff = 1
            second.payoff = -1