#!/usr/bin/env python3
"""服務卡 → 架構／資料流 SVG（決定性機械生成，零外部資源）。

模板化元件圖：左「使用者」→ 中計算節點（Worker／Pages，依 components.cloudflare）→
右資料層（D1／KV／AE／Queue／Workers AI／Cron 各自小方塊，依 components 有無渲染）；
data_flow.external_services 以虛線箭頭出圖右側標 domain。
純幾何＋文字 SVG，同輸入同輸出（無時間戳、無隨機）。嚴禁 mockup 與 AI 生圖——
本模組只畫部署契約裡宣告的事實。compact 版供卡片牆內嵌（省外連與文字細節）。
"""
from xml.sax.saxutils import escape

GREEN = "#2c6e49"
GREEN_FILL = "#e7f0ea"
LINE = "#9db8a8"
MUTED = "#5b6b60"
DASH = "#7d9a8b"
INK = "#1c2b22"
FONT = "ui-sans-serif,system-ui,'Noto Sans TC',sans-serif"

COMPUTE_LABEL = {"workers": "Worker", "pages": "Pages"}
# id → (完整標籤, 短標籤)
DATA_LABEL = {
    "d1": ("D1 資料庫", "D1"),
    "kv": ("KV 儲存", "KV"),
    "r2": ("R2 物件儲存", "R2"),
    "queues": ("Queue 佇列", "Queue"),
    "workers-ai": ("Workers AI", "AI"),
    "analytics-engine": ("Analytics Engine", "AE"),
    "cron": ("Cron 排程", "Cron"),
    "vectorize": ("Vectorize", "Vec"),
    "durable-objects": ("Durable Objects", "DO"),
}
EXT_PLACEHOLDER = {"(user-directed)": "使用者指定端點", "(user-configured)": "使用者設定端點"}
EXT_MAXLEN = 30


def _split_components(card: dict) -> tuple[list[tuple[str, str]], list[tuple[str, str, str]]]:
    """components.cloudflare → (計算節點 [(id, label)], 資料層 [(id, 全標籤, 短標籤)])。"""
    compute: list[tuple[str, str]] = []
    data: list[tuple[str, str, str]] = []
    for raw in card.get("components", {}).get("cloudflare", []):
        base = str(raw).strip().replace("（選配）", "(選配)")
        opt = base.endswith("(選配)")
        cid = base[: -len("(選配)")].strip() if opt else base
        suffix = "（選配）" if opt else ""
        if cid in COMPUTE_LABEL:
            compute.append((cid, COMPUTE_LABEL[cid] + suffix))
        else:
            full, short = DATA_LABEL.get(cid, (cid, cid[:6]))
            data.append((cid, full + suffix, short))
    return compute, data


def _externals(card: dict) -> list[str]:
    """external_services → 去重、佔位符轉中文、截斷後的標籤列（保序）。"""
    seen: set[str] = set()
    out: list[str] = []
    for e in card.get("data_flow", {}).get("external_services", []):
        label = EXT_PLACEHOLDER.get(str(e).strip(), str(e).strip())
        if not label or label in seen:
            continue
        seen.add(label)
        if len(label) > EXT_MAXLEN:
            label = label[: EXT_MAXLEN - 1] + "…"
        out.append(label)
    return out


def _box(x: float, y: float, w: float, h: float, fill: str, stroke: str,
         label: str, fs: int, tfill: str) -> str:
    cx, cy = x + w / 2, y + h / 2 + fs * 0.35
    return (f'<rect x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" rx="6" '
            f'fill="{fill}" stroke="{stroke}"/>'
            f'<text x="{cx:g}" y="{cy:g}" text-anchor="middle" font-size="{fs}" '
            f'fill="{tfill}">{escape(label)}</text>')


def _markers(mid: str) -> str:
    return (f'<defs><marker id="{mid}s" markerWidth="8" markerHeight="8" refX="7" refY="4" '
            f'orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="{GREEN}"/></marker>'
            f'<marker id="{mid}d" markerWidth="8" markerHeight="8" refX="7" refY="4" '
            f'orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="{DASH}"/></marker></defs>')


def _svg_full(card: dict) -> str:
    compute, data = _split_components(card)
    if not compute:
        compute = [("app", "服務")]
    ext = _externals(card)
    w_total, m = 720, 18
    ux, uw, uh = 24, 104, 40
    cx0, cw, ch, cgap = 252, 150, 40, 12
    dx, dw, dh, dgap = 468, 176, 32, 8
    eh = 26
    comp_h = len(compute) * ch + (len(compute) - 1) * cgap
    data_h = len(data) * dh + (len(data) - 1) * dgap if data else 0
    ext_h = len(ext) * eh
    right_h = data_h + (14 if data_h and ext_h else 0) + ext_h
    inner = max(comp_h, right_h, uh)
    height = inner + 2 * m
    yc = m + inner / 2
    mid = f"arw-{card['id']}"
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w_total} {height:g}" role="img" '
        f'font-family="{FONT}" aria-label="{escape(card["name"])} 架構與資料流圖">',
        f'<title>{escape(card["name"])} 架構與資料流（依部署契約機械生成）</title>',
        _markers(mid),
        _box(ux, yc - uh / 2, uw, uh, GREEN, GREEN, "使用者", 14, "#ffffff"),
    ]
    cy0 = m + (inner - comp_h) / 2
    for i, (_, label) in enumerate(compute):
        parts.append(_box(cx0, cy0 + i * (ch + cgap), cw, ch, GREEN_FILL, GREEN, label, 13, INK))
    parts.append(f'<line x1="{ux + uw}" y1="{yc:g}" x2="{cx0 - 6}" y2="{yc:g}" '
                 f'stroke="{GREEN}" stroke-width="1.5" marker-end="url(#{mid}s)"/>')
    dy0 = m + (inner - right_h) / 2 if right_h else yc
    for i, (_, label, _short) in enumerate(data):
        by = dy0 + i * (dh + dgap)
        parts.append(_box(dx, by, dw, dh, "#ffffff", LINE, label, 12, INK))
        parts.append(f'<line x1="{cx0 + cw}" y1="{yc:g}" x2="{dx - 6}" y2="{by + dh / 2:g}" '
                     f'stroke="{LINE}" stroke-width="1.2" marker-end="url(#{mid}s)"/>')
    ey0 = dy0 + data_h + (14 if data_h else 0)
    trunk_x = (cx0 + cw + dx) / 2 - 5  # 計算節點右緣與資料欄之間的中繼豎線，避免穿盒
    for i, label in enumerate(ext):
        ry = ey0 + i * eh + eh / 2
        parts.append(f'<path d="M {cx0 + cw} {yc:g} L {trunk_x:g} {yc:g} L {trunk_x:g} {ry:g} '
                     f'L {w_total - 24} {ry:g}" '
                     f'fill="none" stroke="{DASH}" stroke-width="1.2" stroke-dasharray="5 4" '
                     f'marker-end="url(#{mid}d)"/>')
        parts.append(f'<text x="{w_total - 26}" y="{ry - 6:g}" text-anchor="end" '
                     f'font-size="11" fill="{MUTED}">{escape(label)}</text>')
    parts.append("</svg>")
    return "".join(parts)


def _svg_compact(card: dict) -> str:
    compute, data = _split_components(card)
    if not compute:
        compute = [("app", "服務")]
    w_total, m = 320, 10
    ux, uw, uh = 8, 58, 26
    cx0, cw, ch, cgap = 102, 84, 26, 6
    dx, dw, dh, dgap = 226, 86, 20, 5
    comp_h = len(compute) * ch + (len(compute) - 1) * cgap
    data_h = len(data) * dh + (len(data) - 1) * dgap if data else 0
    inner = max(comp_h, data_h, uh)
    height = inner + 2 * m
    yc = m + inner / 2
    mid = f"arwc-{card['id']}"
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w_total} {height:g}" role="img" '
        f'font-family="{FONT}" aria-label="{escape(card["name"])} 元件圖">',
        f'<title>{escape(card["name"])} 元件圖（依部署契約機械生成）</title>',
        _markers(mid),
        _box(ux, yc - uh / 2, uw, uh, GREEN, GREEN, "使用者", 11, "#ffffff"),
    ]
    cy0 = m + (inner - comp_h) / 2
    for i, (_, label) in enumerate(compute):
        parts.append(_box(cx0, cy0 + i * (ch + cgap), cw, ch, GREEN_FILL, GREEN, label, 11, INK))
    parts.append(f'<line x1="{ux + uw}" y1="{yc:g}" x2="{cx0 - 5}" y2="{yc:g}" '
                 f'stroke="{GREEN}" stroke-width="1.3" marker-end="url(#{mid}s)"/>')
    dy0 = m + (inner - data_h) / 2 if data_h else yc
    for i, (_, _full, short) in enumerate(data):
        by = dy0 + i * (dh + dgap)
        parts.append(_box(dx, by, dw, dh, "#ffffff", LINE, short, 10, INK))
        parts.append(f'<line x1="{cx0 + cw}" y1="{yc:g}" x2="{dx - 5}" y2="{by + dh / 2:g}" '
                     f'stroke="{LINE}" stroke-width="1" marker-end="url(#{mid}s)"/>')
    parts.append("</svg>")
    return "".join(parts)


def arch_svg(card: dict, compact: bool = False) -> str:
    """服務卡 → 內嵌用 SVG 字串。compact=True 為卡片牆小版（省外連與文字細節）。"""
    return _svg_compact(card) if compact else _svg_full(card)
