# Extensible Games CLI

Build a Python 3.11+ application using only the standard library. Support scissors-paper-rock against the computer.


## Usage

To run:
```bash
python3 run.py --rounds 5
```

To test:
```bash
python3 -m unittest -v
```

## Design Trade Offs
The verbal and written feedback was to design for:
 - extensibility; 
 - maintainability; and to 
 - demonstrate ability outside of AI code generators

This design has abstracted:
 - Game
 - Action
 - Move (Action + Player + PayOff)
 - Interface
 - Player

To demonstrate the extensibility of this codebase, I have cherrypicked 4 extensions and coded them all without needing the `core` folder. I have also tabulated the diff size and number of files touched.

| Branch | Feature | Diff | Files touched | Verify |
|---|---|---|---|---|
| `prisoners-dilemma` | Prisoner's Dilemma game | +25 / −2 | 2 | `git diff --minimal master...prisoners-dilemma` |
| `lizard-spock` | Rock Paper Scissors Lizard Spock game | +28 / −1 | 2 | `git diff --minimal master...lizard-spock` |
| `serial` | Serial interface (9600 baud, 8N1) | +46 / −9 | 3 | `git diff --minimal master...serial` |
| `udp` | UDP interface on localhost port 9999 | +38 / −9 | 3 | `git diff --minimal master...udp` |

Diff sizes show insertions and deletions relative to `master`. None of these branches modify `src/core`.
