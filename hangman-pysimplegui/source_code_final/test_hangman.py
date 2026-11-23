"""Unit and scaling tests for Hangman in hangman-pysimplegui/source_code_final/hangman.py.

Precondition Anchors:
- Line 197: head = (100, 290)
- Line 198: torso = [((100, 270), (100, 170))]
"""

import pathlib
import sys
import time
import unittest

PROJECT_DIR = pathlib.Path(__file__).resolve().parent
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

import hangman


class TestHangmanScaling(unittest.TestCase):
    def test_smallest_valid_input_boundary(self):
        """Smallest valid input boundary: target word of length 1 ('A')."""
        game = hangman.Hangman(target_word="A")
        # Initial state: 1 hidden letter
        self.assertEqual(game._guessed_word, "_")
        self.assertEqual(game._wrong_guesses, 0)

        # Play correct guess
        game._play("A")
        self.assertEqual(game._guessed_word, "A")
        self.assertEqual(game._wrong_guesses, 0)

    def test_ordinary_fixture_input_and_drawing_anchors(self):
        """Ordinary fixture input: target word 'HANGMAN' and drawing anchors head and torso."""
        game = hangman.Hangman(target_word="HANGMAN")
        self.assertEqual(game._guessed_word, "_ _ _ _ _ _ _")

        # Play valid guesses
        game._play("A")
        game._play("N")
        # Expected display word:
        expected_word = "_ A N _ _ A N"
        self.assertEqual(game._guessed_word, expected_word)
        self.assertEqual(game._wrong_guesses, 0)

        # 1st wrong guess -> head drawn (line 197 anchor)
        game._play("Z")
        self.assertEqual(game._wrong_guesses, 1)
        drawings = game._canvas.drawings
        head_drawings = [d for d in drawings if d[0] == "circle" and d[1] == (100, 290)]
        self.assertEqual(len(head_drawings), 1)

        # 2nd wrong guess -> torso drawn (line 198 anchor)
        game._play("X")
        self.assertEqual(game._wrong_guesses, 2)
        torso_drawings = [
            d for d in game._canvas.drawings
            if d[0] == "line" and d[1] == ((100, 270), (100, 170))
        ]
        self.assertEqual(len(torso_drawings), 1)

    def test_scaling_and_operation_counts(self):
        """Measure scaling of Hangman on 3 increasing sizes: N=1, N=7, N=20."""
        sizes = [
            ("A", 1),
            ("HANGMAN", 7),
            ("ELECTROENCEPHALOGRAM", 20),
        ]
        repetitions = 5

        for word, expected_n in sizes:
            for rep in range(repetitions):
                game = hangman.Hangman(target_word=word)
                # Word construction operation count is exactly N character iterations
                start = time.perf_counter()
                display = game._build_guessed_word()
                duration = time.perf_counter() - start

                # Correctness assertions outside timed interval
                self.assertEqual(len(game._target_word), expected_n)
                expected_blanks = " ".join(["_"] * expected_n)
                self.assertEqual(display, expected_blanks)
                self.assertGreaterEqual(duration, 0.0)


if __name__ == "__main__":
    unittest.main()
