#!/usr/bin/env python3
"""目錄站建置：registry 服務卡 YAML → 靜態 HTML（dist/）。

真相源＝registry repo（cards/＋taxonomy.yaml）；本站只 render 不另存資料。
本地：--registry <path>；CI：checkout registry 後同樣傳路徑。決定性輸出（無時間戳）。
"""
import argparse
from pathlib import Path

import yaml

LEVEL_LABEL = {"discovered": "Discovered", "community-verified": "Community Verified",
               "smallgreen-ready": "SmallGreen Ready"}
MAINT_LABEL = {"active": "維護中", "slowing": "更新趨緩", "stalled": "久未更新",
               "archived": "已封存", "revived": "復活維護"}

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
        f'<h2><a href="https://github.com/{ad or up}" rel="noopener">{card["name"]}</a></h2>',
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
    html = f"""<!doctype html>
<html lang="zh-Hant"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>SmallGreen Cloud — 經驗證的免費層小型開源服務</title>
<style>{CSS}</style></head><body>
<header><h1>SmallGreen Cloud</h1>
<p>可在 Cloudflare 免費層自架的小型開源服務目錄——每個收錄專案附機器可驗的部署契約、驗證證據（Evidence Pack）與資料流向揭露。收錄 ≠ 背書：目前全部為 Discovered 等級（已驗證可部署，尚無社群使用見證）。</p></header>
<main>
<p class="note">共 {len(cards)} 個專案。徽章說明：免費層 A＝零必填 secret 即可部署；C＝需設定 secret 或用量額度緊（詳各卡）。低碳欄位由部署契約機械推導，非自報。</p>
<nav class="cats">{cat_links}</nav>
{"".join(sections)}
</main>
<footer>
<p>標準與驗證方法：<a href="https://github.com/smallgreen-cloud/spec">spec</a>（v0.2.1）｜資料真相源：<a href="https://github.com/smallgreen-cloud/registry">registry</a>（本站只 render 不另存）｜本站本身依 SmallGreen 標準部署（Path A）。文件 CC-BY-4.0，程式碼 Apache-2.0。</p>
</footer></body></html>
"""
    (out / "index.html").write_text(html, encoding="utf-8")
    print(f"built dist: {len(cards)} cards, {len(taxonomy)} categories")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--registry", required=True, type=Path)
    ap.add_argument("--out", type=Path, default=Path(__file__).resolve().parent.parent / "dist")
    a = ap.parse_args()
    build(a.registry, a.out)
