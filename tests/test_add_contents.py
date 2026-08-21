import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills" / "markdown-contents" / "scripts" / "add_contents.py"
SPEC = importlib.util.spec_from_file_location("add_contents", SCRIPT)
add_contents = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = add_contents
SPEC.loader.exec_module(add_contents)


LIST = "- [Install](#install)\n- [Use](#use)\n"


class AddContentsTests(unittest.TestCase):
    def test_readme_places_contents_after_opening_description(self):
        source = "# Tool\n\nA short description.\n\nAnother opening paragraph.\n\n## Install\n\nText.\n\n## Use\n\nText.\n"
        result = add_contents.update_text(source, "README.md", LIST)
        self.assertLess(result.index("Another opening paragraph."), result.index(add_contents.START))
        self.assertLess(result.index(add_contents.END), result.index("## Install"))

    def test_readme_rejects_a_custom_location(self):
        source = "# Tool\n\nDescription.\n\n## Install\n\nText.\n\n## Use\n\nText.\n"
        with self.assertRaisesRegex(add_contents.ContentsError, "always puts"):
            add_contents.update_text(source, "README.md", LIST, before_heading="Use")

    def test_other_file_requires_a_location(self):
        source = "# Guide\n\n## One\n\nText.\n\n## Two\n\nText.\n"
        with self.assertRaisesRegex(add_contents.ContentsError, "Choose a location"):
            add_contents.update_text(source, "guide.md", LIST)

    def test_before_heading_uses_exact_heading(self):
        source = "# Guide\n\nIntro.\n\n## Install\n\nText.\n\n## Use\n\nText.\n"
        result = add_contents.update_text(source, "guide.md", LIST, before_heading="Install")
        self.assertLess(result.index(add_contents.END), result.index("## Install"))

    def test_after_heading_inserts_directly_below_it(self):
        source = "# Guide\n\n## Overview\n\nIntro.\n\n## Use\n\nText.\n"
        result = add_contents.update_text(source, "guide.md", LIST, after_heading="Overview")
        self.assertLess(result.index("## Overview"), result.index(add_contents.START))
        self.assertLess(result.index(add_contents.END), result.index("Intro."))

    def test_line_location_is_supported(self):
        source = "# Guide\n\nIntro.\n\n## One\n\nText.\n\n## Two\n"
        result = add_contents.update_text(source, "guide.md", LIST, at_line=5)
        self.assertLess(result.index(add_contents.END), result.index("## One"))

    def test_existing_contents_are_replaced_without_moving(self):
        source = (
            "# Guide\n\nIntro.\n\n"
            f"{add_contents.START}\n## Contents\n\n- [Old](#old)\n{add_contents.END}\n\n"
            "## One\n\nText.\n\n## Two\n\nText.\n"
        )
        result = add_contents.update_text(source, "guide.md", LIST)
        self.assertEqual(result.count(add_contents.START), 1)
        self.assertNotIn("[Old]", result)
        self.assertIn("[Install]", result)

    def test_heading_inside_code_block_is_ignored(self):
        source = "# Guide\n\n```md\n## Install\n```\n\n## Install\n\nText.\n\n## Use\n\nText.\n"
        result = add_contents.update_text(source, "guide.md", LIST, before_heading="Install")
        self.assertLess(result.index(add_contents.END), result.rindex("## Install"))

    def test_repeated_heading_requires_a_line_number(self):
        source = "# Guide\n\n## Example\n\nOne.\n\n## Example\n\nTwo.\n"
        with self.assertRaisesRegex(add_contents.ContentsError, "more than once"):
            add_contents.update_text(source, "guide.md", LIST, before_heading="Example")

    def test_windows_newlines_are_preserved(self):
        source = "# Guide\r\n\r\nIntro.\r\n\r\n## One\r\n\r\n## Two\r\n"
        result = add_contents.update_text(source, "guide.md", LIST, before_heading="One")
        self.assertNotIn("\n", result.replace("\r\n", ""))


if __name__ == "__main__":
    unittest.main()
