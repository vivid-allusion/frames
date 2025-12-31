import unittest

from scripts.append_camera_dolly import SENTENCE, transform_text


class TestAppendCameraDolly(unittest.TestCase):
    def test_insert_after_terminal_period_no_newline(self) -> None:
        src = "A simple prompt."
        out = transform_text(src)
        self.assertEqual(out, "A simple prompt." + SENTENCE)

    def test_insert_before_trailing_newline(self) -> None:
        src = "A simple prompt.\n"
        out = transform_text(src)
        self.assertEqual(out, "A simple prompt." + SENTENCE + "\n")

    def test_no_period_append_with_dot(self) -> None:
        src = "A simple prompt"
        out = transform_text(src)
        self.assertTrue(out.endswith(". " + SENTENCE.lstrip()))

    def test_idempotent_skip_when_already_present(self) -> None:
        # Already ends with sentence
        src = "A simple prompt." + SENTENCE
        out = transform_text(src)
        self.assertEqual(out, src)

    def test_last_period_not_terminal_add_dot(self) -> None:
        # There is a period earlier, but not terminal; should add new ". " + sentence
        src = "Intro. Then more text without final period"
        out = transform_text(src)
        self.assertTrue(out.endswith(". " + SENTENCE.lstrip()))


if __name__ == "__main__":
    unittest.main()
