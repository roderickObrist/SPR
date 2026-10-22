from src.core import Action, Game, Move, Player


class PrisonersDilemmaGame(Game):
    name = "Prisoner's Dilemma"

    def __init__(self, players: list[Player]):
        if len(players) != 2:
            raise ValueError("Prisoner's Dilemma requires exactly two players")
        super().__init__(self.name, players)

    def get_action_space(self) -> list[Action]:
        return [Action("Cooperate", "c"), Action("Defect", "d")]

    def assign_payoffs(self, round: list[Move]) -> None:
        first, second = round
        payoffs = {
            ("Cooperate", "Cooperate"): (3, 3),
            ("Cooperate", "Defect"): (0, 5),
            ("Defect", "Cooperate"): (5, 0),
            ("Defect", "Defect"): (1, 1),
        }
        first.payoff, second.payoff = payoffs[first.action.name, second.action.name]
