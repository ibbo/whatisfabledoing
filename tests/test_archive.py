"""Regression checks for the archive after removing the commercial offer."""
from html.parser import HTMLParser
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class Page(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.links = []
        self.text = []
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            self.links.append(dict(attrs).get("href", ""))

    def handle_data(self, data):
        self.text.append(data)


class ArchiveTest(unittest.TestCase):
    def test_withdrawn_offer_assets_are_not_published(self):
        for name in ("index.html", "sample.html", "sample.md"):
            with self.subTest(name=name):
                self.assertFalse((ROOT / "evidence-briefs" / name).exists())

    def test_homepage_does_not_promote_withdrawn_offer(self):
        page = Page((ROOT / "index.html").read_text())
        self.assertFalse(any("evidence-briefs" in url for url in page.links))
        self.assertNotIn("Read a source-linked evidence brief", " ".join(page.text))

    def test_archive_retains_honest_freshness_and_data(self):
        page = Page((ROOT / "index.html").read_text())
        self.assertIn("This is an archive", " ".join(page.text))
        for name in ("fable-field-reports.md", "fable-field-reports.json"):
            self.assertTrue((ROOT / "data" / name).is_file())


if __name__ == "__main__":
    unittest.main()
