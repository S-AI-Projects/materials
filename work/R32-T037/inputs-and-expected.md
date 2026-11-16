# R32-T037 — Inputs, preconditions, and expected results

The documented behavior targets `SpaceRocks._process_game_logic()` in
`asterioids-pygame-project/source_code_final/space_rocks/game.py`.

## Source-backed preconditions

- `game.py:17` initializes `self.asteroids = []`.
- `game.py:18` initializes `self.bullets = []`.
- `game.py:79–81` removes a colliding asteroid and bullet, then calls
  `asteroid.split()`.
- `game.py:88–89` sets `"You won!"` when the asteroid list is empty and the
  spaceship remains active.
- `models.py:65` records the asteroid size; `models.py:73–74` creates smaller
  asteroids only when `self.size > 1`. A size-1 asteroid is terminal.

The tests create a `SpaceRocks` instance with `__new__` and set only the state
needed by the focused method. Pygame, models, and utils imports are stubbed;
no window, assets, audio, clock, input device, or external I/O is used.

## Fixture 1 — smallest controlled input

Literal input:

```python
asteroids = []
bullets = []
spaceship = DemoShip()
```

Independent expected output after `_process_game_logic()`:

```python
{
    "asteroids": [],
    "bullets": [],
    "spaceship_active": True,
    "message": "You won!",
}
```

Reason: `game.py:88–89` finds no asteroids and an active spaceship.

## Fixture 2 — ordinary bullet collision

Literal input:

```python
asteroids = [DemoAsteroid(size=1)]
bullets = [DemoBullet()]
spaceship = DemoShip()
```

The deterministic asteroid double collides with the bullet, not the ship.
It represents the real model's terminal size-1 asteroid (`models.py:73–74`)
so splitting creates no child asteroids.

Independent expected output after `_process_game_logic()`:

```python
{
    "asteroids": [],
    "bullets": [],
    "asteroid_split_called": True,
    "spaceship_active": True,
    "message": "You won!",
}
```

Reason: `game.py:79–81` removes both colliding objects and calls `split()`;
the size-1 asteroid adds no children, so `game.py:88–89` sets the win message.
