#!/usr/bin/env python3
"""目錄站建置：registry 服務卡 YAML → 靜態 HTML（dist/）。

真相源＝registry repo（cards/＋taxonomy.yaml）；本站只 render 不另存資料。
本地：--registry <path>；CI：checkout registry 後同樣傳路徑。決定性輸出（無時間戳）。
"""
import argparse
import json
from pathlib import Path

import yaml

LEVEL_LABEL = {"discovered": "Discovered", "community-verified": "Community Verified",
               "smallgreen-ready": "SmallGreen Ready"}
MAINT_LABEL = {"active": "維護中", "slowing": "更新趨緩", "stalled": "久未更新",
               "archived": "已封存", "revived": "復活維護"}
BASE = "https://smallgreen-site.pages.dev"
DEFINITION = ("SmallGreen Cloud 是一套針對可在 Cloudflare 免費層自架的小型開源服務的部署標準與驗證目錄："
              "每個收錄專案提供機器可驗的部署契約（profile／acceptance／maintenance 三檔）、"
              "AI agent 可自主執行的部署引導（AGENTS.md）、公開的驗證證據（Evidence Pack），"
              "以及資料流向與遙測的信任揭露。目標是讓個人以零月費、可退場、可驗證的方式擁有自己的小型服務。")
FAQ = [
    ("什麼是 SmallGreen Cloud？", DEFINITION),
    ("收錄代表背書嗎？", "不代表。收錄等級分三級：Discovered（已驗證可部署）、Community Verified（有真實使用見證）、SmallGreen Ready（agent 全自主部署＋零未揭露外連＋可乾淨移除）。等級由機械檢核與證據晉升，不可自我宣告。"),
    ("免費層等級 A/C/D 是什麼意思？", "A＝零必填 secret 即可部署且不用量緊資源；C＝需設定 secret 或使用共用額度緊的資源（如 Workers AI）；D＝必用額度緊資源或有付費前置。由部署契約機械判定，非自報。"),
    ("低碳標示怎麼來的？", "scale-to-zero 與無閒置基礎設施由 wrangler 資源宣告機械推導（事件驅動、無常駐程序），記錄在每次驗證的 Evidence Pack，禁止手填。"),
    ("AI agent 可以直接用這個目錄部署嗎？", "可以。每個收錄專案的 adapter repo 含 AGENTS.md 非互動部署引導與鎖定 commit 的契約；本站 /cards.json 與 /llms-full.txt 提供機器可讀的完整卡片資料。"),
]

CSS = """
:root{--fg:#1c2b22;--bg:#f6f8f6;--card:#ffffff;--line:#d8e0d8;--green:#2c6e49;--muted:#5b6b60;--warn:#8a6d1a}
*{box-sizing:border-box}body{margin:0;font-family:ui-sans-serif,system-ui,'Noto Sans TC',sans-serif;color:var(--fg);background:var(--bg);line-height:1.55}
header{background:var(--green);color:#fff;padding:2rem 1.25rem}
header h1{margin:0 0 .3rem;font-size:1.6rem}header p{margin:0;opacity:.92;max-width:52rem}
main{max-width:72rem;margin:0 auto;padding:1.5rem 1.25rem}
.note{font-size:.85rem;color:var(--muted);margin:.75rem 0 1.25rem}
.grid{display:grid;gap:1rem;grid-template-columns:repeat(auto-fill,minmax(20rem,1fr))}
.card{background:var(--card);border:1px solid var(--line);border-radius:.6rem;padding:1rem 1.1rem;display:flex;flex-direction:column;gap:.5rem}
.card h2{margin:0;font-size:1.1rem}.card h2 a{color:var(--fg);text-decoration:none}.card h2 a:hover{text-decoration:underline}
.badges{display:flex;flex-wrap:wrap;gap:.35rem;font-size:.72rem}
.badge{border:1px solid var(--line);border-radius:.25rem;padding:.1rem .4rem;color:var(--muted)}
.badge.level{border-color:var(--green);color:var(--green)}
.badge.grade-A{background:var(--green);border-color:var(--green);color:#fff}
.badge.grade-C,.badge.grade-D{border-color:var(--warn);color:var(--warn)}
.badge.lc{color:var(--green);border-color:var(--green)}
.one{margin:0;font-size:.92rem}.meta{font-size:.78rem;color:var(--muted);margin:0}
.disc{font-size:.8rem;color:var(--muted);border-top:1px dashed var(--line);padding-top:.5rem;margin:0}
.agents{font-size:.75rem;color:var(--muted)}
footer{max-width:72rem;margin:1rem auto 2rem;padding:0 1.25rem;font-size:.78rem;color:var(--muted)}
footer a,main a{color:var(--green)}
.cats{margin:.5rem 0 1rem;font-size:.85rem}.cats a{margin-right:.8rem}
"""


def badge_row(card: dict) -> str:
    v = card["verification"]
    lc = card["low_carbon"]
    b = [f'<span class="badge level">{LEVEL_LABEL[v["level"]]}</span>',
         f'<span class="badge grade-{card["free_tier_grade"]}">免費層 {card["free_tier_grade"]}</span>']
    if lc.get("scale_to_zero"):
        b.append('<span class="badge lc">scale-to-zero</span>')
    if lc.get("no_idle_infra"):
        b.append('<span class="badge lc">無閒置基礎設施</span>')
    b.append(f'<span class="badge">{MAINT_LABEL[card["maintenance_status"]]}</span>')
    return "".join(b)


def render_card(card: dict) -> str:
    up = card["repo"]["upstream"]
    ad = card["repo"].get("adapter")
    agents = "、".join(f'{a["agent"]}（{a["result"]}）' for a in card["verification"].get("compatible_agents", []))
    packs_n = len(card["verification"].get("evidence_packs", []))
    parts = [
        '<article class="card">',
        f'<h2><a href="/s/{card["id"]}.html">{card["name"]}</a></h2>',
        f'<div class="badges">{badge_row(card)}</div>',
        f'<p class="one">{card["one_liner"]}</p>',
        f'<p class="meta">上游 <a href="https://github.com/{up}" rel="noopener">{up}</a>（{card["repo"].get("license","")}）',
    ]
    if ad:
        parts.append(f'　適配 <a href="https://github.com/{ad}" rel="noopener">{ad.split("/")[-1]}</a>')
    parts.append(f'　驗證紀錄 {packs_n} 筆</p>')
    if agents:
        parts.append(f'<p class="agents">部署過的 agent：{agents}</p>')
    disc = card.get("data_flow", {}).get("disclosure")
    if disc:
        parts.append(f'<p class="disc">資料流向：{disc}</p>')
    parts.append("</article>")
    return "\n".join(parts)


def card_jsonld(card: dict) -> dict:
    return {
        "@context": "https://schema.org",
        "@type": "SoftwareApplication",
        "name": card["name"],
        "description": card["one_liner"],
        "url": f"{BASE}/s/{card['id']}.html",
        "applicationCategory": "DeveloperApplication",
        "operatingSystem": "Cloudflare Workers",
        "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"},
        "license": f"https://spdx.org/licenses/{card['repo'].get('license','')}",
        "codeRepository": f"https://github.com/{card['repo']['upstream']}",
        "review": {
            "@type": "Review",
            "name": f"SmallGreen 部署驗證（{LEVEL_LABEL[card['verification']['level']]}）",
            "author": {"@type": "Organization", "name": "SmallGreen Cloud"},
            "datePublished": card["verification"].get("last_verified", ""),
            "reviewBody": f"依 SmallGreen spec {card['verification']['spec_version']} 驗證部署；"
                          f"免費層等級 {card['free_tier_grade']}；Evidence Pack {len(card['verification'].get('evidence_packs', []))} 筆。",
        },
    }


def render_card_page(card: dict) -> str:
    v = card["verification"]
    ad = card["repo"].get("adapter")
    up = card["repo"]["upstream"]
    agents_rows = "".join(
        f"<tr><td>{a['agent']}</td><td>{a['model']}</td><td>{a['result']}</td></tr>"
        for a in v.get("compatible_agents", []))
    packs = "".join(
        f'<li><a href="https://github.com/smallgreen-cloud/registry/blob/main/{p}" rel="noopener">{p.split("/")[-1]}</a></li>'
        for p in v.get("evidence_packs", []))
    jsonld = json.dumps(card_jsonld(card), ensure_ascii=False)
    quota = f'<p class="disc">額度備註：{card["quota_note"]}</p>' if card.get("quota_note") else ""
    return f"""<!doctype html>
<html lang="zh-Hant"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{card['name']} — SmallGreen Cloud 驗證檔案</title>
<meta name="description" content="{card['one_liner']}（SmallGreen 驗證：{LEVEL_LABEL[v['level']]}、免費層 {card['free_tier_grade']}）">
<link rel="canonical" href="{BASE}/s/{card['id']}.html">
<meta property="og:title" content="{card['name']} — SmallGreen Cloud">
<meta property="og:description" content="{card['one_liner']}">
<meta property="og:type" content="website">
<script type="application/ld+json">{jsonld}</script>
<style>{CSS}</style></head><body>
<header><h1><a href="/" style="color:#fff;text-decoration:none">SmallGreen Cloud</a> / {card['name']}</h1>
<p>{card['one_liner']}</p></header>
<main>
<div class="badges">{badge_row(card)}</div>
<h2>部署方式</h2>
<p>依適配 repo 的 AGENTS.md（AI agent 可自主執行）：<a href="https://github.com/{ad}" rel="noopener">github.com/{ad}</a>。
上游專案：<a href="https://github.com/{up}" rel="noopener">{up}</a>（{card['repo'].get('license','')}）。</p>
<h2>資料流向揭露</h2>
<p>{card.get('data_flow', {}).get('disclosure', '')}</p>
<p class="meta">外連：{('、'.join(card.get('data_flow', {}).get('external_services', [])) or '無')}</p>
{quota}
<h2>驗證紀錄（spec {v['spec_version']}，最近 {v.get('last_verified','')}）</h2>
<table><tr><th>agent</th><th>model</th><th>結果</th></tr>{agents_rows}</table>
<h3>Evidence Packs</h3><ul>{packs}</ul>
</main>
<footer><p><a href="/">回目錄</a>｜<a href="/cards.json">cards.json</a>｜<a href="/llms.txt">llms.txt</a>｜標準：<a href="https://github.com/smallgreen-cloud/spec">spec</a></p></footer>
</body></html>
"""


def write_machine_outputs(cards, taxonomy, out: Path):
    # cards.json：agent 直接可食的全量結構化資料
    (out / "cards.json").write_text(
        json.dumps({"source": "https://github.com/smallgreen-cloud/registry",
                    "spec": "https://github.com/smallgreen-cloud/spec",
                    "cards": cards}, ensure_ascii=False, indent=1), encoding="utf-8")
    # llms.txt（llmstxt.org 慣例）
    lines = ["# SmallGreen Cloud", "", f"> {DEFINITION}", "",
             "重要事實：收錄等級（Discovered／Community Verified／SmallGreen Ready）由機械檢核與公開證據晉升，不可自我宣告；"
             "免費層等級與低碳欄位由部署契約機械推導。",
             "", "## 核心資源", "",
             f"- [服務目錄（本站）]({BASE}/)：全部收錄專案與驗證徽章",
             f"- [cards.json]({BASE}/cards.json)：全量服務卡結構化資料（JSON）",
             f"- [llms-full.txt]({BASE}/llms-full.txt)：全部服務卡的完整文字版",
             "- [SmallGreen spec](https://github.com/smallgreen-cloud/spec)：標準本體（部署契約 schema、驗證等級、Evidence Pack 規格；CC-BY-4.0/Apache-2.0）",
             "- [registry](https://github.com/smallgreen-cloud/registry)：服務卡真相源＋全部 Evidence Packs（可稽核）",
             "", "## 收錄服務", ""]
    for c in cards:
        lines.append(f"- [{c['name']}]({BASE}/s/{c['id']}.html)：{c['one_liner']}（免費層 {c['free_tier_grade']}）")
    (out / "llms.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    # llms-full.txt：逐卡完整
    full = [f"# SmallGreen Cloud 全量服務卡\n\n{DEFINITION}\n"]
    for c in cards:
        v = c["verification"]
        full.append(f"## {c['name']}（{c['id']}）\n"
                    f"{c['one_liner']}\n"
                    f"- 上游：github.com/{c['repo']['upstream']}（{c['repo'].get('license','')}）\n"
                    f"- 適配（AI agent 部署入口）：github.com/{c['repo'].get('adapter','')}\n"
                    f"- 驗證：{LEVEL_LABEL[v['level']]}，spec {v['spec_version']}，最近 {v.get('last_verified','')}，"
                    f"Evidence Packs {len(v.get('evidence_packs', []))} 筆\n"
                    f"- 免費層 {c['free_tier_grade']}；低碳：scale_to_zero={c['low_carbon']['scale_to_zero']}、"
                    f"no_idle_infra={c['low_carbon']['no_idle_infra']}\n"
                    f"- 資料流向：{c.get('data_flow', {}).get('disclosure','')}\n"
                    f"- 部署過的 agent：{'、'.join(a['agent'] + '/' + a['model'] + '（' + a['result'] + '）' for a in v.get('compatible_agents', []))}\n")
    (out / "llms-full.txt").write_text("\n".join(full), encoding="utf-8")
    # robots.txt：明示歡迎（含 AI 爬蟲）
    bots = ["GPTBot", "OAI-SearchBot", "ChatGPT-User", "ClaudeBot", "Claude-User", "anthropic-ai",
            "PerplexityBot", "Google-Extended", "Applebot-Extended", "CCBot", "Bytespider", "meta-externalagent"]
    robots = ["# SmallGreen Cloud：內容 CC-BY-4.0，歡迎索引與 AI 檢索引用（附來源連結）", "User-agent: *", "Allow: /", ""]
    for b in bots:
        robots += [f"User-agent: {b}", "Allow: /", ""]
    robots.append(f"Sitemap: {BASE}/sitemap.xml")
    (out / "robots.txt").write_text("\n".join(robots) + "\n", encoding="utf-8")
    # sitemap
    last = max((c["verification"].get("last_verified", "2026-08-02") for c in cards), default="2026-08-02")
    urls = [f"<url><loc>{BASE}/</loc><lastmod>{last}</lastmod></url>"]
    for c in cards:
        urls.append(f"<url><loc>{BASE}/s/{c['id']}.html</loc>"
                    f"<lastmod>{c['verification'].get('last_verified', last)}</lastmod></url>")
    (out / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + "".join(urls) + "</urlset>\n",
        encoding="utf-8")


def build(registry: Path, out: Path):
    cards = [yaml.safe_load(p.read_text(encoding="utf-8")) for p in sorted((registry / "cards").glob("*.yaml"))]
    taxonomy = yaml.safe_load((registry / "taxonomy.yaml").read_text(encoding="utf-8"))["categories"]
    out.mkdir(parents=True, exist_ok=True)
    cat_links = " ".join(f'<a href="#cat-{c["id"]}">{c["name"]}</a>' for c in taxonomy)
    sections = []
    for c in taxonomy:
        members = [x for x in cards if c["id"] in x["categories"]]
        sections.append(f'<h2 id="cat-{c["id"]}">{c["name"]}（{len(members)}）</h2>'
                        f'<div class="grid">{"".join(render_card(m) for m in members)}</div>')
    itemlist = json.dumps({
        "@context": "https://schema.org",
        "@graph": [
            {"@type": "WebSite", "name": "SmallGreen Cloud", "url": BASE,
             "description": DEFINITION,
             "publisher": {"@type": "Organization", "name": "SmallGreen Cloud",
                            "url": "https://github.com/smallgreen-cloud"}},
            {"@type": "Dataset", "name": "SmallGreen Evidence Dataset",
             "description": "全部收錄專案的部署驗證證據（Evidence Packs）與服務卡結構化資料",
             "url": "https://github.com/smallgreen-cloud/registry",
             "license": "https://creativecommons.org/licenses/by/4.0/",
             "distribution": [{"@type": "DataDownload", "encodingFormat": "application/json",
                                "contentUrl": f"{BASE}/cards.json"}]},
            {"@type": "ItemList", "itemListElement": [
                {"@type": "ListItem", "position": i + 1, "url": f"{BASE}/s/{c['id']}.html", "name": c["name"]}
                for i, c in enumerate(cards)]},
            {"@type": "FAQPage", "mainEntity": [
                {"@type": "Question", "name": q,
                 "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in FAQ]},
        ]}, ensure_ascii=False)
    faq_html = "".join(f"<h3>{q}</h3><p>{a}</p>" for q, a in FAQ)
    html = f"""<!doctype html>
<html lang="zh-Hant"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>SmallGreen Cloud — 經驗證的免費層小型開源服務</title>
<meta name="description" content="{DEFINITION[:150]}">
<link rel="canonical" href="{BASE}/">
<meta property="og:title" content="SmallGreen Cloud — 經驗證的免費層小型開源服務目錄">
<meta property="og:description" content="{DEFINITION[:150]}">
<meta property="og:type" content="website">
<script type="application/ld+json">{itemlist}</script>
<style>{CSS}</style></head><body>
<header><h1>SmallGreen Cloud</h1>
<p>可在 Cloudflare 免費層自架的小型開源服務目錄——每個收錄專案附機器可驗的部署契約、驗證證據（Evidence Pack）與資料流向揭露。收錄 ≠ 背書：目前全部為 Discovered 等級（已驗證可部署，尚無社群使用見證）。</p></header>
<main>
<p class="note">共 {len(cards)} 個專案。徽章說明：免費層 A＝零必填 secret 即可部署；C＝需設定 secret 或用量額度緊（詳各卡）。低碳欄位由部署契約機械推導，非自報。</p>
<nav class="cats">{cat_links}</nav>
{"".join(sections)}
<h2 id="faq">常見問題</h2>
{faq_html}
</main>
<footer>
<p>標準與驗證方法：<a href="https://github.com/smallgreen-cloud/spec">spec</a>（v0.2.1）｜資料真相源：<a href="https://github.com/smallgreen-cloud/registry">registry</a>（本站只 render 不另存）｜機器可讀：<a href="/cards.json">cards.json</a>・<a href="/llms.txt">llms.txt</a>・<a href="/sitemap.xml">sitemap</a>｜本站本身依 SmallGreen 標準部署（Path A）。文件 CC-BY-4.0，程式碼 Apache-2.0。</p>
</footer></body></html>
"""
    (out / "index.html").write_text(html, encoding="utf-8")
    sdir = out / "s"
    sdir.mkdir(exist_ok=True)
    for c in cards:
        (sdir / f"{c['id']}.html").write_text(render_card_page(c), encoding="utf-8")
    write_machine_outputs(cards, taxonomy, out)
    print(f"built dist: {len(cards)} cards, {len(taxonomy)} categories, "
          f"{len(cards)} detail pages + cards.json/llms/robots/sitemap")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--registry", required=True, type=Path)
    ap.add_argument("--out", type=Path, default=Path(__file__).resolve().parent.parent / "dist")
    a = ap.parse_args()
    build(a.registry, a.out)
