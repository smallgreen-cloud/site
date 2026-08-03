#!/usr/bin/env python3
"""目錄站建置：registry 服務卡 YAML → 靜態 HTML（dist/）。

真相源＝registry repo（cards/＋taxonomy.yaml）；本站只 render 不另存資料。
本地：--registry <path>；CI：checkout registry 後同樣傳路徑。決定性輸出（無時間戳）。
卡片牆＝單一牆、預設依 last_verified 新→舊；主導航＝分類錨點（hash 觸發 JS 分類過濾，
無 JS 時錨點仍跳至牆頂）。架構／資料流 SVG 由 gen_arch_svg 機械生成（雙圖制：
卡片無 images.screenshot 時以架構圖代主圖）。零外部資源：JS／CSS／SVG 全 inline。
"""
import argparse
import json
from pathlib import Path

import yaml

from gen_arch_svg import arch_svg

LEVEL_LABEL = {"discovered": "Discovered", "community-verified": "Community Verified",
               "smallgreen-ready": "SmallGreen Ready"}
MAINT_LABEL = {"active": "維護中", "slowing": "更新趨緩", "stalled": "久未更新",
               "archived": "已封存", "revived": "復活維護"}
GRADES = ["A", "B", "C", "D"]
BASE = "https://smallgreen-site.pages.dev"
DEFINITION = ("SmallGreen Cloud 是一套針對可在 Cloudflare 免費層自架的小型開源服務的部署標準與驗證目錄："
              "每個收錄專案提供機器可驗的部署契約（profile／acceptance／maintenance 三檔）、"
              "AI agent 可自主執行的部署引導（AGENTS.md）、公開的驗證證據（Evidence Pack）、"
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
footer{max-width:72rem;margin:1rem auto 2rem;padding:0 1.25rem;font-size:.78rem;color:var(--muted)}
footer a,main a{color:var(--green)}
.cats{margin:.5rem 0 1rem;font-size:.85rem}.cats a{margin-right:.8rem}
.card svg{width:100%;height:auto;border:1px solid var(--line);border-radius:.4rem;background:#fff;margin:.15rem 0}
.filters{background:var(--card);border:1px solid var(--line);border-radius:.6rem;padding:.5rem 1rem .7rem;margin:0 0 1.25rem;font-size:.85rem}
.filters legend{font-weight:600;padding:0 .3rem}
.fgroup{display:flex;flex-wrap:wrap;gap:.3rem .9rem;align-items:center;margin:.3rem 0}
.ftitle{color:var(--muted);min-width:4.5rem}
.filters label{cursor:pointer}
.filters input{accent-color:var(--green);margin-right:.3rem;vertical-align:-2px}
#fclear{background:none;border:1px solid var(--line);border-radius:.35rem;padding:.15rem .6rem;color:var(--muted);cursor:pointer;font-size:.8rem}
#fclear:hover{border-color:var(--green);color:var(--green)}
.fcount{color:var(--muted)}
figure{margin:1.25rem 0;background:var(--card);border:1px solid var(--line);border-radius:.6rem;padding:.9rem}
figure svg,figure img{max-width:100%;height:auto;display:block}
figcaption{font-size:.78rem;color:var(--muted);margin-top:.5rem}
.agent-install{border:2px solid var(--green);background:#e7f0ea;border-radius:.6rem;padding:1rem 1.1rem;margin:1.5rem 0}
.agent-install h2{margin:0 0 .4rem}
.cmdrow{display:flex;gap:.5rem;align-items:stretch}
.cmdrow pre{flex:1;margin:0;background:#fff;border:1px solid var(--line);border-radius:.35rem;padding:.6rem .7rem;font-size:.85rem;white-space:pre-wrap;word-break:break-all}
.cmdrow button{background:var(--green);color:#fff;border:0;border-radius:.35rem;padding:0 1rem;cursor:pointer;font-size:.85rem}
.cmdrow button:hover{opacity:.9}
details.tech{border:1px solid var(--line);border-radius:.6rem;background:var(--card);padding:.6rem 1rem;margin:1.25rem 0}
details.tech summary{cursor:pointer;font-weight:600}
details.tech table{border-collapse:collapse;font-size:.85rem;margin:.5rem 0}
details.tech th,details.tech td{border:1px solid var(--line);padding:.3rem .6rem;text-align:left}
"""

FILTER_JS = """
(function(){
var cards=Array.prototype.slice.call(document.querySelectorAll('.grid .card'));
var boxes=Array.prototype.slice.call(document.querySelectorAll('.filters input[type="checkbox"]'));
var cnt=document.getElementById('fcount');
var cat='';
function picked(g){var r=[],i;for(i=0;i<boxes.length;i++){if(boxes[i].getAttribute('data-group')===g&&boxes[i].checked){r.push(boxes[i].value);}}return r;}
function apply(){
 var lv=picked('level'),gr=picked('grade'),mt=picked('maint'),lc=picked('lc').length>0,n=0,i,c,ok;
 for(i=0;i<cards.length;i++){c=cards[i];ok=true;
  if(lv.length&&lv.indexOf(c.getAttribute('data-level'))<0){ok=false;}
  if(ok&&gr.length&&gr.indexOf(c.getAttribute('data-grade'))<0){ok=false;}
  if(ok&&mt.length&&mt.indexOf(c.getAttribute('data-maint'))<0){ok=false;}
  if(ok&&lc&&c.getAttribute('data-lc')!=='1'){ok=false;}
  if(ok&&cat&&(' '+c.getAttribute('data-cats')+' ').indexOf(' '+cat+' ')<0){ok=false;}
  c.style.display=ok?'':'none';if(ok){n++;}}
 if(cnt){cnt.textContent=String(n);}
}
function syncHash(){var h=window.location.hash;cat=(h.indexOf('#cat-')===0)?h.slice(5):'';apply();}
var i;for(i=0;i<boxes.length;i++){boxes[i].addEventListener('change',apply);}
var clr=document.getElementById('fclear');
if(clr){clr.addEventListener('click',function(){var j;for(j=0;j<boxes.length;j++){boxes[j].checked=false;}
 if(window.location.hash.indexOf('#cat-')===0){window.location.hash='wall';}else{cat='';apply();}});}
window.addEventListener('hashchange',syncHash);
syncHash();
})();
"""

COPY_JS = """
(function(){
var b=document.getElementById('copy-btn');
if(!b){return;}
b.addEventListener('click',function(){
 var el=document.getElementById('agent-cmd');
 var t=el?el.textContent.replace(/^\\s+|\\s+$/g,''):'';
 function done(){b.textContent='已複製';setTimeout(function(){b.textContent='複製';},2000);}
 function fallback(){var ta=document.createElement('textarea');ta.value=t;document.body.appendChild(ta);
  ta.select();try{document.execCommand('copy');done();}catch(e){}document.body.removeChild(ta);}
 if(navigator.clipboard&&navigator.clipboard.writeText){navigator.clipboard.writeText(t).then(done,fallback);}
 else{fallback();}
});
})();
"""


def sort_cards(cards: list) -> list:
    """預設排序：last_verified 新→舊；同日以 id 字典序（決定性）。"""
    by_id = sorted(cards, key=lambda c: c["id"])
    return sorted(by_id, key=lambda c: c["verification"].get("last_verified", ""), reverse=True)


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


def render_card(card: dict, cat_names: dict) -> str:
    """卡片牆一卡：五要素（名稱／一句話／驗證徽章／免費層／最近驗證日期）＋小版元件圖。
    data-* 屬性供 inline 篩選 JS 使用。"""
    up = card["repo"]["upstream"]
    v = card["verification"]
    cats = card.get("categories", [])
    cat_txt = "、".join(cat_names.get(c, c) for c in cats)
    lc = "1" if card["low_carbon"].get("scale_to_zero") else "0"
    parts = [
        f'<article class="card" data-level="{v["level"]}" data-grade="{card["free_tier_grade"]}"'
        f' data-lc="{lc}" data-maint="{card["maintenance_status"]}"'
        f' data-cats="{" ".join(cats)}" data-verified="{v.get("last_verified", "")}">',
        f'<h2><a href="/s/{card["id"]}.html">{card["name"]}</a></h2>',
        f'<div class="badges">{badge_row(card)}</div>',
        f'<p class="one">{card["one_liner"]}</p>',
        arch_svg(card, compact=True),
        f'<p class="meta">最近驗證 {v.get("last_verified", "")}｜{cat_txt}｜'
        f'上游 <a href="https://github.com/{up}" rel="noopener">{up}</a></p>',
        "</article>",
    ]
    return "\n".join(parts)


def card_jsonld(card: dict) -> dict:
    return {
        "@context": "https://schema.org",
        "@type": "SoftwareApplication",
        "name": card["name"],
        "description": card["one_liner"],
        "url": f"{BASE}/s/{card['id']}.html",
        "image": f"{BASE}/img/arch/{card['id']}.svg",
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


def render_figures(card: dict) -> str:
    """雙圖制：有 images.screenshot（站內相對路徑）→ 主圖截圖＋副圖架構 SVG；
    沒有（現階段全部）→ 架構 SVG 代主圖。截圖僅接受站內路徑（零外部資源鐵律）。"""
    svg = arch_svg(card)
    arch_fig = (f'<figure>{svg}'
                f'<figcaption>架構與資料流：依部署契約（components＋data_flow）機械生成，'
                f'虛線＝對外連線。非示意 mockup。</figcaption></figure>')
    shot = card.get("_shot_site_path")
    if shot:
        return (f'<figure><img src="{shot}" alt="{card["name"]} 實際畫面截圖" loading="lazy">'
                f'<figcaption>實際畫面截圖（Evidence Pack 驗證時收取，非示意圖）</figcaption></figure>' + arch_fig)
    return arch_fig


def render_agent_install(card: dict) -> str:
    """「交給 Agent 安裝」醒目區塊：可複製指令＋一鍵複製（inline JS，零外部資源）。"""
    ad = card["repo"].get("adapter")
    if not ad:
        return ('<section class="agent-install"><h2>交給 Agent 安裝</h2>'
                '<p>本專案尚無 adapter repo，暫不提供 agent 自主安裝入口。</p></section>')
    cmd = f"請照 https://github.com/{ad} 的 AGENTS.md 部署這個服務"
    return (f'<section class="agent-install"><h2>交給 Agent 安裝</h2>\n'
            f'<p>把這段丟給你的 Claude Code／Codex／Gemini CLI：</p>\n'
            f'<div class="cmdrow"><pre id="agent-cmd">{cmd}</pre>'
            f'<button type="button" id="copy-btn" aria-label="複製指令">複製</button></div>\n'
            f'<p class="meta">adapter repo 鎖定已驗證 commit，內含非互動部署引導與部署契約三檔。</p>'
            f'</section>')


def render_card_page(card: dict) -> str:
    """詳頁價值層次：一句話 use case → 視覺（雙圖制）→ 信任信號 →
    「交給 Agent 安裝」→ 技術棧與驗證紀錄（details 摺疊）。"""
    v = card["verification"]
    up = card["repo"]["upstream"]
    ad = card["repo"].get("adapter")
    agents_rows = "".join(
        f"<tr><td>{a['agent']}</td><td>{a['model']}</td><td>{a['result']}</td></tr>"
        for a in v.get("compatible_agents", []))
    packs = "".join(
        f'<li><a href="https://github.com/smallgreen-cloud/registry/blob/main/{p}" rel="noopener">{p.split("/")[-1]}</a></li>'
        for p in v.get("evidence_packs", []))
    ext = card.get("data_flow", {}).get("external_services", [])
    ext_html = "".join(f"<li>{e}</li>" for e in ext) or "<li>無</li>"
    jsonld = json.dumps(card_jsonld(card), ensure_ascii=False)
    quota = f'<p class="disc">額度備註：{card["quota_note"]}</p>' if card.get("quota_note") else ""
    comp = "、".join(card.get("components", {}).get("cloudflare", []))
    adapter_line = (f'適配（AI agent 部署入口）：<a href="https://github.com/{ad}" rel="noopener">github.com/{ad}</a>。'
                    if ad else "")
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
{render_figures(card)}
<h2>信任信號</h2>
<p class="meta">驗證等級 {LEVEL_LABEL[v['level']]}｜最近驗證 {v.get('last_verified','')}｜維護狀態 {MAINT_LABEL[card['maintenance_status']]}</p>
<h3>資料流向揭露</h3>
<p>{card.get('data_flow', {}).get('disclosure', '')}</p>
<h3>外連清單</h3>
<ul>{ext_html}</ul>
{render_agent_install(card)}
<details class="tech">
<summary>技術棧與驗證紀錄</summary>
<p>Cloudflare 元件：{comp}。上游專案：<a href="https://github.com/{up}" rel="noopener">{up}</a>（{card['repo'].get('license','')}）。{adapter_line}</p>
<h3>agent 部署矩陣（spec {v['spec_version']}，最近驗證 {v.get('last_verified','')}）</h3>
<table><tr><th>agent</th><th>model</th><th>結果</th></tr>{agents_rows}</table>
<h3>Evidence Packs</h3><ul>{packs}</ul>
{quota}
</details>
</main>
<footer><p><a href="/">回目錄</a>｜<a href="/cards.json">cards.json</a>｜<a href="/llms.txt">llms.txt</a>｜標準：<a href="https://github.com/smallgreen-cloud/spec">spec</a></p></footer>
<script>{COPY_JS}</script>
</body></html>
"""


def render_filters(cards: list) -> str:
    """屬性標籤多選篩選器：驗證等級／免費層 A-D／低碳／維護狀態（data-* 驅動）。"""
    present_maint = {c["maintenance_status"] for c in cards}
    maints = [k for k in MAINT_LABEL if k in present_maint]

    def cb(group: str, value: str, label: str) -> str:
        return (f'<label><input type="checkbox" data-group="{group}" value="{value}">'
                f'{label}</label>')

    return (
        '<fieldset class="filters"><legend>篩選（可多選，同群組為「或」、跨群組為「且」）</legend>'
        f'<div class="fgroup"><span class="ftitle">驗證等級</span>'
        f'{"".join(cb("level", k, v) for k, v in LEVEL_LABEL.items())}</div>'
        f'<div class="fgroup"><span class="ftitle">免費層</span>'
        f'{"".join(cb("grade", g, g) for g in GRADES)}</div>'
        f'<div class="fgroup"><span class="ftitle">低碳</span>'
        f'{cb("lc", "1", "scale-to-zero")}</div>'
        f'<div class="fgroup"><span class="ftitle">維護狀態</span>'
        f'{"".join(cb("maint", k, MAINT_LABEL[k]) for k in maints)}</div>'
        f'<div class="fgroup"><button type="button" id="fclear">清除篩選</button>'
        f'<span class="fcount">符合 <span id="fcount">{len(cards)}</span> 個</span></div>'
        '</fieldset>')


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
    cards = sort_cards(cards)
    taxonomy = yaml.safe_load((registry / "taxonomy.yaml").read_text(encoding="utf-8"))["categories"]
    cat_names = {c["id"]: c["name"] for c in taxonomy}
    out.mkdir(parents=True, exist_ok=True)
    # 雙圖制主圖：卡片 images.screenshot（registry 相對路徑物件）→ 複製檔案進 dist 並掛站內路徑
    shots_dir = out / "img" / "shots"
    for c in cards:
        shot = (c.get("images") or {}).get("screenshot")
        src = (registry / shot["path"]) if isinstance(shot, dict) and shot.get("path") else None
        if src is not None and src.exists():
            shots_dir.mkdir(parents=True, exist_ok=True)
            dest = shots_dir / f"{c['id']}{src.suffix}"
            dest.write_bytes(src.read_bytes())
            c["_shot_site_path"] = f"/img/shots/{dest.name}"
    cat_links = f'<a href="#wall">全部（{len(cards)}）</a> ' + " ".join(
        f'<a href="#cat-{c["id"]}">{c["name"]}（{sum(1 for x in cards if c["id"] in x["categories"])}）</a>'
        for c in taxonomy)
    anchors = "".join(f'<span id="cat-{c["id"]}"></span>' for c in taxonomy)
    wall = (f'{anchors}<div id="wall">{render_filters(cards)}'
            f'<div class="grid">{"".join(render_card(c, cat_names) for c in cards)}</div></div>')
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
<p class="note">共 {len(cards)} 個專案，預設依最近驗證日期排序（新→舊）。徽章說明：免費層 A＝零必填 secret 即可部署；C＝需設定 secret 或用量額度緊（詳各卡）。低碳欄位由部署契約機械推導，非自報。</p>
<nav class="cats">{cat_links}</nav>
{wall}
<h2 id="faq">常見問題</h2>
{faq_html}
</main>
<footer>
<p>標準與驗證方法：<a href="https://github.com/smallgreen-cloud/spec">spec</a>（v0.2.1）｜資料真相源：<a href="https://github.com/smallgreen-cloud/registry">registry</a>（本站只 render 不另存）｜機器可讀：<a href="/cards.json">cards.json</a>・<a href="/llms.txt">llms.txt</a>・<a href="/sitemap.xml">sitemap</a>｜本站本身依 SmallGreen 標準部署（Path A）。文件 CC-BY-4.0，程式碼 Apache-2.0。</p>
</footer>
<script>{FILTER_JS}</script>
</body></html>
"""
    (out / "index.html").write_text(html, encoding="utf-8")
    sdir = out / "s"
    sdir.mkdir(exist_ok=True)
    for c in cards:
        (sdir / f"{c['id']}.html").write_text(render_card_page(c), encoding="utf-8")
    idir = out / "img" / "arch"
    idir.mkdir(parents=True, exist_ok=True)
    for c in cards:
        (idir / f"{c['id']}.svg").write_text(
            '<?xml version="1.0" encoding="UTF-8"?>\n' + arch_svg(c), encoding="utf-8")
    write_machine_outputs(cards, taxonomy, out)
    print(f"built dist: {len(cards)} cards, {len(taxonomy)} categories, "
          f"{len(cards)} detail pages + {len(cards)} arch svgs + cards.json/llms/robots/sitemap")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--registry", required=True, type=Path)
    ap.add_argument("--out", type=Path, default=Path(__file__).resolve().parent.parent / "dist")
    a = ap.parse_args()
    build(a.registry, a.out)
