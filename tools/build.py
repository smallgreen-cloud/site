#!/usr/bin/env python3
"""Build the bilingual SmallGreen Cloud static site from Registry YAML.

Source ownership:
- Registry YAML owns service facts.
- site_content.py owns canonical editorial copy and translations.
- This renderer validates, escapes and emits deterministic static artifacts.
"""
import argparse
import json
import shutil
from html import escape
from pathlib import Path
from urllib.parse import quote

import yaml

from gen_arch_svg import arch_svg
from site_content import CONCEPT_DETAILS, CONCEPTS, FAQ, HOME, LANGS, NAV, STATIC_PAGES


DEFAULT_BASE_URL = "https://smallgreen-site-9pi.pages.dev"
LEVEL_LABEL = {
    "en": {"discovered": "Discovered", "community-verified": "Community Verified", "smallgreen-ready": "SmallGreen Ready"},
    "zh-tw": {"discovered": "Discovered", "community-verified": "Community Verified", "smallgreen-ready": "SmallGreen Ready"},
}
MAINT_LABEL = {
    "en": {"active": "Active", "slowing": "Slowing", "stalled": "Stalled", "archived": "Archived", "revived": "Revived"},
    "zh-tw": {"active": "維護中", "slowing": "更新趨緩", "stalled": "久未更新", "archived": "已封存", "revived": "復活維護"},
}


def text(value) -> str:
    return escape(str(value), quote=True)


def title_lines(lines: list, class_name: str = "title-line") -> str:
    return "".join(f'<span class="{class_name}">{text(line)}</span>' for line in lines)


def clean_zh_display_copy(html: str) -> str:
    """Website display copy uses layout rhythm instead of prose punctuation.

    This operates on the final zh-Hant document so Registry-sourced editorial
    strings follow the same presentation rule without mutating Registry facts.
    Technical ASCII in URLs, versions, code and identifiers remains unchanged.
    """
    replacements = {"。": "", "，": "　", "；": "　", "：": " ", "！": "", "？": ""}
    for punctuation, replacement in replacements.items():
        html = html.replace(punctuation, replacement)
    return html


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
    <a class="brand" href="{route(lang)}"><span class="brand-mark" aria-hidden="true"></span>SmallGreen Cloud</a>
    <div class="nav-links">{''.join(items)}</div>
    <a class="language-link" href="{other}" lang="{'en' if lang == 'zh-tw' else 'zh-Hant'}">{text(labels['language'])}</a>
  </nav>
</header>"""


def footer_html(lang: str) -> str:
    copy = ("Open standard. Public evidence. User-owned deployments."
            if lang == "en" else "開放標準、公開證據、使用者擁有部署。")
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
    html = f"""<!doctype html>
<html lang="{language_code(lang)}"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{text(title)} — SmallGreen Cloud</title>
<meta name="description" content="{text(description[:160])}">
<link rel="canonical" href="{canonical}">
<link rel="alternate" hreflang="en" href="{en_url}">
<link rel="alternate" hreflang="zh-Hant-TW" href="{zh_url}">
<link rel="alternate" hreflang="x-default" href="{en_url}">
<link rel="alternate" type="application/atom+xml" href="/feed.xml" title="SmallGreen Cloud updates">
<meta name="author" content="SmallGreen Cloud maintainers">
<meta property="og:title" content="{text(title)} — SmallGreen Cloud">
<meta property="og:description" content="{text(description[:160])}">
<meta property="og:type" content="website"><meta property="og:url" content="{canonical}">
<meta name="twitter:card" content="summary">
<link rel="stylesheet" href="/assets/site.css">
{structured}</head><body>
<a class="skip-link" href="#main">{'跳至主要內容' if lang == 'zh-tw' else 'Skip to content'}</a>
{nav_html(lang, active, path)}
<main id="main">{body}</main>
{footer_html(lang)}
<script src="/assets/site.js" defer></script>
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
        card["_i18n"] = {"en": localized}
    taxonomy = yaml.safe_load((registry / "taxonomy.yaml").read_text(encoding="utf-8"))["categories"]
    return sort_cards(cards), taxonomy


def service_copy(card: dict, lang: str) -> str:
    return card["_i18n"]["en"]["one_liner"] if lang == "en" else card["one_liner"]


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
  <span class="service-meta">{tag_row(card, lang)}<span>{text(verified)}</span></span>
</a>""")
    return '<div class="service-index">' + "".join(rows) + "</div>"


def home_body(cards: list, lang: str) -> str:
    c = HOME[lang]
    flow = (["Repository", "Deployment Contract", "Deploy Agent", "Conformance Evidence"]
            if lang == "en" else ["開源 Repo", "部署契約", "Deploy Agent", "Conformance Evidence"])
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
<section class="section"><div class="shell"><div class="section-head"><div><p class="kicker">{text(c['trust_label'])}</p><h2>{title_lines(c.get('trust_title_lines', [c['trust_title']]))}</h2></div><p class="section-intro">{text(c['trust_text'])}</p></div><div class="trust-grid">{trust_html}</div></div></section>
"""


def static_page_body(page: dict, lang: str) -> str:
    blocks = "".join(f'<section class="content-block"><h2>{text(title)}</h2><p>{text(body)}</p></section>'
                     for title, body in page["sections"])
    return f"""
<header class="page-hero"><div class="shell"><p class="kicker">{text(page['label'])}</p><h1 class="page-title">{title_lines(page.get('title_lines', [page['title']]))}</h1><p class="page-lede">{text(page['lede'])}</p></div></header>
<section class="section"><div class="shell"><div class="content-grid">{blocks}</div></div></section>"""


def concepts_index_body(lang: str) -> str:
    title = "Canonical concepts for Small Software." if lang == "en" else "Small Software 的核心定義。"
    lede = ("One stable URL for each term, with scope, limits and machine-readable references."
            if lang == "en" else "每個名詞只有一個穩定 URL，明示範圍、限制與機器可讀參考。")
    items = []
    for index, (slug, copy) in enumerate(CONCEPTS.items(), 1):
        heading, answer = copy[lang]
        items.append(f'<a class="concept-item" href="{route(lang, f"concepts/{slug}")}"><small>CONCEPT {index:02}</small><div><h2>{text(heading)}</h2><p>{text(answer)}</p></div></a>')
    return f'<header class="page-hero"><div class="shell"><p class="kicker">CONCEPTS</p><h1 class="page-title">{text(title)}</h1><p class="page-lede">{text(lede)}</p></div></header><section class="section"><div class="shell"><div class="concept-grid">{"".join(items)}</div></div></section>'


def concept_body(slug: str, lang: str) -> str:
    title, answer = CONCEPTS[slug][lang]
    section_labels = (["Direct answer", "Why it matters", "Scope", "Out of scope", "How it works", "Example",
                       "Machine-readable references", "Evidence and limitations", "Related concepts", "Version"]
                      if lang == "en" else ["直接回答", "為何重要", "範圍", "不包含", "如何運作", "例子",
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
<section class="section"><div class="shell article-layout"><aside class="article-index">SmallGreen Cloud<br>Concept v1.0</aside><article class="prose">
<h2>{text(section_labels[0])}</h2><p>{text(answer)}</p>
<h2>{text(section_labels[1])}</h2><p>{text(detail['why'])}</p>
<h2>{text(section_labels[2])}</h2><p>{text(scope)}</p>
<h2>{text(section_labels[3])}</h2><p>{text(out_scope)}</p>
<h2>{text(section_labels[4])}</h2><p>{text(detail['how'])}</p>
<h2>{text(section_labels[5])}</h2><p>{text(detail['example'])}</p>
<h2>{text(section_labels[6])}</h2><p>{refs}</p>
<h2>{text(section_labels[7])}</h2><p>{text(detail['evidence'])}</p>
<h2>{text(section_labels[8])}</h2><p>{related_html}</p>
<h2>{text(section_labels[9])}</h2><p>Concept v1.0 · SmallGreen Spec v0.2.1</p>
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


def services_index_body(cards: list, lang: str) -> str:
    title = "A service index built from evidence." if lang == "en" else "依證據建立的服務索引。"
    lede = ("Compare purpose, resource budget, maintenance state and verification date."
            if lang == "en" else "直接比較用途、資源預算、維護狀態與驗證日期。")
    return f'<header class="page-hero"><div class="shell"><p class="kicker">SERVICES / {len(cards)}</p><h1 class="page-title">{text(title)}</h1><p class="page-lede">{text(lede)}</p></div></header><section class="section"><div class="shell">{service_rows(cards, lang)}</div></section>'


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
<div class="evidence-strip"><div class="evidence-status"><span class="pass">{text(LEVEL_LABEL[lang][verification['level']])}</span><span>{len(packs)} EVIDENCE</span><span>SPEC {text(verification['spec_version'])}</span><span>{text(verification.get('last_verified', '—'))}</span></div><div class="evidence-meta">{"Public evidence, scoped to this version and date." if lang == "en" else "公開證據僅適用於標示的版本與日期。"}</div></div>
{screenshot_html}
<figure class="architecture">{arch_svg(card)}<figcaption>{"Architecture generated from the Service Card data flow." if lang == "en" else "依服務卡資料流機械生成的架構圖。"}</figcaption></figure>
{f'<section class="agent-install"><h2>{"Give this to your Agent" if lang == "en" else "交給 Agent 安裝"}</h2><div class="command"><code id="agent-command">{text(install)}</code><button class="copy-button" type="button" data-copy="agent-command" data-copied-label="{copied}">{copy_label}</button></div></section>' if adapter else ''}
<h2>{"Ownership and data" if lang == "en" else "所有權與資料"}</h2><dl class="facts">{facts_html}</dl>
<h2>Evidence Packs</h2><ul>{pack_links or '<li>—</li>'}</ul>
<p><a href="{route(lang, 'services')}">← {"Back to service index" if lang == "en" else "回服務目錄"}</a></p>
</article></div></section>"""


def faq_body(lang: str) -> str:
    title = "Questions that should be answered before deployment." if lang == "en" else "部署前就應該回答的問題。"
    items = "".join(f'<details><summary>{text(q)}</summary><p>{text(a)}</p></details>' for q, a in FAQ[lang])
    return f'<header class="page-hero"><div class="shell"><p class="kicker">FAQ</p><h1 class="page-title">{text(title)}</h1></div></header><section class="section"><div class="shell prose">{items}</div></section>'


def write_legacy_redirects(cards: list, out: Path, base_url: str) -> None:
    legacy = out / "s"
    legacy.mkdir(exist_ok=True)
    for card in cards:
        target = f"/services/{card['id']}/"
        canonical = f"{base_url}{target}"
        page = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta http-equiv="refresh" content="0; url={target}"><link rel="canonical" href="{canonical}"><title>Moved — SmallGreen Cloud</title></head><body><main><p>Moved to <a href="{target}">{target}</a>.</p></main></body></html>"""
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
    not_found = """<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex"><title>Page not found — SmallGreen Cloud</title><link rel="stylesheet" href="/assets/site.css"></head><body><main id="main"><header class="page-hero"><div class="shell"><p class="kicker">404</p><h1 class="page-title">Page not found<br><span lang="zh-Hant">找不到頁面</span></h1><p class="page-lede">The requested path does not exist<br><span lang="zh-Hant">這個網址沒有對應內容</span></p><div class="actions"><a class="button primary" href="/">English home</a><a class="button" href="/zh-tw/">繁體中文首頁</a></div></div></header></main></body></html>"""
    (out / "404.html").write_text(not_found, encoding="utf-8")


def write_machine_outputs(cards: list, out: Path, base_url: str, canonical_routes: list) -> None:
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
    (out / "cards.json").write_text(json.dumps({
        "source": "https://github.com/smallgreen-cloud/registry",
        "spec": "https://github.com/smallgreen-cloud/spec",
        "languages": ["en", "zh-Hant-TW"], "cards": public_cards,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (out / "analytics-policy.json").write_text(json.dumps({
        "schema_version": "1.0", "tracking_scope": "aggregate-only", "cookies": False,
        "user_identifiers": False, "custom_events": False, "query_strings": False,
        "providers": ["Cloudflare Web Analytics", "Cloudflare Edge Analytics", "Cloudflare AI Crawl Control",
                      "Google Search Console", "Bing Webmaster"],
        "purpose": ["SEO measurement", "AEO measurement", "Core Web Vitals", "crawler governance"],
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    llms = ["# SmallGreen Cloud", "", "> The ownership and deployment layer for Small Software.", "",
            "## Canonical resources", "", f"- [Manifesto]({base_url}/manifesto/)",
            f"- [Concepts]({base_url}/concepts/)", f"- [Services]({base_url}/services/)",
            f"- [Standard]({base_url}/standard/)", f"- [Evidence policy]({base_url}/evidence/)",
            f"- [Structured service cards]({base_url}/cards.json)", "", "## Services", ""]
    llms.extend(f"- [{card['name']}]({base_url}/services/{card['id']}/): {service_copy(card, 'en')}" for card in cards)
    (out / "llms.txt").write_text("\n".join(llms) + "\n", encoding="utf-8")

    full = ["# SmallGreen Cloud full service index", ""]
    for card in cards:
        v = card["verification"]
        full.extend([f"## {card['name']}", service_copy(card, "en"),
                     f"- URL: {base_url}/services/{card['id']}/",
                     f"- Upstream: https://github.com/{card['repo']['upstream']}",
                     f"- Verification: {v['level']}; Spec {v['spec_version']}; {v.get('last_verified', '—')}",
                     f"- Resource budget: {card['free_tier_grade']}", ""])
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
            f'<title>SmallGreen Cloud</title><id>{base_url}/</id><updated>{feed_updated}T00:00:00Z</updated>'
            f'{feed_items}</feed>\n')
    (out / "feed.xml").write_text(feed, encoding="utf-8")


def build(registry: Path, out: Path, base_url: str = DEFAULT_BASE_URL) -> None:
    base_url = clean_base_url(base_url)
    cards, _taxonomy = load_registry(registry)
    out.mkdir(parents=True, exist_ok=True)
    assets = out / "assets"
    assets.mkdir(exist_ok=True)
    source_assets = Path(__file__).resolve().parent.parent / "assets"
    shutil.copyfile(source_assets / "site.css", assets / "site.css")
    shutil.copyfile(source_assets / "site.js", assets / "site.js")
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
    website_jsonld = {"@context": "https://schema.org", "@type": "WebSite", "name": "SmallGreen Cloud",
                      "url": f"{base_url}/", "description": HOME["en"]["lede"]}
    for lang in LANGS:
        body = home_body(cards, lang)
        write_page(out, route(lang), layout(lang=lang, active="home", path="", title=HOME[lang]["title"],
                                                   description=HOME[lang]["lede"], body=body, base_url=base_url,
                                                   jsonld=website_jsonld))
        canonical_routes.append((lang, "", max(c["verification"].get("last_verified", "") for c in cards)))

        for slug, localized in STATIC_PAGES.items():
            page = localized[lang]
            page_body = evidence_index_body(cards, lang) if slug == "evidence" else static_page_body(page, lang)
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
                                                          title=("Verified services" if lang == "en" else "驗證服務目錄"),
                                                          description=("Compare Small Software by public deployment evidence." if lang == "en" else "依公開部署證據比較 Small Software。"),
                                                          body=services_index_body(cards, lang), base_url=base_url))
        canonical_routes.append((lang, "services", max(c["verification"].get("last_verified", "") for c in cards)))
        for card in cards:
            path = f"services/{card['id']}"
            write_page(out, route(lang, path), layout(lang=lang, active="services", path=path, title=card["name"],
                                                       description=service_copy(card, lang), body=service_detail_body(card, lang),
                                                       base_url=base_url, jsonld=service_jsonld(card, lang, base_url)))
            canonical_routes.append((lang, path, card["verification"].get("last_verified")))

        write_page(out, route(lang, "faq"), layout(lang=lang, active="faq", path="faq",
                                                     title=("Frequently asked questions" if lang == "en" else "常見問題"),
                                                     description=("Answers about ownership, verification and privacy." if lang == "en" else "關於所有權、驗證與隱私的回答。"),
                                                     body=faq_body(lang), base_url=base_url,
                                                     jsonld={"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
                                                         {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}}
                                                         for q, a in FAQ[lang]]}))
        canonical_routes.append((lang, "faq", None))

    write_legacy_redirects(cards, out, base_url)
    write_cloudflare_outputs(cards, out)
    write_machine_outputs(cards, out, base_url, canonical_routes)
    print(f"built bilingual site: {len(cards)} services, {len(CONCEPTS)} concepts, {len(list(out.rglob('*.html')))} HTML pages")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", required=True, type=Path)
    parser.add_argument("--out", type=Path, default=Path(__file__).resolve().parent.parent / "dist")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    args = parser.parse_args()
    build(args.registry, args.out, args.base_url)
