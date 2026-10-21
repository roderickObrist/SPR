from src.games.scissors_paper_rock import ScissorsPaperRockGame
from src.core import Player, PlayerType, Strategy
from time import sleep
from getpass import getuser
from src.interfaces.cli import Cli

from src.storage.file_system import FileSystemStorage

if __name__ == "__main__":
    cli = Cli()

    strategy = cli.get_user_strategy()

    game = ScissorsPaperRockGame(
        [
            Player(PlayerType.HUMAN, getuser(), strategy),
            Player(PlayerType.COMPUTER, "Computer", Strategy()),
        ]
    )

    cli.load_game(game, FileSystemStorage())

    for i in range(5):
        cli.play_round()
