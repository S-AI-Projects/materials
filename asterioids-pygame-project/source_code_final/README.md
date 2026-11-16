# Space Rocks

A simple space game made with Python and Pygame

## Installation

Requires Python 3.

```
pip install -r requirements.txt
python space_rocks
```

## Worked example: SpaceRocks game logic

This deterministic example exercises the real `_process_game_logic()` method
without opening a game window or loading assets. Run it from this
`source_code_final/` directory with the documented Pygame dependency installed.

The constructor initializes the asteroid and bullet lists at
`space_rocks/game.py:17–18`. The smallest fixture uses those empty lists.
In the ordinary fixture, a bullet hits a size-1 asteroid. The game removes
both objects and calls `asteroid.split()` (`game.py:79–81`). The model only
creates smaller asteroids when `size > 1` (`models.py:73–74`), so this
terminal asteroid leaves the list empty and the active spaceship wins
(`game.py:88–89`).

<!-- SPACE_ROCKS_EXAMPLE_BEGIN -->
```python
import os
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
from pathlib import Path
import sys

sys.path.insert(0, str(Path("space_rocks").resolve()))
from game import SpaceRocks


class Thing:
    def move(self, _screen):
        pass


class Ship(Thing):
    pass


class Bullet(Thing):
    pass


class TerminalAsteroid(Thing):
    def __init__(self):
        self.size = 1
        self.split_called = False

    def collides_with(self, other):
        return isinstance(other, Bullet)

    def split(self):
        # Asteroid.split() creates children only when size > 1.
        self.split_called = True


def make_game(asteroids, bullets):
    game = SpaceRocks.__new__(SpaceRocks)
    game.screen = object()
    game.asteroids = asteroids
    game.bullets = bullets
    game.spaceship = Ship()
    game.message = ""
    return game


def report(game):
    return {
        "asteroids": len(game.asteroids),
        "bullets": len(game.bullets),
        "spaceship_active": game.spaceship is not None,
        "message": game.message,
    }


# Smallest input: the two empty collections established by game.py:17–18.
smallest = make_game(asteroids=[], bullets=[])
smallest._process_game_logic()
print("smallest:", report(smallest))

# Ordinary input: one terminal (size-1) asteroid and one bullet.
rock = TerminalAsteroid()
ordinary = make_game(asteroids=[rock], bullets=[Bullet()])
print("ordinary input:", {
    "asteroids": len(ordinary.asteroids),
    "bullets": len(ordinary.bullets),
    "spaceship_active": ordinary.spaceship is not None,
})
ordinary._process_game_logic()
result = report(ordinary)
result["terminal_asteroid_split_called"] = rock.split_called
print("ordinary result:", result)
```
<!-- SPACE_ROCKS_EXAMPLE_END -->

Expected output:

```text
smallest: {'asteroids': 0, 'bullets': 0, 'spaceship_active': True, 'message': 'You won!'}
ordinary input: {'asteroids': 1, 'bullets': 1, 'spaceship_active': True}
ordinary result: {'asteroids': 0, 'bullets': 0, 'spaceship_active': True, 'message': 'You won!', 'terminal_asteroid_split_called': True}
```
