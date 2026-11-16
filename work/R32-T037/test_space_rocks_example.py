import re
import sys
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from types import ModuleType

ROOT = Path(__file__).resolve().parents[2]
PROJECT = ROOT / "asterioids-pygame-project" / "source_code_final"
SPACE_ROCKS = PROJECT / "space_rocks"
sys.path.insert(0, str(SPACE_ROCKS))

# Stub imported dependencies so the tests exercise only the named game module.
pygame_stub = ModuleType("pygame")
models_stub = ModuleType("models")
models_stub.Asteroid = type("Asteroid", (), {})
models_stub.Spaceship = type("Spaceship", (), {})
utils_stub = ModuleType("utils")
for helper in ("get_random_position", "load_sprite", "print_text"):
    setattr(utils_stub, helper, lambda *args, **kwargs: None)
sys.modules["pygame"] = pygame_stub
sys.modules["models"] = models_stub
sys.modules["utils"] = utils_stub

from game import SpaceRocks  # noqa: E402


class DemoObject:
    def move(self, _screen):
        pass


class DemoShip(DemoObject):
    pass


class DemoBullet(DemoObject):
    pass


class DemoAsteroid(DemoObject):
    def __init__(self, size=1):
        self.size = size
        self.split_called = False

    def collides_with(self, other):
        return isinstance(other, DemoBullet)

    def split(self):
        # A real size-1 Asteroid does not create smaller asteroids.
        self.split_called = True


def make_game(asteroids, bullets):
    game = SpaceRocks.__new__(SpaceRocks)
    game.screen = object()
    game.asteroids = asteroids
    game.bullets = bullets
    game.spaceship = DemoShip()
    game.message = ""
    return game


def test_source_lines_establish_fixtures_and_terminal_asteroid():
    game_lines = (SPACE_ROCKS / "game.py").read_text().splitlines()
    model_lines = (SPACE_ROCKS / "models.py").read_text().splitlines()
    assert game_lines[16].strip() == "self.asteroids = []", "game.py:17"
    assert game_lines[17].strip() == "self.bullets = []", "game.py:18"
    assert game_lines[80].strip() == "asteroid.split()", "game.py:81"
    assert game_lines[87].strip() == (
        "if not self.asteroids and self.spaceship:"
    ), "game.py:88"
    assert game_lines[88].strip() == 'self.message = "You won!"', "game.py:89"
    assert model_lines[64].strip() == "self.size = size", "models.py:65"
    assert model_lines[73].strip() == "if self.size > 1:", "models.py:74"


def test_smallest_valid_input():
    # Literal input: no asteroids, no bullets, active spaceship.
    game = make_game(asteroids=[], bullets=[])
    game._process_game_logic()
    # Independently expected: the active ship wins with no asteroids.
    assert game.asteroids == []
    assert game.bullets == []
    assert game.spaceship is not None
    assert game.message == "You won!"


def test_ordinary_bullet_collision_with_terminal_asteroid():
    # Literal ordinary input: one size-1 asteroid, one bullet, active ship.
    rock = DemoAsteroid(size=1)
    game = make_game(asteroids=[rock], bullets=[DemoBullet()])
    game._process_game_logic()
    # Expected: remove both objects; size 1 splits into no child asteroids.
    assert rock.size == 1
    assert game.asteroids == []
    assert game.bullets == []
    assert rock.split_called is True
    assert game.spaceship is not None
    assert game.message == "You won!"


def test_readme_example_executes_and_prints_expected_output(monkeypatch):
    readme = (PROJECT / "README.md").read_text()
    fence = chr(96) * 3
    pattern = (
        r"<!-- SPACE_ROCKS_EXAMPLE_BEGIN -->\s*"
        + fence
        + r"python\s*(.*?)"
        + fence
    )
    match = re.search(pattern, readme, re.DOTALL)
    assert match is not None, "Runnable README example not found"
    monkeypatch.chdir(PROJECT)
    output = StringIO()
    with redirect_stdout(output):
        exec(
            compile(match.group(1), "README example", "exec"),
            {"__name__": "__main__"},
        )
    expected = (
        "smallest: {'asteroids': 0, 'bullets': 0, 'spaceship_active': True, 'message': 'You won!'}\n"
        "ordinary input: {'asteroids': 1, 'bullets': 1, 'spaceship_active': True}\n"
        "ordinary result: {'asteroids': 0, 'bullets': 0, 'spaceship_active': True, 'message': 'You won!', 'terminal_asteroid_split_called': True}\n"
    )
    assert output.getvalue() == expected
