from collections.abc import Callable

from src.core import Action, Game, Interface, Storage, Strategy


class _Exit(Exception):
    pass


class HumanStrategy(Strategy):
    def __init__(self, save: Callable[[], None]):
        self.save = save

    def probabilities_for_actions(self, actions: list[Action]) -> list[float]:
        options = {
            key.lower(): action
            for action in actions
            for key in (action.name, action.shortcut)
        }
        choices = ", ".join(
            f"{action.name.lower()} ({action.shortcut})" for action in actions
        )
        while True:
            choice = input(f"Choose {choices}, save, or exit: ").strip().lower()
            if choice == "save":
                self.save()
            elif choice == "exit":
                raise _Exit
            elif choice in options:
                return [float(action == options[choice]) for action in actions]
            else:
                print("Invalid choice. Try again.")


class Cli(Interface):
    def get_user_strategy(self) -> Strategy:
        return HumanStrategy(self.save_state)

    def load_game(self, game: Game, storage: Storage) -> None:
        self.game, self.storage = game, storage
        try:
            self.load_state()
        except FileNotFoundError:
            return
        if not self._confirm("Resume saved game? (y/n): "):
            game.rounds = []

    def play_round(self) -> bool:
        try:
            moves = self.game.do_round()
        except _Exit:
            return False
        for move in moves:
            print(f"{move.player.name}: {move.action.name}")
        result = (
            "Win" if moves[0].payoff > 0 else "Loss" if moves[0].payoff < 0 else "Tie"
        )
        print(result)
        return True

    def finish(self) -> None:
        if self._confirm("Save game? (y/n): "):
            self.save_state()

    def save_state(self) -> None:
        self.storage.save_state(self.game)
        print("Game saved.")

    def load_state(self) -> None:
        self.storage.load_state(self.game)

    def _confirm(self, prompt: str) -> bool:
        while True:
            answer = input(prompt).strip().lower()
            if answer in ("y", "yes"):
                return True
            if answer in ("n", "no"):
                return False
            print("Please enter yes or no.")
