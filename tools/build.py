#!/usr/bin/env python3
"""Build the bilingual SmallGreen static site from Registry YAML.

Source ownership:
- Registry YAML owns service facts.
- site_content.py owns canonical editorial copy and translations.
- This renderer validates, escapes and emits deterministic static artifacts.
"""
import argparse
import hashlib
import json
import re
import shutil
from html import escape
from pathlib import Path
from urllib.parse import quote

import yaml

from gen_arch_svg import arch_svg
from site_content import BRAND, CONCEPT_DETAILS, CONCEPT_GUIDE, CONCEPTS, FAQ, HOME, LANGS, MANIFESTO, NAV, POSITIONING, STATIC_PAGES


DEFAULT_BASE_URL = "https://smallgreen-site.pages.dev"
SOURCE_ASSETS = Path(__file__).resolve().parent.parent / "assets"
LEVEL_LABEL = {
    "en": {"discovered": "Discovered", "community-verified": "Community Verified", "smallgreen-ready": "SmallGreen Ready"},
    "zh-tw": {"discovered": "Discovered", "community-verified": "Community Verified", "smallgreen-ready": "SmallGreen Ready"},
}
MAINT_LABEL = {
    "en": {"active": "Active", "slowing": "Slowing", "stalled": "Stalled", "archived": "Archived", "revived": "Revived"},
    "zh-tw": {"active": "維護中", "slowing": "更新趨緩", "stalled": "久未更新", "archived": "已封存", "revived": "復活維護"},
}
ONBOARDING_LABEL = {
    "en": "First-party onboarding",
    "zh-tw": "自有專案上架清單",
}
RESEARCH_LABEL = {
    "en": "Research cases",
    "zh-tw": "研究中案例",
}


def text(value) -> str:
    return escape(str(value), quote=True)


def title_lines(lines: list, class_name: str = "title-line") -> str:
    return "".join(f'<span class="{class_name}">{text(line)}</span>' for line in lines)


def asset_url(filename: str) -> str:
    """Return a content-versioned URL so new HTML never reuses stale CSS or JS."""
    digest = hashlib.sha256((SOURCE_ASSETS / filename).read_bytes()).hexdigest()[:12]
    return f"/assets/{filename}?v={digest}"


def clean_zh_display_copy(html: str) -> str:
    """Website display copy uses layout rhythm instead of prose punctuation.

    This operates on the final zh-Hant document so Registry-sourced editorial
    strings follow the same presentation rule without mutating Registry facts.
    Technical ASCII in URLs, versions, code and identifiers remains unchanged.
    Code elements are machine-facing and must preserve all punctuation exactly.
    """
    replacements = {"。": "　", "，": "　", "；": "　", "：": " ", "！": "", "？": ""}
    segments = re.split(r"(<code\b[^>]*>.*?</code>)", html, flags=re.DOTALL | re.IGNORECASE)
    for index in range(0, len(segments), 2):
        for punctuation, replacement in replacements.items():
            segments[index] = segments[index].replace(punctuation, replacement)
    return "".join(segments)


def clean_base_url(value: str) -> str:
    value = value.rstrip("/")
    if not value.startswith(("http://", "https://")):
        raise ValueError("base_url must start with http:// or https://")
    return value


def language_code(lang: str) -> str:
    return "zh-Hant" if lang == "zh-tw" else "en"


def route(lang: str, path: str = "") -> str:
    path = path.strip("/")
    prefix = "/zh-tw" if lang == "zh-tw" else ""
    return f"{prefix}/{path}/" if path else f"{prefix}/"


def paired_route(lang: str, path: str) -> str:
    return route("zh-tw" if lang == "en" else "en", path)


def output_path(out: Path, url_path: str) -> Path:
    return out / url_path.strip("/") / "index.html" if url_path != "/" else out / "index.html"


def write_page(out: Path, url_path: str, html: str) -> None:
    dest = output_path(out, url_path)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(html, encoding="utf-8")


def nav_html(lang: str, active: str, current_path: str) -> str:
    labels = NAV[lang]
    items = []
    for key in ("manifesto", "concepts", "services", "standard", "evidence", "faq"):
        current = ' aria-current="page"' if active == key else ""
        items.append(f'<a href="{route(lang, key)}"{current}>{text(labels[key])}</a>')
    other = paired_route(lang, current_path)
    return f"""
<header class="site-header">
  <nav class="nav-shell" aria-label="{'主要導覽' if lang == 'zh-tw' else 'Primary navigation'}">
    <a class="brand" href="{route(lang)}"><span class="brand-mark" aria-hidden="true"></span>{BRAND}</a>
    <div class="nav-links">{''.join(items)}</div>
    <a class="language-link" href="{other}" lang="{'en' if lang == 'zh-tw' else 'zh-Hant'}">{text(labels['language'])}</a>
  </nav>
</header>"""


def footer_html(lang: str) -> str:
    copy = ("Open-source projects. Clear deployment. Your account."
            if lang == "en" else "開源專案、清楚部署、自己的帳號。")
    return f"""
<footer class="site-footer">
  <div class="shell footer-grid">
    <p>{text(copy)}<br>Documents CC BY 4.0 · Code Apache-2.0</p>
    <div class="footer-links">
      <a href="/cards.json">cards.json</a><a href="/llms.txt">llms.txt</a>
      <a href="{route(lang, 'analytics')}">{'Analytics policy' if lang == 'en' else '分析政策'}</a>
      <a href="/sitemap.xml">sitemap.xml</a><a href="https://github.com/smallgreen-cloud">GitHub</a>
    </div>
  </div>
</footer>"""


def layout(*, lang: str, active: str, path: str, title: str, description: str,
           body: str, base_url: str, jsonld=None) -> str:
    canonical_path = route(lang, path)
    counterpart = paired_route(lang, path)
    canonical = f"{base_url}{canonical_path}"
    alternate = f"{base_url}{counterpart}"
    en_url = canonical if lang == "en" else alternate
    zh_url = canonical if lang == "zh-tw" else alternate
    structured = ""
    if jsonld:
        jsonld_text = json.dumps(jsonld, ensure_ascii=False).replace("</", "<\\/")
        structured = f'<script type="application/ld+json">{jsonld_text}</script>'
    bing_verification = (
        '<meta name="msvalidate.01" content="3F053D60DF41C4723BAD4DEB0195890B">'
        if path == "" else ""
    )
    html = f"""<!doctype html>
<html lang="{language_code(lang)}"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
{bing_verification}
<title>{text(title)} — {BRAND}</title>
<meta name="description" content="{text(description[:160])}">
<link rel="canonical" href="{canonical}">
<link rel="alternate" hreflang="en" href="{en_url}">
<link rel="alternate" hreflang="zh-Hant-TW" href="{zh_url}">
<link rel="alternate" hreflang="x-default" href="{en_url}">
<link rel="alternate" type="application/atom+xml" href="/feed.xml" title="{BRAND} updates">
<meta name="author" content="{BRAND} maintainers">
<meta property="og:title" content="{text(title)} — {BRAND}">
<meta property="og:description" content="{text(description[:160])}">
<meta property="og:type" content="website"><meta property="og:url" content="{canonical}">
<meta name="twitter:card" content="summary">
<link rel="stylesheet" href="{asset_url('site.css')}">
{structured}</head><body>
<a class="skip-link" href="#main">{'跳至主要內容' if lang == 'zh-tw' else 'Skip to content'}</a>
{nav_html(lang, active, path)}
<main id="main">{body}</main>
{footer_html(lang)}
<script src="{asset_url('site.js')}" defer></script>
</body></html>
"""
    return clean_zh_display_copy(html) if lang == "zh-tw" else html


def sort_cards(cards: list) -> list:
    return sorted(sorted(cards, key=lambda c: c["id"]),
                  key=lambda c: c["verification"].get("last_verified", ""), reverse=True)


def load_registry(registry: Path) -> tuple:
    card_paths = sorted((registry / "cards").glob("*.yaml"))
    if not card_paths:
        raise ValueError(f"no cards found in {registry / 'cards'}")
    cards = [yaml.safe_load(path.read_text(encoding="utf-8")) for path in card_paths]
    translation_path = registry / "translations" / "en.yaml"
    if not translation_path.is_file():
        raise ValueError("missing Registry translations/en.yaml")
    translations = yaml.safe_load(translation_path.read_text(encoding="utf-8")).get("services", {})
    missing = sorted({card["id"] for card in cards} - set(translations))
    if missing:
        raise ValueError(f"missing Registry English translations: {', '.join(missing)}")
    for card in cards:
        localized = translations[card["id"]]
        if not all(isinstance(localized.get(field), str) and localized[field].strip()
                   for field in ("one_liner", "data_flow")):
            raise ValueError(f"invalid Registry English translation: {card['id']}")
        summary = card.get("product_summary")
        required_summary = ("project_type", "problem", "audience", "capabilities",
                            "deployment_requirements", "limitations")
        if not isinstance(summary, dict) or any(
                not isinstance(summary.get(field), dict)
                or not summary[field].get("en")
                or not summary[field].get("zh-tw")
                for field in required_summary):
            raise ValueError(f"invalid Registry product_summary: {card['id']}")
        card["_i18n"] = {"en": localized}
    taxonomy = yaml.safe_load((registry / "taxonomy.yaml").read_text(encoding="utf-8"))["categories"]
    return sort_cards(cards), taxonomy


def load_onboarding(registry: Path) -> list:
    """Load transparent first-party candidates without mixing them into verified cards."""
    path = registry / "onboarding" / "first-party.yaml"
    if not path.is_file():
        return []
    doc = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    projects = doc.get("projects", [])
    if not isinstance(projects, list):
        raise ValueError("Registry onboarding projects must be a list")
    required = {"id", "name", "state", "state_label", "product_summary", "architecture", "current_stage", "next_steps"}
    for project in projects:
        missing = sorted(required - set(project))
        if missing:
            raise ValueError(f"onboarding project {project.get('id', 'unknown')} missing: {', '.join(missing)}")
        summary = project["product_summary"]
        required_summary = ("project_type", "problem", "audience", "capabilities",
                            "deployment_requirements", "limitations")
        if not isinstance(summary, dict) or any(
                not isinstance(summary.get(field), dict)
                or not summary[field].get("en")
                or not summary[field].get("zh-tw")
                for field in required_summary):
            raise ValueError(f"onboarding project {project['id']} needs bilingual product_summary")
        architecture = project["architecture"]
        if not isinstance(architecture, dict) or not architecture.get("cloudflare"):
            raise ValueError(f"onboarding project {project['id']} needs architecture.cloudflare")
        for field in ("current_stage", "next_steps"):
            if not isinstance(project[field], dict) or not project[field].get("en") or not project[field].get("zh-tw"):
                raise ValueError(f"onboarding project {project['id']} needs en and zh-tw {field}")
    return projects


def load_research_cases(registry: Path) -> list:
    """Load research-stage candidates without presenting them as verified cards."""
    path = registry / "candidates" / "research-cases.yaml"
    if not path.is_file():
        return []
    doc = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    projects = doc.get("projects", [])
    if not isinstance(projects, list):
        raise ValueError("Registry research cases must be a list")
    required = {"id", "name", "axis", "state", "state_label", "source", "product_summary",
                "architecture", "current_stage", "next_steps"}
    required_summary = ("project_type", "problem", "audience", "capabilities",
                        "deployment_requirements", "limitations")
    source_fields = ("repository", "license", "default_branch", "last_push", "checked_on")
    for project in projects:
        missing = sorted(required - set(project))
        if missing:
            raise ValueError(f"research case {project.get('id', 'unknown')} missing: {', '.join(missing)}")
        if project["state"] != "content-research":
            raise ValueError(f"research case {project['id']} must use state content-research")
        if not isinstance(project["state_label"], dict) or not project["state_label"].get("en") or not project["state_label"].get("zh-tw"):
            raise ValueError(f"research case {project['id']} needs bilingual state_label")
        summary = project["product_summary"]
        if not isinstance(summary, dict) or any(
                not isinstance(summary.get(field), dict)
                or not summary[field].get("en")
                or not summary[field].get("zh-tw")
                or any(not isinstance(summary[field][lang], (str, list)) for lang in ("en", "zh-tw"))
                for field in required_summary):
            raise ValueError(f"research case {project['id']} needs bilingual product_summary")
        for field in ("audience", "capabilities", "deployment_requirements", "limitations"):
            if any(not isinstance(summary[field][lang], list) or not summary[field][lang] for lang in ("en", "zh-tw")):
                raise ValueError(f"research case {project['id']} needs bilingual list summary for {field}")
        source = project["source"]
        if not isinstance(source, dict) or any(not source.get(field) for field in source_fields):
            raise ValueError(f"research case {project['id']} needs source repository metadata")
        architecture = project["architecture"]
        if not isinstance(architecture, dict) or not (architecture.get("cloudflare") or architecture.get("github")):
            raise ValueError(f"research case {project['id']} needs Cloudflare or GitHub architecture data")
        for field in ("current_stage", "next_steps"):
            if not isinstance(project[field], dict) or not project[field].get("en") or not project[field].get("zh-tw"):
                raise ValueError(f"research case {project['id']} needs en and zh-tw {field}")
        if any(not isinstance(project["next_steps"][lang], list) or not project["next_steps"][lang]
               for lang in ("en", "zh-tw")):
            raise ValueError(f"research case {project['id']} needs bilingual next_steps lists")
        install = project.get("agent_install")
        if install is not None:
            required_install = {"protocol", "status", "deployment_ready", "contract_url", "trigger",
                                "target", "hosting", "runtime_setup", "blockers"}
            missing_install = sorted(required_install - set(install)) if isinstance(install, dict) else sorted(required_install)
            if missing_install:
                raise ValueError(f"research case {project['id']} agent_install missing: {', '.join(missing_install)}")
            if install["protocol"] != "smallgreen-install/v1":
                raise ValueError(f"research case {project['id']} uses an unsupported install protocol")
            if install["status"] != "candidate" or install["deployment_ready"] is not False:
                raise ValueError(f"research case {project['id']} cannot claim a ready install while it remains research-stage")
            if not isinstance(install["blockers"], list) or not install["blockers"]:
                raise ValueError(f"research case {project['id']} candidate install needs blockers")
            if install["target"] != {"client": "chatgpt-work", "hosting": "sites", "execution_mode": "native-sites"}:
                raise ValueError(f"research case {project['id']} install target must be native ChatGPT Work Sites")
            hosting = install["hosting"]
            if hosting.get("managed_resources") != ["site", "d1", "r2"] or hosting.get("external_infrastructure") != []:
                raise ValueError(f"research case {project['id']} install must use only Sites-managed site, D1 and R2")
            runtime = install["runtime_setup"]
            if (runtime.get("name"), runtime.get("timing"), runtime.get("entry_channel"), runtime.get("chat_handling")) != (
                    "GROQ_API_KEY", "after-deploy", "application-ui", "forbidden"):
                raise ValueError(f"research case {project['id']} Groq key must be entered after deploy in the application UI")
            if any(not isinstance(install["trigger"].get(lang), str) or not install["trigger"][lang].strip()
                   for lang in ("en", "zh-tw")):
                raise ValueError(f"research case {project['id']} install trigger must be bilingual")
            if not re.fullmatch(r"https://raw\.githubusercontent\.com/[\w.-]+/[\w.-]+/[0-9a-f]{40}/\.smallgreen/install\.yaml",
                                install["contract_url"]):
                raise ValueError(f"research case {project['id']} install contract URL must pin a GitHub commit")
    return projects


def service_copy(card: dict, lang: str) -> str:
    return card["_i18n"]["en"]["one_liner"] if lang == "en" else card["one_liner"]


def audience_copy(item: dict, lang: str) -> str:
    audience = item["product_summary"]["audience"][lang]
    if isinstance(audience, list):
        return ", ".join(audience) if lang == "en" else "、".join(audience)
    return str(audience)


def tag_row(card: dict, lang: str) -> str:
    verification = card["verification"]
    level = LEVEL_LABEL[lang][verification["level"]]
    grade = text(card["free_tier_grade"])
    maintained = MAINT_LABEL[lang][card["maintenance_status"]]
    return (f'<span class="tag">{text(level)}</span>'
            f'<span class="tag grade-{grade.lower()}">{"Budget" if lang == "en" else "資源預算"} {grade}</span>'
            f'<span class="tag">{text(maintained)}</span>')


def service_rows(cards: list, lang: str, limit=None) -> str:
    rows = []
    for card in cards[:limit] if limit else cards:
        verified = card["verification"].get("last_verified", "—")
        rows.append(f"""
<a class="service-row" href="{route(lang, 'services/' + card['id'])}">
  <span class="service-name">{text(card['name'])}</span>
  <span class="service-purpose">{text(service_copy(card, lang))}</span>
  <span class="service-audience"><strong>{'適合' if lang == 'zh-tw' else 'For'}</strong> {text(audience_copy(card, lang))}</span>
  <span class="service-meta">{tag_row(card, lang)}<span>{text(verified)}</span></span>
</a>""")
    return '<div class="service-index">' + "".join(rows) + "</div>"


def onboarding_copy(project: dict, field: str, lang: str):
    return project[field][lang]


def summary_copy(item: dict, field: str, lang: str):
    return item["product_summary"][field][lang]


def product_summary_body(item: dict, lang: str) -> str:
    labels = {
        "project_type": ("What is this project", "這是什麼專案"),
        "problem": ("What problem does it solve", "解決什麼問題"),
        "audience": ("Who it is for", "適合誰"),
        "capabilities": ("What it can do", "可以做什麼"),
        "deployment_requirements": ("Before you deploy", "部署前要準備什麼"),
        "limitations": ("What to know first", "開始前要知道的限制"),
    }
    blocks = []
    for field in ("project_type", "problem"):
        label = labels[field][0 if lang == "en" else 1]
        blocks.append(f'<section class="summary-block summary-core"><h2>{text(label)}</h2><p>{text(summary_copy(item, field, lang))}</p></section>')
    for field in ("audience", "capabilities", "deployment_requirements", "limitations"):
        label = labels[field][0 if lang == "en" else 1]
        values = summary_copy(item, field, lang)
        values = values if isinstance(values, list) else [values]
        items = "".join(f"<li>{text(value)}</li>" for value in values)
        block_class = "summary-core" if field in ("audience", "capabilities") else "summary-operations"
        blocks.append(f'<section class="summary-block {block_class}"><h2>{text(label)}</h2><ul>{items}</ul></section>')
    summary_label = "DECIDE FIRST" if lang == "en" else "部署前先判斷"
    return f'<section class="product-summary" aria-label="{text(summary_label)}"><p class="summary-label">{text(summary_label)}</p><div class="summary-grid">' + "".join(blocks) + "</div></section>"


def onboarding_architecture(project: dict) -> dict:
    return {
        "id": project["id"],
        "name": project["name"],
        "components": {"cloudflare": project["architecture"]["cloudflare"]},
        "data_flow": {"external_services": project["architecture"].get("external_services", [])},
    }


def onboarding_rows(projects: list, lang: str) -> str:
    rows = []
    for project in projects:
        audience = "、".join(summary_copy(project, "audience", lang)) if lang == "zh-tw" else ", ".join(summary_copy(project, "audience", lang))
        rows.append(f'''
<a class="onboarding-card" href="{route(lang, 'services/' + project['id'])}">
  <span class="onboarding-state">{text(project['state_label'][lang])}</span>
  <h3>{text(project['name'])}</h3>
  <p class="onboarding-type">{text(summary_copy(project, 'project_type', lang))}</p>
  <p class="onboarding-purpose">{text(summary_copy(project, 'problem', lang))}</p>
  <p class="onboarding-audience"><strong>{'適合' if lang == 'zh-tw' else 'For'}</strong> {text(audience)}</p>
  <span class="onboarding-link">{'查看上架進度 →' if lang == 'zh-tw' else 'View onboarding status →'}</span>
</a>''')
    return '<div class="onboarding-grid">' + "".join(rows) + "</div>"


def research_case_architecture(project: dict) -> dict:
    return {
        "id": project["id"],
        "name": project["name"],
        "components": {
            "cloudflare": project["architecture"].get("cloudflare", []),
            "github": project["architecture"].get("github", []),
        },
        "data_flow": {"external_services": project["architecture"].get("external_services", [])},
    }


def research_rows(projects: list, lang: str, limit=None) -> str:
    rows = []
    for project in projects[:limit] if limit else projects:
        audience = "、".join(summary_copy(project, "audience", lang)) if lang == "zh-tw" else ", ".join(summary_copy(project, "audience", lang))
        source = project["source"]
        rows.append(f'''
<article class="research-card">
  <div class="research-meta"><span class="research-state">{text(project['state_label'][lang])}</span><span>{text(source['license'])}</span><span>{text(project['axis'])}</span></div>
  <h3><a href="{route(lang, 'services/' + project['id'])}">{text(project['name'])}</a></h3>
  <p class="research-type">{text(summary_copy(project, 'project_type', lang))}</p>
  <p class="research-purpose">{text(summary_copy(project, 'problem', lang))}</p>
  <p class="research-audience"><strong>{'適合' if lang == 'zh-tw' else 'For'}</strong> {text(audience)}</p>
  <figure class="architecture-compact">{arch_svg(research_case_architecture(project), compact=True, provenance="research")}<figcaption>{'依研究階段架構 metadata 生成的草圖' if lang == 'zh-tw' else 'Sketch generated from research-stage architecture metadata'}</figcaption></figure>
  <p class="research-upstream"><a href="https://github.com/{text(source['repository'])}">{text(source['repository'])}</a><br>{'查看研究卡 →' if lang == 'zh-tw' else 'View research case →'}</p>
</article>''')
    return '<div class="research-grid">' + "".join(rows) + "</div>"


def _legacy_home_body(cards: list, lang: str, onboarding: list, research_cases: list) -> str:
    c = HOME[lang]
    flow = (["Understand the project", "Declare the deployment", "Run it in your account", "Verify the exit"]
            if lang == "en" else ["理解專案", "說清楚部署", "在自己的帳號運行", "驗證退場"])
    trust = ([
        ("Machine-verifiable", "Schemas and validators decide whether a contract is valid."),
        ("No phone-home", "The standard forbids hidden telemetry in verified projects."),
        ("Exit is tested", "Teardown and resource-zero checks are part of the evidence trail."),
    ] if lang == "en" else [
        ("機器可驗", "Schema 與 Validator 判定契約是否成立。"),
        ("不含 phone-home", "標準禁止已驗證專案加入隱藏遙測。"),
        ("退場也要驗收", "Teardown 與資源歸零是證據的一部分。"),
    ])
    trust_html = "".join(f'<article class="trust-panel"><h3>{text(a)}</h3><p>{text(b)}</p></article>' for a, b in trust)
    flow_html = "".join(f"<li>{text(item)}</li>" for item in flow)
    onboarding_block = ""
    if onboarding:
        onboarding_block = f'''
<section class="section onboarding-section"><div class="shell"><div class="section-head"><div><p class="kicker">05 / {text(ONBOARDING_LABEL[lang])}</p><h2>{title_lines(["先看懂，再部署" if lang == "zh-tw" else "Understand it before you deploy"])}</h2></div><p class="section-intro">{'這些自有專案已經有可用產品形狀，正在補齊公開契約與驗證證據。' if lang == 'zh-tw' else 'These first-party projects already have a usable product shape and are now completing public contracts and evidence.'}</p></div>{onboarding_rows(onboarding, lang)}</div></section>'''
    research_block = ""
    if research_cases:
        research_block = f'''
<section class="section research-section"><div class="shell"><div class="section-head"><div><p class="kicker">06 / {text(RESEARCH_LABEL[lang])}</p><h2>{title_lines(["先整理案例，再進驗證" if lang == "zh-tw" else "Map the cases before verification"])}</h2></div><p class="section-intro">{'這些案例已依上游 README 與 metadata 整理成可讀研究卡　但尚未完成部署契約與 Evidence。' if lang == 'zh-tw' else 'These cases are mapped from upstream READMEs and metadata, but deployment contracts and Evidence are not complete yet.'}</p></div>{research_rows(research_cases, lang, limit=6)}<div class="actions"><a class="button" href="{route(lang, 'services')}">{'查看全部研究中案例' if lang == 'zh-tw' else 'View all research cases'} →</a></div></div></section>'''
    return f"""
<section class="hero"><div class="shell hero-grid">
  <div class="hero-copy"><p class="kicker">{text(c['eyebrow'])}</p><h1>{title_lines(c.get('title_lines', [c['title']]), 'hero-title-line')}</h1>
  <p class="hero-lede">{text(c['lede'])}</p>
  <div class="actions"><a class="button primary" href="{route(lang, 'services')}">{text(c['primary'])}</a>
  <a class="button" href="{route(lang, 'standard')}">{text(c['secondary'])} →</a></div></div>
  <aside class="hero-system" aria-label="{'Trust path' if lang == 'en' else '信任路徑'}"><ol class="system-flow">{flow_html}</ol></aside>
</div></section>
<section class="section"><div class="shell"><div class="section-head"><div><p class="kicker">{text(c['how_label'])}</p><h2>{''.join(f'<span class="title-line">{text(line)}</span>' for line in c['how_title_lines'])}</h2></div>
<p class="section-intro">{text('The guide and the judge are deliberately separated' if lang == 'en' else '引導者與裁判刻意分離　避免 Agent 自我宣告成功')}</p></div>
<div class="trust-path">{''.join(f'<article class="path-step"><b>0{i}</b><h3>{text(item)}</h3><p>{text(desc)}</p></article>' for i, (item, desc) in enumerate(([("Service Card", "A clear view for people"), ("Contract", "Structured facts for Agents"), ("Agent", "A guide through deployment"), ("Evidence", "A machine-checked public trail")] if lang == "en" else [("服務卡", "給人的清楚說明"), ("部署契約", "給 Agent 的結構化事實"), ("Agent", "引導部署流程"), ("驗證證據", "機械檢核的公開軌跡")]), 1))}</div>
</div></section>
<section class="section"><div class="shell"><div class="section-head"><div><p class="kicker">{text(c['services_label'])}</p><h2>{title_lines(c.get('services_title_lines', [c['services_title']]))}</h2></div><p class="section-intro">{text(c['services_text'])}</p></div>
{service_rows(cards, lang, limit=6)}<div class="actions"><a class="button" href="{route(lang, 'services')}">{text('View all services' if lang == 'en' else '查看全部服務')} →</a></div></div></section>
{onboarding_block}
{research_block}
    <section class="section"><div class="shell"><div class="section-head"><div><p class="kicker">{text(c['trust_label'])}</p><h2>{title_lines(c.get('trust_title_lines', [c['trust_title']]))}</h2></div><p class="section-intro">{text(c['trust_text'])}</p></div><div class="trust-grid">{trust_html}</div></div></section>
"""


def home_body(cards: list, lang: str, onboarding: list, research_cases: list) -> str:
    """首頁依序回答：SmallGreen 是什麼、如何判斷、從哪裡開始。"""
    c = HOME[lang]
    flow = ([
        ("What does it solve", "Purpose and audience"),
        ("What does it need", "Data and deployment"),
        ("Can you keep control", "Evidence and exit"),
    ] if lang == "en" else [
        ("它要解決什麼", "用途與適合對象"),
        ("它需要什麼", "資料與部署方式"),
        ("能不能自己掌握", "證據與退場方式"),
    ])
    flow_html = "".join(
        f'<li><span class="system-flow-copy"><strong>{text(title)}</strong><span>{text(description)}</span></span></li>'
        for title, description in flow
    )
    trust_html = "".join(
        f'<article class="trust-panel"><h3>{text(title)}</h3><p>{text(description)}</p></article>'
        for title, description in c["trust_items"]
    )
    return f"""
<section class="hero"><div class="shell hero-grid">
  <div class="hero-copy"><p class="kicker">{text(c['eyebrow'])}</p><h1>{title_lines(c['title_lines'], 'hero-title-line')}</h1>
  <p class="hero-definition"><span>{text(c['definition_label'])}</span>{text(c['definition'])}</p>
  <p class="hero-lede">{text(c['lede'])}</p>
  <div class="actions"><a class="button primary" href="{route(lang, 'services')}">{text(c['primary'])}</a>
  <a class="button" href="{route(lang, c['secondary_path'])}">{text(c['secondary'])} →</a></div></div>
  <aside class="hero-system" aria-label="{'Ownership path' if lang == 'en' else '服務所有權路徑'}"><ol class="system-flow">{flow_html}</ol></aside>
</div></section>
<section class="section home-trust"><div class="shell"><div class="section-head"><div><p class="kicker">{text(c['how_label'])}</p><h2>{title_lines(c['how_title_lines'])}</h2></div>
<p class="section-intro">{text(c['how_text'])}</p></div><div class="trust-grid">{trust_html}</div>
</div></section>
<section class="section"><div class="shell"><div class="section-head"><div><p class="kicker">{text(c['services_label'])}</p><h2>{title_lines(c['services_title_lines'])}</h2></div><p class="section-intro">{text(c['services_text'])}</p></div>
{service_rows(cards, lang, limit=3)}<div class="actions"><a class="button" href="{route(lang, 'services')}">{text('View all services' if lang == 'en' else '查看全部服務')} →</a>
<a class="button" href="{route(lang, 'concepts')}">{text('Read the six questions' if lang == 'en' else '閱讀六個判斷問題')} →</a></div></div></section>
"""


def static_page_body(page: dict, lang: str) -> str:
    blocks = "".join(f'<section class="content-block"><h2>{text(title)}</h2><p>{text(body)}</p></section>'
                     for title, body in page["sections"])
    return f"""
<header class="page-hero"><div class="shell"><p class="kicker">{text(page['label'])}</p><h1 class="page-title">{title_lines(page.get('title_lines', [page['title']]))}</h1><p class="page-lede">{text(page['lede'])}</p></div></header>
<section class="section"><div class="shell"><div class="content-grid">{blocks}</div></div></section>"""


def manifesto_body(lang: str) -> str:
    manifesto = MANIFESTO[lang]
    mission_label, mission = manifesto["mission"]
    vision_label, vision = manifesto["vision"]
    principles = "".join(
        f'''<article class="principle-row"><span class="principle-number">{index:02}</span><div><h3>{text(title)}</h3><p>{text(body)}</p></div></article>'''
        for index, (title, body) in enumerate(manifesto["principles"], 1)
    )
    practice = "".join(
        f'''<article><p class="kicker">{text(title)}</p><p>{text(body)}</p></article>'''
        for title, body in manifesto["practice"]
    )
    purpose_intro = ("SmallGreen exists to close the gap between code and a service you can run."
                     if lang == "en" else "SmallGreen 要補上程式碼與可運行服務之間的空白")
    principles_intro = ("These commitments define what SmallGreen will make visible."
                        if lang == "en" else "這些承諾定義 SmallGreen 必須公開的內容")
    practice_intro = ("About SmallGreen becomes real in what we publish and what we refuse to claim."
                      if lang == "en" else "SmallGreen 會落實在我們公開什麼　以及拒絕宣稱什麼")
    return f'''
<header class="page-hero manifesto-hero"><div class="shell"><p class="kicker">{text(manifesto["label"])}</p><h1 class="page-title">{title_lines(manifesto["title_lines"])}</h1><p class="page-lede">{text(manifesto["lede"])}</p></div></header>
<section class="section manifesto-purpose"><div class="shell"><div class="section-head"><div><p class="kicker">01 / {text("PURPOSE" if lang == "en" else "目的")}</p><h2>{title_lines(["What we are making possible"] if lang == "en" else ["讓開源專案", "成為自己的服務"])}</h2></div><p class="section-intro">{text(purpose_intro)}</p></div><div class="manifesto-purpose-grid"><article><h3>{text(mission_label)}</h3><p>{text(mission)}</p></article><article><h3>{text(vision_label)}</h3><p>{text(vision)}</p></article></div></div></section>
<section class="section manifesto-principles"><div class="shell"><div class="section-head"><div><p class="kicker">02 / {text(manifesto["principles_label"])}</p><h2>{title_lines(["Three commitments" if lang == "en" else "三個承諾"])}</h2></div><p class="section-intro">{text(principles_intro)}</p></div><div class="principles-list">{principles}</div></div></section>
<section class="section manifesto-practice"><div class="shell"><div class="section-head"><div><p class="kicker">03 / {text(manifesto["practice_label"])}</p><h2>{title_lines(["Make the promise observable" if lang == "en" else "讓承諾可以被看見"])}</h2></div><p class="section-intro">{text(practice_intro)}</p></div><div class="manifesto-practice-grid">{practice}</div><div class="actions"><a class="button primary" href="{route(lang, 'concepts')}">{text("See the six questions" if lang == "en" else "查看六個判斷問題")} →</a></div></div></section>'''


def concepts_index_body(lang: str) -> str:
    guide = CONCEPT_GUIDE[lang]
    stages = []
    number = 0
    for label, heading, intro, items in guide["stages"]:
        rows = []
        for slug, question, condition, evidence in items:
            number += 1
            concept_heading, _ = CONCEPTS[slug][lang]
            rows.append(f'''
<a class="concept-row" href="{route(lang, f"concepts/{slug}")}"><span class="concept-number">{number:02}</span><div class="concept-question"><span class="concept-name">{text(concept_heading)}</span><h3>{text(question)}</h3></div><div class="concept-check"><p><strong>{text(guide['pass_label'])}</strong> {text(condition)}</p><p><strong>{text(guide['evidence_label'])}</strong> {text(evidence)}</p></div><span class="concept-arrow" aria-hidden="true">↗</span></a>''')
        stages.append(f'''
<section class="concept-stage"><div class="concept-stage-head"><p class="kicker">{text(label)}</p><h2>{text(heading)}</h2><p>{text(intro)}</p></div><div class="concept-list">{"".join(rows)}</div></section>''')
    return f'''<header class="page-hero concepts-hero"><div class="shell"><p class="kicker">{text(guide["label"])}</p><h1 class="page-title">{title_lines(guide["title_lines"])}</h1><p class="page-lede">{text(guide["lede"])}</p></div></header><section class="section concept-path"><div class="shell">{"".join(stages)}</div></section>'''


def concept_body(slug: str, lang: str) -> str:
    title, answer = CONCEPTS[slug][lang]
    section_labels = (["Why it matters", "Scope", "Out of scope", "How it works", "Example",
                       "Machine-readable references", "Evidence and limitations", "Related concepts", "Version"]
                      if lang == "en" else ["為何重要", "範圍", "不包含", "如何運作", "例子",
                                             "機器可讀參考", "證據與限制", "相關概念", "版本"])
    scope = ("A stable concept used by Service Cards, deployment contracts and the SmallGreen Spec."
             if lang == "en" else "供服務卡、部署契約與 SmallGreen Spec 共用的穩定概念。")
    out_scope = ("It is not a guarantee of security, permanence or universal compatibility."
                 if lang == "en" else "不代表安全、永久可用或通用相容性的保證。")
    refs = ('<a href="https://github.com/smallgreen-cloud/spec">SmallGreen Spec</a> · '
            '<a href="/cards.json">cards.json</a> · <a href="/llms.txt">llms.txt</a>')
    detail = CONCEPT_DETAILS[slug][lang]
    related = [key for key in CONCEPTS if key != slug][:3]
    related_html = " · ".join(
        f'<a href="{route(lang, "concepts/" + key)}">{text(CONCEPTS[key][lang][0])}</a>' for key in related
    )
    return f"""
<header class="page-hero"><div class="shell"><p class="kicker">CANONICAL CONCEPT</p><h1 class="page-title">{text(title)}</h1><p class="page-lede">{text(answer)}</p></div></header>
<section class="section"><div class="shell article-layout"><aside class="article-index">{BRAND}<br>Concept v1.0</aside><article class="prose">
<h2>{text(section_labels[0])}</h2><p>{text(detail['why'])}</p>
<h2>{text(section_labels[1])}</h2><p>{text(scope)}</p>
<h2>{text(section_labels[2])}</h2><p>{text(out_scope)}</p>
<h2>{text(section_labels[3])}</h2><p>{text(detail['how'])}</p>
<h2>{text(section_labels[4])}</h2><p>{text(detail['example'])}</p>
<h2>{text(section_labels[5])}</h2><p>{refs}</p>
<h2>{text(section_labels[6])}</h2><p>{text(detail['evidence'])}</p>
<h2>{text(section_labels[7])}</h2><p>{related_html}</p>
<h2>{text(section_labels[8])}</h2><p>Concept v1.0 · SmallGreen Spec v0.2.1</p>
</article></div></section>"""


def evidence_index_body(cards: list, lang: str) -> str:
    page = STATIC_PAGES["evidence"][lang]
    rows = []
    for card in cards:
        verification = card["verification"]
        packs = verification.get("evidence_packs", [])
        screenshot = card.get("_screenshot_url")
        image = (f'<img src="{screenshot}" alt="{text(card["name"])} verified service screenshot" '
                 'loading="lazy" width="1200" height="750">') if screenshot else '<div class="evidence-no-image">CONTRACT-ONLY SERVICE</div>'
        rows.append(f'''<article class="evidence-item">{image}<div class="evidence-item-copy">
<p class="kicker">{text(verification['level'])} · {text(verification.get('last_verified', '—'))}</p>
<h2><a href="{route(lang, 'services/' + card['id'])}">{text(card['name'])}</a></h2>
<p>{text(service_copy(card, lang))}</p>
<p class="evidence-count">{len(packs)} Evidence Pack · Spec {text(verification['spec_version'])}</p>
</div></article>''')
    return f'''<header class="page-hero"><div class="shell"><p class="kicker">{text(page['label'])}</p>
<h1 class="page-title">{title_lines(page.get('title_lines', [page['title']]))}</h1><p class="page-lede">{text(page['lede'])}</p></div></header>
<section class="section"><div class="shell"><div class="evidence-index">{"".join(rows)}</div></div></section>'''


def onboarding_detail_body(project: dict, lang: str) -> str:
    next_steps = "".join(f"<li>{text(item)}</li>" for item in onboarding_copy(project, "next_steps", lang))
    return f"""
<header class="page-hero"><div class="shell"><p class="kicker">FIRST-PARTY / ONBOARDING</p><h1 class="page-title">{text(project['name'])}</h1><p class="page-lede">{text(summary_copy(project, 'project_type', lang))}</p></div></header>
<section class="section"><div class="shell article-layout"><aside class="article-index"><span class="onboarding-state">{text(project['state_label'][lang])}</span><p>{text('自有專案' if lang == 'zh-tw' else 'First-party project')}</p></aside><article class="prose">
<div class="onboarding-note"><strong>{'這不是已驗證服務' if lang == 'zh-tw' else 'This is not a verified service yet'}</strong><p>{'目前公開的是產品用途與上架進度；驗證完成後才會進入正式服務卡與 Evidence 索引。' if lang == 'zh-tw' else 'This page publishes the product purpose and onboarding status. It will enter the verified service index only after evidence is complete.'}</p></div>
{product_summary_body(project, lang)}
<figure class="architecture">{arch_svg(onboarding_architecture(project), provenance="onboarding")}<figcaption>{"Architecture generated from onboarding project data." if lang == "en" else "依上架準備資料生成的架構圖。"}</figcaption></figure>
<h2>{'目前進度' if lang == 'zh-tw' else 'Current stage'}</h2><p>{text(onboarding_copy(project, 'current_stage', lang))}</p>
<h2>{'上架前待辦' if lang == 'zh-tw' else 'Before catalogue entry'}</h2><ul>{next_steps}</ul>
<p><a href="{route(lang, 'services')}">← {'回服務目錄' if lang == 'zh-tw' else 'Back to service index'}</a></p>
</article></div></section>"""


def research_detail_body(project: dict, lang: str) -> str:
    next_steps = "".join(f"<li>{text(item)}</li>" for item in project["next_steps"][lang])
    source = project["source"]
    warning = ("這不是已驗證服務　這是根據上游 README 與 metadata 整理的研究卡　部署契約、實際部署與 Evidence 尚未完成。"
               if lang == "zh-tw" else
               "This is not a verified service. It is a research card assembled from the upstream README and metadata. The deployment contract, live deployment and Evidence are not complete.")
    facts = [
        (("Upstream" if lang == "en" else "上游"), f'<a href="https://github.com/{text(source["repository"])}">{text(source["repository"])}</a>'),
        (("License" if lang == "en" else "授權"), text(source["license"])),
        (("Default branch" if lang == "en" else "預設分支"), text(source["default_branch"])),
        (("Last push" if lang == "en" else "最近推送"), text(source["last_push"])),
        (("Checked on" if lang == "en" else "資料核對日"), text(source["checked_on"])),
    ]
    facts_html = "".join(f'<div class="fact"><dt>{text(label)}</dt><dd>{value}</dd></div>' for label, value in facts)
    install = project.get("agent_install")
    install_html = ""
    if install:
        phrase = install["trigger"][lang]
        copied = "已複製" if lang == "zh-tw" else "Copied"
        copy_label = "複製" if lang == "zh-tw" else "Copy"
        title = "Agent 安裝契約" if lang == "zh-tw" else "Agent install contract"
        status = "候選契約" if lang == "zh-tw" else "Candidate contract"
        note = ("Work 可以讀取安裝契約，但這條路徑尚未完成全新帳戶驗收；不得回報 SmallGreen Ready。"
                if lang == "zh-tw" else
                "Work can read this install contract, but the fresh-account path is not verified yet and must not be reported as SmallGreen Ready.")
        contract_label = "查看原始安裝契約" if lang == "zh-tw" else "View source install contract"
        discovery_label = "機器可讀 install.json" if lang == "zh-tw" else "Machine-readable install.json"
        # The trigger is a machine-facing command. Preserve its punctuation exactly;
        # the prose formatter intentionally normalizes Chinese sentence punctuation.
        install_html = f'''<section class="agent-install candidate-install"><h2>{title}</h2><p><span class="research-state">{status}</span></p><p>{text(note)}</p><div class="command"><code id="research-agent-command">{escape(str(phrase))}</code><button class="copy-button" type="button" data-copy="research-agent-command" data-copied-label="{copied}">{copy_label}</button></div><p><a href="{text(install['contract_url'])}">{contract_label}</a> · <a href="/services/{text(project['id'])}/install.json">{discovery_label}</a></p></section>'''
    return f"""
<header class="page-hero"><div class="shell"><p class="kicker">RESEARCH CASE / {text(project['id'])}</p><h1 class="page-title">{text(project['name'])}</h1><p class="page-lede">{text(summary_copy(project, 'project_type', lang))}</p></div></header>
<section class="section"><div class="shell article-layout"><aside class="article-index"><span class="research-state">{text(project['state_label'][lang])}</span><p>{text('候選研究卡' if lang == 'zh-tw' else 'Research-stage candidate')}</p></aside><article class="prose">
<div class="research-note"><strong>{'這不是已驗證服務' if lang == 'zh-tw' else 'Not a verified service'}</strong><p>{text(warning)}</p></div>
{product_summary_body(project, lang)}
<figure class="architecture">{arch_svg(research_case_architecture(project), provenance="research")}<figcaption>{'依研究階段架構 metadata 生成　尚待部署驗證。' if lang == 'zh-tw' else 'Architecture generated from research-stage metadata; deployment verification is still pending.'}</figcaption></figure>
{install_html}
<h2>{'目前進度' if lang == 'zh-tw' else 'Current stage'}</h2><p>{text(project['current_stage'][lang])}</p>
<h2>{'上游資料' if lang == 'zh-tw' else 'Upstream facts'}</h2><dl class="facts">{facts_html}</dl>
<h2>{'下一步' if lang == 'zh-tw' else 'Next steps'}</h2><ul>{next_steps}</ul>
<p><a href="{route(lang, 'services')}">← {'回服務目錄' if lang == 'zh-tw' else 'Back to service index'}</a></p>
</article></div></section>"""


def services_index_body(cards: list, lang: str, onboarding: list, research_cases: list) -> str:
    title = "Find a project you can run yourself" if lang == "en" else "找一個自己能運行的開源小型專案"
    lede = ("Start with the problem and audience. Then compare deployment requirements, evidence and limits. The three layers below stay separate on purpose."
            if lang == "en" else "先看專案要解決什麼與適合誰　再比較部署前提 證據與限制　以下三個層級刻意分開。")
    pending = f'''<section class="section onboarding-section"><div class="shell"><div class="section-head"><div><p class="kicker">02 / {text(ONBOARDING_LABEL[lang])}</p><h2>{title_lines(["先看懂，再部署" if lang == "zh-tw" else "Understand it before you deploy"])}</h2></div><p class="section-intro">{'產品用途、目前能力與剩餘上架閘門公開列出。' if lang == 'zh-tw' else 'Purpose, current capability and remaining catalogue gates are public.'}</p></div>{onboarding_rows(onboarding, lang)}</div></section>''' if onboarding else ""
    research = f'''<section class="section research-section"><div class="shell"><div class="section-head"><div><p class="kicker">03 / {text(RESEARCH_LABEL[lang])} / {len(research_cases)}</p><h2>{title_lines(["研究中的候選案例" if lang == "zh-tw" else "Research-stage candidates"])}</h2></div><p class="section-intro">{'研究卡公開用途、適合對象、架構與上游資料　但不等同已上架或可直接部署。' if lang == 'zh-tw' else 'Research cards publish purpose, audience, architecture and upstream facts; they are not catalogue entries or deployment evidence.'}</p></div>{research_rows(research_cases, lang)}</div></section>''' if research_cases else ""
    catalogue_title = "已收錄服務" if lang == "zh-tw" else "Catalogue entries"
    catalogue_intro = "每列先說明專案用途與適合對象　再提供證據層級 資源等級與最近核對日。開啟服務卡可查看架構 部署前提 資料流與限制。" if lang == "zh-tw" else "Every row starts with purpose and audience, then shows evidence level, resource grade and verification date. Open the Service Card for architecture, requirements, data flow and limits."
    guide = ("<ul class=\"directory-guide\"><li><strong>Catalogued</strong> — published service cards with evidence.</li><li><strong>Onboarding</strong> — first-party projects being prepared.</li><li><strong>Research</strong> — upstream cases still being assessed.</li></ul>"
             if lang == "en" else "<ul class=\"directory-guide\"><li><strong>已收錄</strong>　有正式服務卡與公開證據。</li><li><strong>上架準備</strong>　SmallGreen 自有專案正在補齊資料。</li><li><strong>研究中</strong>　仍在評估上游案例　尚未完成驗證。</li></ul>")
    return f"""<header class="page-hero"><div class="shell"><p class="kicker">SERVICES / {len(cards)} CATALOGUED</p><h1 class="page-title">{text(title)}</h1><p class="page-lede">{text(lede)}</p>{guide}</div></header><section class="section"><div class="shell"><div class="section-head"><div><p class="kicker">01 / {text('已收錄服務' if lang == 'zh-tw' else 'CATALOGUED SERVICES')}</p><h2>{title_lines([catalogue_title])}</h2></div><p class="section-intro">{text(catalogue_intro)}</p></div>{service_rows(cards, lang)}</div></section>{pending}{research}"""


def service_jsonld(card: dict, lang: str, base_url: str) -> dict:
    return {
        "@context": "https://schema.org", "@type": "SoftwareApplication",
        "name": card["name"], "description": service_copy(card, lang),
        "url": f"{base_url}{route(lang, 'services/' + card['id'])}",
        "applicationCategory": "DeveloperApplication", "operatingSystem": "Cloudflare",
        "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"},
        "license": f"https://spdx.org/licenses/{quote(card['repo'].get('license', ''))}",
        "codeRepository": f"https://github.com/{card['repo']['upstream']}",
    }


def service_detail_body(card: dict, lang: str) -> str:
    verification = card["verification"]
    packs = verification.get("evidence_packs", [])
    externals = card.get("data_flow", {}).get("external_services", [])
    adapter = card["repo"].get("adapter")
    install = (f"Please follow https://github.com/{adapter}/AGENTS.md to deploy this service"
               if lang == "en" else f"請照 https://github.com/{adapter}/AGENTS.md 部署這個服務") if adapter else ""
    copied = "已複製" if lang == "zh-tw" else "Copied"
    copy_label = "複製" if lang == "zh-tw" else "Copy"
    disclosure = (card["_i18n"]["en"]["data_flow"] if lang == "en"
                  else card.get("data_flow", {}).get("disclosure", ""))
    ext_text = "、".join(externals) if externals else ("無" if lang == "zh-tw" else "None")
    pack_links = "".join(f'<li><a href="https://github.com/smallgreen-cloud/registry/blob/main/{text(pack)}">{text(Path(pack).name)}</a></li>' for pack in packs)
    facts = [
        (("Upstream" if lang == "en" else "上游"), f'<a href="https://github.com/{text(card["repo"]["upstream"])}">{text(card["repo"]["upstream"])}</a>'),
        (("License" if lang == "en" else "授權"), text(card["repo"].get("license", "—"))),
        (("Profile" if lang == "en" else "Profile"), text(card["profile"])),
        (("External services" if lang == "en" else "外部服務"), text(ext_text)),
        (("Data flow" if lang == "en" else "資料流"), text(disclosure)),
    ]
    facts_html = "".join(f'<div class="fact"><dt>{text(label)}</dt><dd>{value}</dd></div>' for label, value in facts)
    screenshot = card.get("_screenshot_url")
    screenshot_html = (f'<figure class="service-screenshot"><img src="{screenshot}" alt="{text(card["name"])} verified service screenshot" '
                       'loading="eager" width="1200" height="750"><figcaption>'
                       f'{"Screenshot referenced by the published Evidence Pack" if lang == "en" else "由公開 Evidence Pack 引用的真實服務截圖"}'
                       '</figcaption></figure>') if screenshot else ""
    return f"""
<header class="page-hero"><div class="shell"><p class="kicker">SERVICE CARD / {text(card['id'])}</p><h1 class="page-title">{text(card['name'])}</h1><p class="page-lede">{text(service_copy(card, lang))}</p></div></header>
<section class="section"><div class="shell article-layout"><aside class="article-index">{tag_row(card, lang)}</aside><article class="prose">
{product_summary_body(card, lang)}
<section class="evidence-strip" aria-label="{'What has been checked' if lang == 'en' else '已經檢查什麼'}"><p class="evidence-label">{'WHAT HAS BEEN CHECKED' if lang == 'en' else '已經檢查什麼'}</p><div class="evidence-status"><span class="pass">{text(LEVEL_LABEL[lang][verification['level']])}</span><span>{len(packs)} EVIDENCE</span><span>SPEC {text(verification['spec_version'])}</span><span>{text(verification.get('last_verified', '—'))}</span></div><div class="evidence-meta">{"Public evidence, scoped to this version and date." if lang == "en" else "公開證據僅適用於標示的版本與日期。"}</div></section>
<h2>{'How it runs' if lang == 'en' else '怎麼運行'}</h2>
{screenshot_html}
<figure class="architecture">{arch_svg(card)}<figcaption>{"Architecture generated from the Service Card data flow." if lang == "en" else "依服務卡資料流機械生成的架構圖。"}</figcaption></figure>
{f'<section class="agent-install"><h2>{"Give this to your Agent" if lang == "en" else "交給 Agent 安裝"}</h2><div class="command"><code id="agent-command">{text(install)}</code><button class="copy-button" type="button" data-copy="agent-command" data-copied-label="{copied}">{copy_label}</button></div></section>' if adapter else ''}
<h2>{"Where it runs and what it touches" if lang == "en" else "在哪裡運行、會碰到什麼資料"}</h2><dl class="facts">{facts_html}</dl>
<h2>{'Source evidence' if lang == 'en' else '原始證據'}</h2><ul>{pack_links or '<li>—</li>'}</ul>
<p><a href="{route(lang, 'services')}">← {"Back to service index" if lang == "en" else "回服務目錄"}</a></p>
</article></div></section>"""


def faq_body(lang: str) -> str:
    title = "Questions that should be answered before deployment" if lang == "en" else "部署前就應該回答的問題"
    items = "".join(
        f'<details><summary>{text(question)}</summary><p>{faq_answer_html(answer)}</p></details>'
        for question, answer in FAQ[lang]
    )
    return f'<header class="page-hero"><div class="shell"><p class="kicker">FAQ</p><h1 class="page-title">{text(title)}</h1></div></header><section class="section"><div class="shell prose">{items}</div></section>'


def faq_answer_lines(answer) -> list:
    return answer if isinstance(answer, list) else [answer]


def faq_answer_text(answer) -> str:
    return " ".join(str(line) for line in faq_answer_lines(answer))


def faq_answer_html(answer) -> str:
    return "".join(f'<span class="faq-line">{text(line)}</span>' for line in faq_answer_lines(answer))


def write_legacy_redirects(cards: list, out: Path, base_url: str) -> None:
    legacy = out / "s"
    legacy.mkdir(exist_ok=True)
    for card in cards:
        target = f"/services/{card['id']}/"
        canonical = f"{base_url}{target}"
        page = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta http-equiv="refresh" content="0; url={target}"><link rel="canonical" href="{canonical}"><title>Moved — {BRAND}</title></head><body><main><p>Moved to <a href="{target}">{target}</a>.</p></main></body></html>"""
        (legacy / f"{card['id']}.html").write_text(page, encoding="utf-8")


def write_cloudflare_outputs(cards: list, out: Path) -> None:
    csp = ("default-src 'self'; base-uri 'self'; object-src 'none'; frame-ancestors 'none'; "
           "form-action 'none'; img-src 'self' data:; style-src 'self'; font-src 'self'; "
           "script-src 'self' 'unsafe-inline' https://static.cloudflareinsights.com; "
           "connect-src 'self' https://cloudflareinsights.com; upgrade-insecure-requests")
    headers = f"""/*
  Content-Security-Policy: {csp}
  Referrer-Policy: strict-origin-when-cross-origin
  X-Content-Type-Options: nosniff
  X-Frame-Options: DENY
  Permissions-Policy: camera=(), microphone=(), geolocation=(), payment=(), usb=()
  Cross-Origin-Opener-Policy: same-origin

/assets/*
  Cache-Control: public, max-age=3600, must-revalidate
"""
    (out / "_headers").write_text(headers, encoding="utf-8")
    redirects = "".join(f"/s/{card['id']}.html /services/{card['id']}/ 301\n" for card in cards)
    (out / "_redirects").write_text(redirects, encoding="utf-8")
    not_found = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex"><title>Page not found — {BRAND}</title><link rel="stylesheet" href="{asset_url('site.css')}"></head><body><main id="main"><header class="page-hero"><div class="shell"><p class="kicker">404</p><h1 class="page-title">Page not found<br><span lang="zh-Hant">找不到頁面</span></h1><p class="page-lede">The requested path does not exist<br><span lang="zh-Hant">這個網址沒有對應內容</span></p><div class="actions"><a class="button primary" href="/">English home</a><a class="button" href="/zh-tw/">繁體中文首頁</a></div></div></header></main></body></html>"""
    (out / "404.html").write_text(not_found, encoding="utf-8")


def write_machine_outputs(cards: list, out: Path, base_url: str, canonical_routes: list,
                          onboarding: list, research_cases: list) -> None:
    public_cards = []
    for card in cards:
        item = {key: value for key, value in card.items() if not key.startswith("_")}
        item["url"] = f"{base_url}/services/{card['id']}/"
        item["translations"] = {
            "en": card["_i18n"]["en"],
            "zh-Hant-TW": {
                "one_liner": card["one_liner"],
                "data_flow": card.get("data_flow", {}).get("disclosure", ""),
            },
        }
        public_cards.append(item)
    public_onboarding = []
    for project in onboarding:
        item = {key: value for key, value in project.items() if not key.startswith("_")}
        item["url"] = f"{base_url}/services/{project['id']}/"
        public_onboarding.append(item)
    public_research = []
    for project in research_cases:
        item = {key: value for key, value in project.items() if not key.startswith("_")}
        item["url"] = f"{base_url}/services/{project['id']}/"
        public_research.append(item)
        install = project.get("agent_install")
        if install:
            install_dir = out / "services" / project["id"]
            install_dir.mkdir(parents=True, exist_ok=True)
            discovery = {
                **install,
                "service_card": f"{base_url}/services/{project['id']}/",
                "source": {
                    "repository": project["source"]["repository"],
                    "commit": project["source"].get("locked_commit"),
                    "license": project["source"]["license"],
                },
                "notice": "Candidate install discovery. Inspectable, not yet verified as SmallGreen Ready.",
            }
            (install_dir / "install.json").write_text(
                json.dumps(discovery, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
            )
    (out / "cards.json").write_text(json.dumps({
        "source": "https://github.com/smallgreen-cloud/registry",
        "spec": "https://github.com/smallgreen-cloud/spec",
        "languages": ["en", "zh-Hant-TW"],
        "positioning": {"en": POSITIONING["en"], "zh-Hant-TW": POSITIONING["zh-tw"]},
        "cards": public_cards,
        "onboarding": public_onboarding, "research_cases": public_research,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (out / "analytics-policy.json").write_text(json.dumps({
        "schema_version": "1.0", "tracking_scope": "aggregate-only", "cookies": False,
        "user_identifiers": False, "custom_events": False, "query_strings": False,
        "providers": ["Cloudflare Web Analytics", "Cloudflare Edge Analytics", "Cloudflare AI Crawl Control",
                      "Google Search Console", "Bing Webmaster"],
        "purpose": ["SEO measurement", "AEO measurement", "Core Web Vitals", "crawler governance"],
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    llms = [f"# {BRAND}", "", f"> {POSITIONING['en']['definition']}",
            f"Audience: {POSITIONING['en']['audience']}",
            f"Problem: {POSITIONING['en']['problem']}", "",
            "## Canonical resources", "", f"- [About]({base_url}/manifesto/)",
            f"- [Concepts]({base_url}/concepts/)", f"- [Services]({base_url}/services/)",
            f"- [Standard]({base_url}/standard/)", f"- [Evidence policy]({base_url}/evidence/)",
            f"- [Structured service cards]({base_url}/cards.json)", "", "## Services", ""]
    llms.extend(f"- [{card['name']}]({base_url}/services/{card['id']}/): {service_copy(card, 'en')}" for card in cards)
    if onboarding:
        llms.extend(["", "## First-party onboarding", ""])
        llms.extend(f"- [{project['name']}]({base_url}/services/{project['id']}/): {summary_copy(project, 'problem', 'en')}" for project in onboarding)
    if research_cases:
        llms.extend(["", "## Research cases", ""])
        llms.extend(f"- [{project['name']}]({base_url}/services/{project['id']}/): {summary_copy(project, 'problem', 'en')} [research-stage, not verified]" for project in research_cases)
    (out / "llms.txt").write_text("\n".join(llms) + "\n", encoding="utf-8")

    full = [f"# {BRAND} full service index", "", "## Positioning", "",
            f"- Definition: {POSITIONING['en']['definition']}",
            f"- Audience: {POSITIONING['en']['audience']}",
            f"- Problem: {POSITIONING['en']['problem']}", ""]
    for card in cards:
        v = card["verification"]
        full.extend([f"## {card['name']}", service_copy(card, "en"),
                     f"- URL: {base_url}/services/{card['id']}/",
                     f"- Upstream: https://github.com/{card['repo']['upstream']}",
                     f"- Verification: {v['level']}; Spec {v['spec_version']}; {v.get('last_verified', '—')}",
                     f"- Resource budget: {card['free_tier_grade']}", ""])
    if onboarding:
        full.extend(["## First-party onboarding", ""])
        for project in onboarding:
            full.extend([f"### {project['name']}", summary_copy(project, "problem", "en"),
                         f"- URL: {base_url}/services/{project['id']}/",
                         f"- Status: {project['state']}", ""])
    if research_cases:
        full.extend(["## Research cases", ""])
        for project in research_cases:
            source = project["source"]
            full.extend([f"### {project['name']}", summary_copy(project, "problem", "en"),
                         f"- URL: {base_url}/services/{project['id']}/",
                         f"- Upstream: https://github.com/{source['repository']}",
                         f"- Status: {project['state']} (not verified)",
                         f"- License: {source['license']}", ""])
    (out / "llms-full.txt").write_text("\n".join(full), encoding="utf-8")

    search_agents = ["OAI-SearchBot", "ChatGPT-User", "Claude-SearchBot", "Claude-User", "PerplexityBot"]
    training_agents = ["GPTBot", "Google-Extended", "CCBot", "Bytespider", "meta-externalagent"]
    robots = ["# Search and user-directed Agent access", "User-agent: *", "Allow: /", ""]
    for agent in search_agents:
        robots.extend([f"User-agent: {agent}", "Allow: /", ""])
    for agent in training_agents:
        robots.extend([f"User-agent: {agent}", "Disallow: /", "Allow: /manifesto/", "Allow: /concepts/",
                       "Allow: /standard/", "Allow: /faq/", "Allow: /zh-tw/manifesto/",
                       "Allow: /zh-tw/concepts/", "Allow: /zh-tw/standard/", "Allow: /zh-tw/faq/", ""])
    robots.append(f"Sitemap: {base_url}/sitemap.xml")
    (out / "robots.txt").write_text("\n".join(robots) + "\n", encoding="utf-8")

    pairs = []
    seen = set()
    for lang, path, lastmod in canonical_routes:
        pair_key = path
        if pair_key in seen:
            continue
        seen.add(pair_key)
        en = f"{base_url}{route('en', path)}"
        zh = f"{base_url}{route('zh-tw', path)}"
        modified = f"<lastmod>{lastmod}</lastmod>" if lastmod else ""
        pairs.append(f'<url><loc>{en}</loc>{modified}<xhtml:link rel="alternate" hreflang="en" href="{en}"/><xhtml:link rel="alternate" hreflang="zh-Hant-TW" href="{zh}"/></url>')
        pairs.append(f'<url><loc>{zh}</loc>{modified}<xhtml:link rel="alternate" hreflang="en" href="{en}"/><xhtml:link rel="alternate" hreflang="zh-Hant-TW" href="{zh}"/></url>')
    sitemap = ('<?xml version="1.0" encoding="UTF-8"?>\n'
               '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">'
               + "".join(pairs) + "</urlset>\n")
    (out / "sitemap.xml").write_text(sitemap, encoding="utf-8")

    feed_parts = []
    for card in cards:
        card_id = card["id"]
        updated = card["verification"].get("last_verified", "2026-08-03")
        feed_parts.append(
            f'<entry><title>{text(card["name"])}</title><id>{base_url}/services/{card_id}/</id>'
            f'<link href="{base_url}/services/{card_id}/"/><updated>{updated}T00:00:00Z</updated>'
            f'<summary>{text(service_copy(card, "en"))}</summary></entry>'
        )
    feed_items = "".join(feed_parts)
    feed_updated = max(card["verification"].get("last_verified", "2026-08-03") for card in cards)
    feed = (f'<?xml version="1.0" encoding="UTF-8"?><feed xmlns="http://www.w3.org/2005/Atom">'
            f'<title>{BRAND}</title><id>{base_url}/</id><updated>{feed_updated}T00:00:00Z</updated>'
            f'{feed_items}</feed>\n')
    (out / "feed.xml").write_text(feed, encoding="utf-8")


def build(registry: Path, out: Path, base_url: str = DEFAULT_BASE_URL) -> None:
    base_url = clean_base_url(base_url)
    cards, _taxonomy = load_registry(registry)
    onboarding = load_onboarding(registry)
    research_cases = load_research_cases(registry)
    verified_ids = {card["id"] for card in cards}
    onboarding = [project for project in onboarding if project["id"] not in verified_ids]
    reserved_ids = verified_ids | {project["id"] for project in onboarding}
    collisions = sorted(reserved_ids & {project["id"] for project in research_cases})
    if collisions:
        raise ValueError(f"research cases collide with published routes: {', '.join(collisions)}")
    out.mkdir(parents=True, exist_ok=True)
    assets = out / "assets"
    assets.mkdir(exist_ok=True)
    shutil.copyfile(SOURCE_ASSETS / "site.css", assets / "site.css")
    shutil.copyfile(SOURCE_ASSETS / "site.js", assets / "site.js")
    evidence_assets = assets / "evidence"
    for card in cards:
        screenshot = (card.get("images") or {}).get("screenshot")
        source = registry / screenshot["path"] if isinstance(screenshot, dict) and screenshot.get("path") else None
        if source and source.is_file():
            evidence_assets.mkdir(exist_ok=True)
            destination = evidence_assets / f"{card['id']}{source.suffix.lower()}"
            shutil.copyfile(source, destination)
            card["_screenshot_url"] = f"/assets/evidence/{destination.name}"

    canonical_routes = []
    website_jsonld = {"@context": "https://schema.org", "@type": "WebSite", "name": BRAND,
                      "url": f"{base_url}/", "description": POSITIONING["en"]["definition"]}
    for lang in LANGS:
        body = home_body(cards, lang, onboarding, research_cases)
        write_page(out, route(lang), layout(lang=lang, active="home", path="", title=HOME[lang]["title"],
                                                   description=HOME[lang]["meta_description"], body=body, base_url=base_url,
                                                   jsonld=website_jsonld))
        canonical_routes.append((lang, "", max(c["verification"].get("last_verified", "") for c in cards)))

        for slug, localized in STATIC_PAGES.items():
            page = MANIFESTO[lang] if slug == "manifesto" else localized[lang]
            page_body = (manifesto_body(lang) if slug == "manifesto" else
                         evidence_index_body(cards, lang) if slug == "evidence" else
                         static_page_body(page, lang))
            write_page(out, route(lang, slug), layout(lang=lang, active=slug, path=slug, title=page["title"],
                                                       description=page["lede"], body=page_body, base_url=base_url))
            canonical_routes.append((lang, slug, None))

        write_page(out, route(lang, "concepts"), layout(lang=lang, active="concepts", path="concepts",
                                                          title=("Concepts" if lang == "en" else "核心概念"),
                                                          description=("Canonical definitions for Small Software." if lang == "en" else "Small Software 的核心定義。"),
                                                          body=concepts_index_body(lang), base_url=base_url))
        canonical_routes.append((lang, "concepts", None))
        for slug, localized in CONCEPTS.items():
            heading, answer = localized[lang]
            path = f"concepts/{slug}"
            jsonld = {"@context": "https://schema.org", "@type": "DefinedTerm", "name": heading,
                      "description": answer, "url": f"{base_url}{route(lang, path)}"}
            write_page(out, route(lang, path), layout(lang=lang, active="concepts", path=path, title=heading,
                                                       description=answer, body=concept_body(slug, lang), base_url=base_url,
                                                       jsonld=jsonld))
            canonical_routes.append((lang, path, None))

        write_page(out, route(lang, "services"), layout(lang=lang, active="services", path="services",
                                                          title=("Find a project" if lang == "en" else "找一個專案"),
                                                          description=("Find open-source small projects you can understand and run yourself." if lang == "en" else "找一個看得懂 且能自己運行的開源小型專案。"),
                                                          body=services_index_body(cards, lang, onboarding, research_cases), base_url=base_url))
        canonical_routes.append((lang, "services", max(c["verification"].get("last_verified", "") for c in cards)))
        for card in cards:
            path = f"services/{card['id']}"
            write_page(out, route(lang, path), layout(lang=lang, active="services", path=path, title=card["name"],
                                                       description=service_copy(card, lang), body=service_detail_body(card, lang),
                                                       base_url=base_url, jsonld=service_jsonld(card, lang, base_url)))
            canonical_routes.append((lang, path, card["verification"].get("last_verified")))
        for project in onboarding:
            path = f"services/{project['id']}"
            write_page(out, route(lang, path), layout(lang=lang, active="services", path=path, title=project["name"],
                                                       description=summary_copy(project, "problem", lang),
                                                       body=onboarding_detail_body(project, lang), base_url=base_url))
            canonical_routes.append((lang, path, None))
        for project in research_cases:
            path = f"services/{project['id']}"
            write_page(out, route(lang, path), layout(lang=lang, active="services", path=path, title=project["name"],
                                                       description=summary_copy(project, "problem", lang),
                                                       body=research_detail_body(project, lang), base_url=base_url))
            canonical_routes.append((lang, path, project["source"].get("checked_on")))

        write_page(out, route(lang, "faq"), layout(lang=lang, active="faq", path="faq",
                                                     title=("Frequently asked questions" if lang == "en" else "常見問題"),
                                                     description=("Answers about ownership, verification and privacy." if lang == "en" else "關於所有權、驗證與隱私的回答。"),
                                                     body=faq_body(lang), base_url=base_url,
                                                     jsonld={"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
                                                         {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": faq_answer_text(a)}}
                                                         for q, a in FAQ[lang]]}))
        canonical_routes.append((lang, "faq", None))

    write_legacy_redirects(cards, out, base_url)
    write_cloudflare_outputs(cards, out)
    write_machine_outputs(cards, out, base_url, canonical_routes, onboarding, research_cases)
    print(f"built bilingual site: {len(cards)} catalogued services + {len(onboarding)} onboarding + {len(research_cases)} research cases, {len(CONCEPTS)} concepts, {len(list(out.rglob('*.html')))} HTML pages")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", required=True, type=Path)
    parser.add_argument("--out", type=Path, default=Path(__file__).resolve().parent.parent / "dist")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    args = parser.parse_args()
    build(args.registry, args.out, args.base_url)
