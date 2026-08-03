import json
import os
import re
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = Path(os.environ.get("REGISTRY_PATH", ROOT.parent / "registry")).resolve()
sys.path.insert(0, str(ROOT / "tools"))

from build import build


class LinkCollector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if tag == "a" and values.get("href"):
            self.links.append(values["href"])


class VisibleTextCollector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []
        self.skip_depth = 0

    def handle_starttag(self, tag, attrs):
        if tag in {"script", "style", "code", "pre"}:
            self.skip_depth += 1

    def handle_endtag(self, tag):
        if tag in {"script", "style", "code", "pre"} and self.skip_depth:
            self.skip_depth -= 1

    def handle_data(self, data):
        if not self.skip_depth:
            self.parts.append(data)

    @property
    def text(self):
        return "".join(self.parts)


class SiteArchitectureTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.out = Path(self.tmp.name) / "dist"
        build(REGISTRY, self.out)

    def tearDown(self):
        self.tmp.cleanup()

    def read(self, relative_path: str) -> str:
        return (self.out / relative_path).read_text(encoding="utf-8")

    def test_required_bilingual_routes_exist(self):
        routes = [
            "index.html",
            "manifesto/index.html",
            "concepts/index.html",
            "services/index.html",
            "standard/index.html",
            "evidence/index.html",
            "faq/index.html",
            "analytics/index.html",
            "zh-tw/index.html",
            "zh-tw/manifesto/index.html",
            "zh-tw/concepts/index.html",
            "zh-tw/services/index.html",
            "zh-tw/standard/index.html",
            "zh-tw/evidence/index.html",
            "zh-tw/faq/index.html",
            "zh-tw/analytics/index.html",
        ]
        for route in routes:
            with self.subTest(route=route):
                self.assertTrue((self.out / route).is_file())

    def test_language_pairs_are_self_canonical_and_cross_linked(self):
        en = self.read("manifesto/index.html")
        zh = self.read("zh-tw/manifesto/index.html")
        self.assertIn('rel="canonical" href="https://smallgreen-site-9pi.pages.dev/manifesto/"', en)
        self.assertIn('hreflang="zh-Hant-TW" href="https://smallgreen-site-9pi.pages.dev/zh-tw/manifesto/"', en)
        self.assertIn('rel="canonical" href="https://smallgreen-site-9pi.pages.dev/zh-tw/manifesto/"', zh)
        self.assertIn('hreflang="en" href="https://smallgreen-site-9pi.pages.dev/manifesto/"', zh)
        self.assertIn('href="/zh-tw/manifesto/"', en)
        self.assertIn('href="/manifesto/"', zh)

    def test_services_use_canonical_directory_routes_with_legacy_redirects(self):
        self.assertTrue((self.out / "services" / "sink" / "index.html").is_file())
        self.assertTrue((self.out / "zh-tw" / "services" / "sink" / "index.html").is_file())
        legacy = self.read("s/sink.html")
        self.assertIn('url=/services/sink/', legacy.lower())
        self.assertIn('rel="canonical" href="https://smallgreen-site-9pi.pages.dev/services/sink/"', legacy)

    def test_shared_assets_are_local_and_present(self):
        self.assertTrue((self.out / "assets" / "site.css").is_file())
        self.assertTrue((self.out / "assets" / "site.js").is_file())
        home = self.read("index.html")
        self.assertIn('href="/assets/site.css"', home)
        self.assertIn('src="/assets/site.js"', home)
        self.assertNotRegex(home, r'<(?:script|img)[^>]+(?:src)="https?://')
        self.assertNotRegex(home, r'<link[^>]+href="https?://[^\"]+\.(?:css|woff2?)')

    def test_forced_title_lines_are_scoped_to_chinese(self):
        css = self.read("assets/site.css")
        self.assertNotRegex(css, r"(?m)^\.hero-title-line\s*\{[^}]*white-space:\s*nowrap")
        self.assertNotRegex(css, r"(?m)^\.title-line\s*\{[^}]*white-space:\s*nowrap")
        self.assertRegex(css, r":lang\(zh-Hant\) \.hero-title-line\s*\{[^}]*white-space:\s*nowrap")

    def test_cloud_standard_palette_tokens_are_canonical(self):
        css = self.read("assets/site.css").lower()
        expected = {
            "--paper": "#f7f8f6",
            "--moss-surface": "#eef1ed",
            "--forest-ink": "#17201b",
            "--fern": "#176b4d",
            "--cloud-blue": "#235fa4",
            "--sprout": "#3f8a62",
            "--mineral": "#b7791f",
            "--dry-moss-line": "#ccd3ce",
        }
        for token, value in expected.items():
            with self.subTest(token=token):
                self.assertIn(f"{token}: {value};", css)

    def test_mobile_article_grid_allows_long_technical_content_to_shrink(self):
        css = self.read("assets/site.css")
        self.assertRegex(
            css,
            r"\.article-layout\s*\{[^}]*grid-template-columns:\s*minmax\(0,\s*1fr\)",
        )
        self.assertRegex(
            css,
            r"\.fact\s*\{[^}]*grid-template-columns:\s*8rem\s+minmax\(0,\s*1fr\)",
        )
        self.assertRegex(css, r"\.fact dd\s*\{[^}]*overflow-wrap:\s*anywhere")

    def test_machine_outputs_use_new_service_urls_and_list_languages(self):
        cards = json.loads(self.read("cards.json"))
        self.assertEqual(cards["languages"], ["en", "zh-Hant-TW"])
        self.assertEqual(cards["cards"][0]["url"].split("/services/")[0], "https://smallgreen-site-9pi.pages.dev")
        llms = self.read("llms.txt")
        self.assertIn("/services/", llms)
        sitemap = self.read("sitemap.xml")
        self.assertIn("/zh-tw/", sitemap)
        self.assertIn("hreflang", sitemap)

    def test_all_html_has_no_template_residue(self):
        for path in self.out.rglob("*.html"):
            text = path.read_text(encoding="utf-8")
            with self.subTest(path=path.relative_to(self.out)):
                self.assertNotIn("{{", text)
                self.assertNotIn("{%", text)
                self.assertEqual(len(re.findall(r"<main(?:\s|>)", text)), 1)

    def test_internal_page_links_resolve(self):
        for path in self.out.rglob("*.html"):
            parser = LinkCollector()
            parser.feed(path.read_text(encoding="utf-8"))
            for href in parser.links:
                if not href.startswith("/") or href.startswith("//"):
                    continue
                clean = href.split("#", 1)[0].split("?", 1)[0]
                if not clean or clean in ("/cards.json", "/llms.txt", "/sitemap.xml"):
                    continue
                target = self.out / clean.strip("/")
                target = target / "index.html" if clean.endswith("/") else target
                with self.subTest(source=path.relative_to(self.out), href=href):
                    self.assertTrue(target.is_file())

    def test_xml_and_crawler_policy_are_well_formed(self):
        ET.parse(self.out / "sitemap.xml")
        ET.parse(self.out / "feed.xml")
        robots = self.read("robots.txt")
        self.assertRegex(robots, r"User-agent: OAI-SearchBot\nAllow: /")
        self.assertRegex(robots, r"User-agent: GPTBot\nDisallow: /")
        self.assertIn("Allow: /concepts/", robots)

    def test_zh_visible_copy_uses_layout_instead_of_prose_punctuation(self):
        forbidden = re.compile(r"[。，；：！？]")
        for path in (self.out / "zh-tw").rglob("*.html"):
            parser = VisibleTextCollector()
            parser.feed(path.read_text(encoding="utf-8"))
            with self.subTest(path=path.relative_to(self.out)):
                self.assertNotRegex(parser.text, forbidden)

        home = self.read("zh-tw/index.html")
        self.assertIn('<span class="hero-title-line">我們正在建立小型軟體</span>', home)
        self.assertIn('<span class="hero-title-line">的所有權與部署層</span>', home)
        self.assertIn('<span class="title-line">依證據選擇</span>', home)
        self.assertIn('<span class="title-line">不依承諾選擇</span>', home)

    def test_concept_pages_include_complete_aeo_structure(self):
        page = self.read("concepts/small-software/index.html")
        for heading in (
            "Direct answer", "Why it matters", "Scope", "Out of scope",
            "How it works", "Example", "Machine-readable references",
            "Evidence and limitations", "Related concepts", "Version",
        ):
            with self.subTest(heading=heading):
                self.assertIn(f">{heading}<", page)

    def test_evidence_index_and_service_pages_publish_sanitized_screenshots(self):
        evidence = self.read("evidence/index.html")
        self.assertIn("evidence-index", evidence)
        self.assertIn('/assets/evidence/', evidence)
        service = self.read("services/sink/index.html")
        self.assertIn('class="service-screenshot"', service)
        self.assertTrue(any((self.out / "assets" / "evidence").glob("*.png")))

    def test_analytics_policy_is_public_bilingual_and_machine_readable(self):
        self.assertTrue((self.out / "analytics-policy.json").is_file())
        policy = json.loads(self.read("analytics-policy.json"))
        self.assertEqual(policy["tracking_scope"], "aggregate-only")
        self.assertFalse(policy["cookies"])
        self.assertFalse(policy["user_identifiers"])
        self.assertIn("Cloudflare Web Analytics", self.read("analytics/index.html"))
        self.assertIn("Cloudflare Web Analytics", self.read("zh-tw/analytics/index.html"))

    def test_cloudflare_pages_security_redirects_and_not_found_outputs(self):
        headers = self.read("_headers")
        self.assertIn("Content-Security-Policy:", headers)
        self.assertIn("static.cloudflareinsights.com", headers)
        self.assertIn("X-Content-Type-Options: nosniff", headers)
        redirects = self.read("_redirects")
        self.assertIn("/s/sink.html /services/sink/ 301", redirects)
        not_found = self.read("404.html")
        self.assertIn("Page not found", not_found)
        self.assertIn("找不到頁面", not_found)

    def test_feed_has_discovery_link(self):
        home = self.read("index.html")
        self.assertIn('type="application/atom+xml" href="/feed.xml"', home)


if __name__ == "__main__":
    unittest.main()
