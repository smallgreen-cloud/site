import hashlib
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


class HeadingCollector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.headings = []
        self._tag = None
        self._parts = []

    def handle_starttag(self, tag, attrs):
        if tag in {"h1", "h2", "h3"}:
            self._tag = tag
            self._parts = []

    def handle_data(self, data):
        if self._tag:
            self._parts.append(data)

    def handle_endtag(self, tag):
        if tag == self._tag:
            self.headings.append("".join(self._parts).strip())
            self._tag = None
            self._parts = []


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
        self.assertIn('rel="canonical" href="https://smallgreen-site.pages.dev/manifesto/"', en)
        self.assertIn('hreflang="zh-Hant-TW" href="https://smallgreen-site.pages.dev/zh-tw/manifesto/"', en)
        self.assertIn('rel="canonical" href="https://smallgreen-site.pages.dev/zh-tw/manifesto/"', zh)
        self.assertIn('hreflang="en" href="https://smallgreen-site.pages.dev/manifesto/"', zh)
        self.assertIn('href="/zh-tw/manifesto/"', en)
        self.assertIn('href="/manifesto/"', zh)

    def test_services_use_canonical_directory_routes_with_legacy_redirects(self):
        self.assertTrue((self.out / "services" / "sink" / "index.html").is_file())
        self.assertTrue((self.out / "zh-tw" / "services" / "sink" / "index.html").is_file())
        legacy = self.read("s/sink.html")
        self.assertIn('url=/services/sink/', legacy.lower())
        self.assertIn('rel="canonical" href="https://smallgreen-site.pages.dev/services/sink/"', legacy)

    def test_first_party_onboarding_pages_are_public_but_separate_from_verified_cards(self):
        for project_id, name in (("homebox-edge", "HomeBox Edge"), ("kb-vault", "Free Second Brain"), ("meeting-capture-kit", "Meeting Capture Kit")):
            for prefix in ("", "zh-tw/"):
                page = self.read(f"{prefix}services/{project_id}/index.html")
                self.assertIn(name, page)
                self.assertIn("onboarding", page.lower())
        services = self.read("services/index.html")
        self.assertIn("HomeBox Edge", services)
        self.assertIn("Free Second Brain", services)

    def test_service_cards_explain_the_project_and_show_architecture(self):
        cards = json.loads(self.read("cards.json"))["cards"]
        for card in cards:
            with self.subTest(card=card["id"]):
                summary = card["product_summary"]
                for field in ("project_type", "problem", "audience", "capabilities", "limitations", "deployment_requirements"):
                    self.assertTrue(summary[field]["zh-tw"])
                    self.assertTrue(summary[field]["en"])
                for prefix in ("", "zh-tw/"):
                    page = self.read(f"{prefix}services/{card['id']}/index.html")
                    self.assertIn("這是什麼專案" if prefix else "What is this project", page)
                    self.assertIn("解決什麼問題" if prefix else "What problem does it solve", page)
                    self.assertIn("適合誰" if prefix else "Who it is for", page)
                    self.assertIn("可以做什麼" if prefix else "What it can do", page)
                    self.assertIn('class="architecture"', page)

    def test_first_party_onboarding_uses_the_same_product_summary_and_architecture_contract(self):
        onboarding = json.loads(self.read("cards.json"))["onboarding"]
        for project in onboarding:
            with self.subTest(project=project["id"]):
                summary = project["product_summary"]
                for field in ("project_type", "problem", "audience", "capabilities", "limitations", "deployment_requirements"):
                    self.assertTrue(summary[field]["zh-tw"])
                    self.assertTrue(summary[field]["en"])
                self.assertTrue(project["architecture"]["cloudflare"])
                for prefix in ("", "zh-tw/"):
                    page = self.read(f"{prefix}services/{project['id']}/index.html")
                    self.assertIn('class="product-summary"', page)
                    self.assertIn('class="architecture"', page)

    def test_research_cases_are_public_but_separate_from_verified_cards_and_onboarding(self):
        data = json.loads(self.read("cards.json"))
        research = data["research_cases"]
        self.assertEqual(len(research), 33)
        self.assertIn("cloud-mail", [item["id"] for item in research])
        self.assertIn("upptime", [item["id"] for item in research])
        self.assertIn("foreclosure-map", [item["id"] for item in research])
        self.assertIn("audio-notes-sites", [item["id"] for item in research])
        ids = {item["id"] for item in data["cards"] + data["onboarding"]}
        self.assertTrue(ids.isdisjoint(item["id"] for item in research))
        for prefix in ("", "zh-tw/"):
            page = self.read(f"{prefix}services/cloud-mail/index.html")
            self.assertIn("Not a verified service" if not prefix else "這不是已驗證服務", page)
            self.assertIn("class=\"research-note\"", page)
            self.assertIn("class=\"architecture\"", page)
        services = self.read("services/index.html")
        self.assertIn("Research-stage candidates", services)
        self.assertIn("First-party onboarding", services)
        self.assertIn("14 CATALOGUED", services)
        self.assertNotIn("14 VERIFIED", services)

    def test_shared_assets_are_local_and_present(self):
        self.assertTrue((self.out / "assets" / "site.css").is_file())
        self.assertTrue((self.out / "assets" / "site.js").is_file())
        home = self.read("index.html")
        css_hash = hashlib.sha256((self.out / "assets" / "site.css").read_bytes()).hexdigest()[:12]
        js_hash = hashlib.sha256((self.out / "assets" / "site.js").read_bytes()).hexdigest()[:12]
        self.assertIn(f'href="/assets/site.css?v={css_hash}"', home)
        self.assertIn(f'src="/assets/site.js?v={js_hash}"', home)
        self.assertNotRegex(home, r'<(?:script|img)[^>]+(?:src)="https?://')
        self.assertNotRegex(home, r'<link[^>]+href="https?://[^\"]+\.(?:css|woff2?)')

    def test_home_pages_include_bing_site_verification(self):
        verification = '<meta name="msvalidate.01" content="3F053D60DF41C4723BAD4DEB0195890B">'
        self.assertIn(verification, self.read("index.html"))
        self.assertIn(verification, self.read("zh-tw/index.html"))

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
        self.assertIn("positioning", cards)
        self.assertIn("service directory and standard", cards["positioning"]["en"]["definition"])
        self.assertIn("服務目錄與標準", cards["positioning"]["zh-Hant-TW"]["definition"])
        self.assertEqual(cards["cards"][0]["url"].split("/services/")[0], "https://smallgreen-site.pages.dev")
        self.assertEqual([item["id"] for item in cards["onboarding"]], ["homebox-edge", "kb-vault", "meeting-capture-kit"])
        self.assertTrue(all(item["url"].startswith("https://smallgreen-site.pages.dev/services/") for item in cards["onboarding"]))
        self.assertEqual(len(cards["research_cases"]), 33)
        self.assertTrue(all(item["url"].startswith("https://smallgreen-site.pages.dev/services/") for item in cards["research_cases"]))
        llms = self.read("llms.txt")
        self.assertIn("/services/", llms)
        self.assertIn("Audience:", llms)
        self.assertIn("Problem:", llms)
        self.assertIn("First-party onboarding", llms)
        self.assertIn("Research cases", llms)
        llms_full = self.read("llms-full.txt")
        self.assertIn("## Positioning", llms_full)
        self.assertIn("First-party onboarding", llms_full)
        self.assertIn("Meeting Capture Kit", llms_full)
        self.assertIn("Research cases", llms_full)
        self.assertIn("Upptime", llms_full)
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
        self.assertIn('<span class="hero-title-line">從開源小型專案</span>', home)
        self.assertIn('<span class="hero-title-line">找到自己能運行的服務</span>', home)
        self.assertNotIn("中小企業", home)
        self.assertIn('<span class="title-line">先看專案本身</span>', home)
        self.assertIn('<span class="title-line">再看部署方式</span>', home)

    def test_all_heading_levels_omit_prose_punctuation(self):
        forbidden = re.compile(r"[。，；：！？.!?,;:]")
        for path in self.out.rglob("*.html"):
            parser = HeadingCollector()
            parser.feed(path.read_text(encoding="utf-8"))
            for heading in parser.headings:
                with self.subTest(path=path.relative_to(self.out), heading=heading):
                    self.assertNotRegex(heading, forbidden)

    def test_authored_title_lines_have_complete_semantic_edges(self):
        forbidden_edges = {"的", "與", "和", "或", "而", "及", "之"}
        for relative in ("zh-tw/index.html", "zh-tw/manifesto/index.html", "zh-tw/standard/index.html"):
            html = self.read(relative)
            lines = re.findall(r'<span class="(?:hero-)?title-line">([^<]+)</span>', html)
            for line in lines:
                with self.subTest(path=relative, line=line):
                    self.assertNotIn(line[0], forbidden_edges)
                    self.assertNotIn(line[-1], forbidden_edges)

    def test_concept_pages_include_complete_aeo_structure(self):
        index = self.read("concepts/index.html")
        for marker in ("concept-path", "concept-stage", "Is the purpose and scope bounded", "Can you maintain move or remove the service and its data", "Pass condition", "Check"):
            with self.subTest(marker=marker):
                self.assertIn(marker, index)
        manifesto = self.read("manifesto/index.html")
        for marker in ("manifesto-purpose-grid", "principles-list", "Own the running service", "Our publication rule"):
            with self.subTest(marker=marker):
                self.assertIn(marker, manifesto)
        self.assertNotIn('<p class="kicker">Mission</p><h3>Mission</h3>', manifesto)
        page = self.read("concepts/small-software/index.html")
        for heading in (
            "Why it matters", "Scope", "Out of scope",
            "How it works", "Example", "Machine-readable references",
            "Evidence and limitations", "Related concepts", "Version",
        ):
            with self.subTest(heading=heading):
                self.assertIn(f">{heading}<", page)

    def test_homepage_stays_at_the_catalogue_level(self):
        for relative in ("index.html", "zh-tw/index.html"):
            home = self.read(relative)
            with self.subTest(relative=relative):
                self.assertIn("service-index", home)
                self.assertIn("home-trust", home)
                self.assertNotIn("onboarding-section", home)
                self.assertNotIn("research-section", home)
                self.assertNotIn("05 /", home)
                self.assertNotIn("06 /", home)

    def test_homepage_states_the_new_positioning_before_technical_terms(self):
        for relative in ("index.html", "zh-tw/index.html"):
            home = self.read(relative)
            with self.subTest(relative=relative):
                self.assertIn('class="hero-definition"', home)
                self.assertIn("SmallGreen", home)
                self.assertIn("service directory" if relative == "index.html" else "服務目錄與標準", home)
                self.assertNotIn("Deployment Contract", home)

    def test_zh_faq_answers_preserve_sentence_boundaries_and_meaning(self):
        faq = self.read("zh-tw/faq/index.html")
        self.assertIn(
            "不會代管</span><span class=\"faq-line\">服務會運行在你自己的帳號</span>"
            "<span class=\"faq-line\">SmallGreen 會公開部署契約、Adapter 與驗證證據",
            faq,
        )
        self.assertNotIn("不會服務運行", faq)
        self.assertNotIn("SmallGreen 公開契約、Adapter", faq)
        self.assertIn("\"text\": \"不會代管 服務會運行在你自己的帳號 SmallGreen 會公開部署契約、Adapter 與驗證證據\"", faq)

    def test_zh_display_cleanup_does_not_merge_sentences(self):
        from build import clean_zh_display_copy

        self.assertIn("第一句　第二句", clean_zh_display_copy("第一句。第二句"))

    def test_public_about_label_uses_plain_language(self):
        en = self.read("manifesto/index.html")
        zh = self.read("zh-tw/manifesto/index.html")
        self.assertIn(">About<", en)
        self.assertIn("ABOUT SMALLGREEN", en)
        self.assertNotIn(">Manifesto<", en)
        self.assertIn("關於 SmallGreen", zh)
        self.assertNotIn(">宣言<", zh)

    def test_concept_copy_uses_ownership_language_correctly(self):
        page = self.read("zh-tw/concepts/ownership-and-deployment-layer/index.html")
        self.assertIn("所有權僅限於使用者帳號內的部署與資料", page)
        self.assertNotIn("所有權限於使用者帳號內", page)

    def test_zh_public_copy_uses_project_terms_and_not_legacy_labels(self):
        for path in self.out.glob("zh-tw/**/index.html"):
            html = path.read_text(encoding="utf-8")
            visible = VisibleTextCollector()
            visible.feed(html)
            with self.subTest(path=path):
                self.assertNotIn("宣言", visible.text)
                self.assertNotIn("Manifesto", visible.text)
                self.assertNotIn("運營", visible.text)
                self.assertNotIn("所有權限於", visible.text)

    def test_service_index_leads_with_project_purpose_and_audience(self):
        for relative in ("services/index.html", "zh-tw/services/index.html"):
            page = self.read(relative)
            with self.subTest(relative=relative):
                self.assertIn("service-audience", page)
                self.assertIn("Find a project you can run yourself" if relative == "services/index.html" else "找一個自己能運行的開源小型專案", page)
                self.assertIn("Catalogued" if relative == "services/index.html" else "已收錄", page)

    def test_service_detail_separates_decision_information_from_operations(self):
        for relative in ("services/sink/index.html", "zh-tw/services/sink/index.html"):
            page = self.read(relative)
            with self.subTest(relative=relative):
                self.assertIn("DECIDE FIRST" if relative == "services/sink/index.html" else "部署前先判斷", page)
                self.assertIn("Before you deploy" if relative == "services/sink/index.html" else "部署前要準備什麼", page)
                self.assertIn("How it runs" if relative == "services/sink/index.html" else "怎麼運行", page)
                self.assertIn("Where it runs and what it touches" if relative == "services/sink/index.html" else "在哪裡運行、會碰到什麼資料", page)

    def test_research_architecture_declares_its_actual_source(self):
        for prefix in ("", "zh-tw/"):
            page = self.read(f"{prefix}services/cloud-mail/index.html")
            with self.subTest(prefix=prefix):
                self.assertIn("research-stage" if not prefix else "研究階段架構", page.lower())
                self.assertIn("metadata", page.lower())
                self.assertNotIn("依部署契約機械生成", page)

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

    def test_browser_qa_base_url_is_a_cli_argument_not_an_undeclared_environment_variable(self):
        qa_script = (ROOT / "tools" / "qa_browser.js").read_text(encoding="utf-8")
        workflow = (ROOT / ".github" / "workflows" / "site.yml").read_text(encoding="utf-8")
        self.assertNotIn("process.env.QA_BASE_URL", qa_script)
        self.assertIn("npm run qa:browser -- http://127.0.0.1:8765", workflow)

    def test_public_artifact_scan_allows_commit_shas_but_rejects_generic_tokens(self):
        workflow = (ROOT / ".github" / "workflows" / "site.yml").read_text(encoding="utf-8")
        self.assertIn(r"(?![0-9a-fA-F]{40}\b)", workflow)
        token_pattern = re.compile(r"\b(?![0-9a-fA-F]{40}\b)[A-Za-z0-9_-]{40}\b")
        self.assertIsNone(token_pattern.search("b7345422e2f63e815c4a8e27fefdbcf27e5d81d6"))
        self.assertIsNotNone(token_pattern.search("Z" * 40))

    def test_cloudflare_deploy_runs_only_after_main_ci_with_repository_secrets(self):
        workflow = (ROOT / ".github" / "workflows" / "site.yml").read_text(encoding="utf-8")
        self.assertIn("uses: actions/upload-artifact@v4", workflow)
        self.assertIn("uses: actions/download-artifact@v4", workflow)
        self.assertIn("needs: [conformance, build]", workflow)
        self.assertIn("github.ref == 'refs/heads/main'", workflow)
        self.assertIn("apiToken: ${{ secrets.CLOUDFLARE_API_TOKEN }}", workflow)
        self.assertIn("accountId: ${{ secrets.CLOUDFLARE_ACCOUNT_ID }}", workflow)
        self.assertIn("pages deploy dist --project-name=smallgreen-site --branch=main", workflow)


if __name__ == "__main__":
    unittest.main()
