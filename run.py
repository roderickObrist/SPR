from src.games.scissors_paper_rock import ScissorsPaperRockGame
from src.core import Player, PlayerType, Strategy
from time import sleep

# from src.interfaces.cli import Cli
# from src.storage.file_system import FileSystemStorage

if __name__ == "__main__":
    game = ScissorsPaperRockGame([
        Player(PlayerType.COMPUTER, "Computer 1", Strategy()),
        Player(PlayerType.COMPUTER, "Computer 2", Strategy())
    ])
    # strategy = RandomStrategy()
    # storage = FileSystemStorage(game.name)
    # cli = Cli(game, storage, strategy, title=game.name)

    # cli.run()

    print(game.name)

    while True:
        round = game.do_round()
        print(round)

        sleep(10)