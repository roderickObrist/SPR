import argparse
from getpass import getuser

from src.core import Player, PlayerType, Strategy
from src.games.scissors_paper_rock import ScissorsPaperRockGame as Game
from src.interfaces.udp import UdpCli as Cli
from src.storage.file_system import FileSystemStorage


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=f"Play {Game.name}")
    parser.add_argument(
        "--rounds", type=int, default=5, help="number of rounds to play (default: 5)"
    )
    args = parser.parse_args()
    if args.rounds < 1:
        parser.error("--rounds must be a positive integer")
    return args


def main():
    args = _parse_args()
    cli = Cli()

    strategy = cli.get_user_strategy()

    game = Game(
        [
            Player(PlayerType.HUMAN, getuser(), strategy),
            Player(PlayerType.COMPUTER, "Computer", Strategy()),
        ]
    )

    cli.load_game(game, FileSystemStorage())

    for _ in range(args.rounds):
        if not cli.play_round():
            break
    else:
        cli.finish()


if __name__ == "__main__":
    main()
