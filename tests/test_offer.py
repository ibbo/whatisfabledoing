"""Static contract checks for the evidence-brief enquiry page."""
from html.parser import HTMLParser
from pathlib import Path
import unittest
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]


class Page(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.links = []
        self.tags = []
        self.text = []
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        self.tags.append(tag)
        if tag == "a":
            self.links.append(dict(attrs).get("href", ""))

    def handle_data(self, data):
        self.text.append(data)


class OfferTest(unittest.TestCase):
    def test_interest_path_is_explicitly_non_transactional(self):
        path = ROOT / "evidence-briefs/index.html"
        self.assertTrue(path.is_file(), "Evidence-brief enquiry page is missing")
        page = Page(path.read_text())
        text = " ".join(" ".join(page.text).split())
        self.assertIn("£149", text)
        self.assertIn("No payment is taken", text)
        self.assertIn("public", text)
        self.assertIn("not personally reviewed by Thomas", text)
        self.assertNotIn("form", page.tags)
        self.assertNotIn("script", page.tags)
        enquiries = [u for u in page.links if urlsplit(u).netloc == "github.com" and urlsplit(u).path == "/ibbo/whatisfabledoing/issues/new"]
        self.assertEqual(len(enquiries), 1, "Use exactly one explicit public enquiry route")
        self.assertFalse(any(u.startswith("mailto:") for u in page.links), "Do not expose a private email")

    def test_archive_links_to_offer_without_claiming_active_collection(self):
        page = Page((ROOT / "index.html").read_text())
        self.assertIn("evidence-briefs/", page.links)
        self.assertNotIn("New reports are added a few times a day.", " ".join(page.text))


    def test_sample_page_is_complete_linked_and_honest(self):
        path = ROOT / "evidence-briefs/sample.html"
        self.assertTrue(path.is_file(), "Sample page is missing")
        page = Page(path.read_text())
        text = " ".join(page.text)
        for phrase in ("AI-prepared sample", "not a vendor ranking", "No third-party code was executed"):
            self.assertIn(phrase, text)
        self.assertNotIn("script", page.tags)
        self.assertIn("sample.md", page.links)
        self.assertIn("./", page.links)
        self.assertEqual(len([u for u in page.links if u.startswith("https://github.com/")]), 10)
        for href in page.links:
            parts = urlsplit(href)
            if not parts.scheme and not parts.netloc and parts.path:
                self.assertTrue((path.parent / parts.path).exists(), f"Missing local link: {href}")


if __name__ == "__main__":
    unittest.main()
