import unittest

from nlp.text_clean import clean_text


class CleanTextTests(unittest.TestCase):
    def test_default_cleanup_normalizes_unicode_and_whitespace(self) -> None:
        text = "ＡＢＣ　１２３\r\n\r\n hello\t world "

        self.assertEqual(clean_text(text), "ABC 123\nhello world")

    def test_remove_url_preserves_surrounding_non_url_text(self) -> None:
        text = "访问 https://example.com/a?q=1。 下一句"

        self.assertEqual(clean_text(text, remove_urls=True), "访问 。 下一句")

    def test_remove_numbers_punctuation_and_lowercase(self) -> None:
        text = "Hello，WORLD! １２3 apples."

        self.assertEqual(
            clean_text(
                text,
                lower=True,
                remove_numbers=True,
                remove_punctuation=True,
            ),
            "hello world apples",
        )

    def test_can_preserve_whitespace_and_blank_lines(self) -> None:
        text = " a  b \n\n\t\nc"

        self.assertEqual(
            clean_text(
                text,
                collapse_whitespace=False,
                remove_blank_lines=False,
                unicode_normalization=None,
            ),
            text,
        )

    def test_rejects_unknown_unicode_normalization(self) -> None:
        with self.assertRaises(ValueError):
            clean_text("text", unicode_normalization="INVALID")


if __name__ == "__main__":
    unittest.main()
