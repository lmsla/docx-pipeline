import unittest

from docx_pipeline.cli import make_parser


class ChapterBreakOptionTest(unittest.TestCase):
    def test_chapter_breaks_are_disabled_by_default(self):
        args = make_parser().parse_args(["build", "input.md", "-o", "output.docx"])
        self.assertFalse(args.chapter_breaks)

    def test_chapter_breaks_can_be_enabled_explicitly(self):
        args = make_parser().parse_args(
            ["build", "input.md", "-o", "output.docx", "--chapter-breaks"]
        )
        self.assertTrue(args.chapter_breaks)


if __name__ == "__main__":
    unittest.main()
