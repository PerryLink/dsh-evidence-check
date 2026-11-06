#!/usr/bin/env python3
"""README visuals for dsh-evidence-check, derived from the shipped pipeline.

Both figures are read off the code, not off a generic checker template:

  `src/model.ts`          the column contract -- 12 alias groups for the rows,
                          6 for the header, and the `requireAnyOf` guard that
                          refuses material carrying none of the row columns.
  `src/shared/rows.ts`    the engine -- one `check.kind` per rule, findings
                          carrying `locator {row, field}` plus the
                          `found` / `expected` / `fix` triple, and `skip(reason)`
                          for a check that cannot run.
  `rules/evidence-check.yaml`
                          seven rules, three basis kinds, `values: []` on EV-003.
  `src/shared/ruleset.ts` `MAX_SEVERITY_BY_KIND`: direct is uncapped,
                          derived-from-principle <= warn,
                          institutional-configuration <= info.
  `src/view.ts`           the report the model reads: issues + skipped +
                          summary counts, and the fixed disclaimer.

Outputs (idempotent overwrite):
  docs/assets/dsh-evidence-check-hero-{zh,en}-{light,dark}.webp   1440x576, Pillow
  docs/assets/dsh-evidence-check-flow-v5-{light,dark}.svg         1100x660, hand-written SVG

Hero -- one evidence list, and the rules hung under the column each one reads.
    Left column: kicker / wordmark / two value lines / one subtitle / meta line
    / footer.  Right: the register itself -- a header band (caseNo, party) and
    six columns over three rows, with the cells the checker marks left visibly
    empty, duplicated or placeholder-filled.  Each rule hangs under its column
    via a bracket, so the picture reads "this column, this rule" instead of a
    row of arrows.  The footnote states the real scopes: 1 header rule, 5 row
    rules, 1 across-row rule (EV-005), and the reader's alias matching.

Flow -- grammar: FIELD-MOUNT MATRIX (a register grid with per-column rule
    brackets), not a left-to-right node chain.  The seven rules are mounted
    under the exact columns they read, each labelled with its `check.kind`;
    the header band carries the one header rule; EV-005 is the only rule that
    compares rows, so it gets the vertical dashed bracket.  The right card is
    the two channels the engine always produces: `issues[]` located by row +
    field, and `skipped[]` carrying a reason.  The bottom is a staircase of the
    three basis kinds and the severity cap each one imposes -- the pack's
    hardest invariant.  Labels are command-surface tokens only (field names,
    rule ids, check kinds, basis kinds, report fields) joined by middots — no
    prose, no Chinese — which is what lets all five README languages share the
    same pair.

The figures' numbers are the engine's own: the three-row list drawn in the flow
reports warn 5 / skipped 1 when run through the built plugin, which is the
summary printed on the report card.

Every label is measured before it is drawn; a label that would overflow aborts
the run instead of shipping clipped text.

Run once:  python scripts/gen-readme-assets.py
Requires:  Pillow, and the Windows fonts msyh.ttc / msyhbd.ttc / consola.ttf /
           consolab.ttf / segoeui.ttf / segoeuib.ttf.
"""
from __future__ import annotations

import os
import sys
from functools import lru_cache
from html import escape

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "docs", "assets")

NAME = "dsh-evidence-check"

FONTS = {
    "cjk": r"C:\Windows\Fonts\msyh.ttc",
    "cjk_b": r"C:\Windows\Fonts\msyhbd.ttc",
    "mono": r"C:\Windows\Fonts\consola.ttf",
    "mono_b": r"C:\Windows\Fonts\consolab.ttf",
    "en": r"C:\Windows\Fonts\segoeui.ttf",
    "en_b": r"C:\Windows\Fonts\segoeuib.ttf",
}
for _p in FONTS.values():
    if not os.path.exists(_p):
        sys.exit(f"FATAL: font missing: {_p}")

SKIN = {
    "light": dict(
        bg_from="#f9f6fd", bg_to="#e4eaf8", card="#ffffff", edge="#e3e0ee",
        text="#14161f", sub="#4d5261", faint="#8b90a0", accent="#4B67B4",
        accent_soft="#eceffa", warn="#b0490e", warn_soft="#fdf1e7",
        line="#e8e5f1", pill="#ece7f9", column="#f5f3fb",
        shadow=(38, 30, 72), glow=54,
    ),
    "dark": dict(
        bg_from="#131a2a", bg_to="#0c1016", card="#1b2231", edge="#2e374b",
        text="#f0f3f9", sub="#a8b1c4", faint="#788093", accent="#8496f5",
        accent_soft="#232c42", warn="#d29922", warn_soft="#2d2637",
        line="#242d3e", pill="#242d42", column="#1f2839",
        shadow=(0, 0, 0), glow=28,
    ),
}


# ----------------------------------------------------------------- primitives --
def hx(value: str) -> tuple[int, int, int]:
    value = value.lstrip("#")
    return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))


@lru_cache(maxsize=None)
def font(kind: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONTS[kind], size)


_SCRATCH = ImageDraw.Draw(Image.new("RGB", (8, 8)))


def mw(text: str, kind: str, size: int) -> float:
    return _SCRATCH.textlength(text, font=font(kind, size))


def fit_size(text: str, kind: str, max_w: float, size: int, floor: int) -> int:
    """Largest size <= `size` at which `text` fits in `max_w`."""
    while size > floor and mw(text, kind, size) > max_w:
        size -= 1
    return size


def require_width(text: str, kind: str, size: int, max_w: float, where: str) -> None:
    got = mw(text, kind, size)
    if got > max_w + 0.5:
        sys.exit(f"FATAL: {where}: {text!r} needs {got:.1f}px, only {max_w:.1f}px — refusing to clip")


def gradient(w: int, h: int, c1: str, c2: str) -> Image.Image:
    base = Image.new("RGB", (w, h))
    d = ImageDraw.Draw(base)
    a, b = hx(c1), hx(c2)
    for y in range(h):
        t = 0.25 * (y / h) + 0.75 * (y / h) ** 1.6
        d.line([(0, y), (w, y)], fill=tuple(int(p + (q - p) * t) for p, q in zip(a, b)))
    return base.convert("RGBA")


def glow(img: Image.Image, cx: int, cy: int, r: int, rgb: tuple[int, int, int],
         alpha: int, blur: int = 100) -> Image.Image:
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(layer).ellipse((cx - r, cy - r, cx + r, cy + r), fill=rgb + (alpha,))
    img.alpha_composite(layer.filter(ImageFilter.GaussianBlur(blur)))
    return img


def shadow(img: Image.Image, box: tuple[int, int, int, int], radius: int,
           rgb: tuple[int, int, int], alpha: int, blur: int, dy: int) -> None:
    x0, y0, x1, y1 = box
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(layer).rounded_rectangle(
        (x0, y0 + dy, x1, y1 + dy), radius, fill=rgb + (alpha,))
    img.alpha_composite(layer.filter(ImageFilter.GaussianBlur(blur)))


def card(img: Image.Image, box: tuple[int, int, int, int], radius: int, s: dict,
         blur: int = 16, dy: int = 9, alpha: int = 30) -> None:
    shadow(img, box, radius, s["shadow"], alpha, blur, dy)
    ImageDraw.Draw(img).rounded_rectangle(box, radius, fill=s["card"],
                                          outline=s["edge"], width=1)


def text(d: ImageDraw.ImageDraw, x: float, y: float, s: str, kind: str, size: int,
         fill: str, anchor: str = "lt") -> None:
    d.text((x, y), s, font=font(kind, size), fill=hx(fill), anchor=anchor)


def pill(img: Image.Image, x: float, y: float, label: str, s: dict, kind: str,
         size: int, h: int, fg: str | None = None, bg: str | None = None,
         edge: str | None = None, padx: float = 14) -> tuple[float, float]:
    d = ImageDraw.Draw(img)
    w = mw(label, kind, size) + padx * 2
    d.rounded_rectangle((x, y, x + w, y + h), h / 2, fill=hx(bg or s["pill"]),
                        outline=hx(edge) if edge else None, width=1)
    text(d, x + w / 2, y + h / 2, label, kind, size, fg or s["accent"], anchor="mm")
    return x + w, y + h


def hbracket(d: ImageDraw.ImageDraw, x0: float, x1: float, y: float, tick: float,
             color: str, width: int = 1) -> None:
    c = hx(color)
    d.line([(x0, y), (x1, y)], fill=c, width=width)
    for x in (x0, x1):
        d.line([(x, y), (x, y - tick)], fill=c, width=width)


def vdash(d: ImageDraw.ImageDraw, x: float, y0: float, y1: float, color: str,
          width: int = 1, dash: int = 5, gap: int = 4) -> None:
    c = hx(color)
    y = y0
    while y < y1:
        d.line([(x, y), (x, min(y + dash, y1))], fill=c, width=width)
        y += dash + gap


# --------------------------------------------------------------------- hero --
HERO = {
    "zh": dict(
        kicker="DeepSeek Harness 插件 · 清单核对",
        value=["七条规则，逐栏核对证据清单", "每条差异落到行号与栏名"],
        sub=["只列清单自身能逐条指认的差异，", "不判证据真伪，绝不改动原件。"],
        meta="evidence_check · EV-001…EV-007 · issues + skipped",
        foot="Apache-2.0 · 只读 · 不联网 · 不调用模型",
        sheet_title="证据清单",
        sheet_chip="只读",
        sheet_meta="案号（2026）某民初 1234 号 · 举证方 原告某某公司 · 3 行",
        header_label="表头",
        header_fields=[("caseNo", "（2026）某民初 1234 号"),
                       ("party", "原告某某公司")],
        header_rule=("EV-006", "headerPresence"),
        headers=["证据编号", "证据名称", "待证事实", "来源", "证据形式", "取得 / 提交日期"],
        rows=[
            ["证1", "", "", "", "书证", ("2026-04-01", "2026-03-02")],
            ["证1", "买卖合同原件", "双方签订合同", "原告留存", "书证",
             ("2025-03-10", "2026-03-02")],
            ["证3", "转账记录", "【待填】", "银行打印", "书证",
             ("2025-05-06", "2026-03-02")],
        ],
        # (row, column) cells the checker marks; column 5 marks the first date.
        marks=[(0, 1), (0, 2), (0, 3), (1, 0), (2, 2), (0, 5)],
        rules=[
            ("EV-005", "unique · rows", 0, 0, "A", "跨行"),
            ("EV-001", "presenceAny", 1, 2, "A", "至少一项"),
            ("EV-002", "presence", 3, 3, "A", "单行"),
            ("EV-004", "date", 5, 5, "A", "两栏比较"),
            ("EV-007", "containsAny", 2, 2, "B", "占位符"),
            ("EV-003", "enum · skipped", 4, 4, "B", "values 未配置"),
        ],
        scope_note="作用域 表头 ×1 · 单行 ×5 · 跨行 ×1（EV-005 行间比较编号）· 栏名匹配忽略大小写、空格、下划线与连字符",
        issue_rule="EV-001",
        issue_sev="warn",
        issue_locator="第 1 行 · 字段 claim",
        issue_found="claim、exhibitName 都为空",
        issue_expected="claim、exhibitName 至少应填写一项",
    ),
    "en": dict(
        kicker="DeepSeek Harness plugin · register check",
        value=["Seven rules, column by column,", "each difference lands on row + field"],
        sub=["Literal differences only — never a verdict on",
             "authenticity, and the original is never touched."],
        meta="evidence_check · EV-001…EV-007 · issues + skipped",
        foot="Apache-2.0 · read-only · no network · no model call",
        sheet_title="Exhibit list",
        sheet_chip="read-only",
        sheet_meta="caseNo (2026) Min Chu 1234 · party plaintiff Co. · 3 rows",
        header_label="header",
        header_fields=[("caseNo", "(2026) Min Chu 1234"), ("party", "plaintiff Co.")],
        header_rule=("EV-006", "headerPresence"),
        headers=["No.", "Exhibit", "Claim", "Source", "Form", "Obtained / submitted"],
        rows=[
            ["E-01", "", "", "", "doc", ("2026-04-01", "2026-03-02")],
            ["E-01", "contract", "goods sale", "kept by P", "doc",
             ("2025-03-10", "2026-03-02")],
            ["E-03", "slip", "TBD", "bank print", "doc",
             ("2025-05-06", "2026-03-02")],
        ],
        marks=[(0, 1), (0, 2), (0, 3), (1, 0), (2, 2), (0, 5)],
        rules=[
            ("EV-005", "unique", 0, 0, "A", "across rows"),
            ("EV-001", "presenceAny", 1, 2, "A", "at least one"),
            ("EV-002", "presence", 3, 3, "A", "per row"),
            ("EV-004", "date", 5, 5, "A", "two fields"),
            ("EV-007", "containsAny", 2, 2, "B", "placeholder"),
            ("EV-003", "enum · skipped", 4, 4, "B", "values unset"),
        ],
        scope_note="scopes: header ×1 · row ×5 · across rows ×1 (EV-005 compares numbers) · names matched ignoring case, spaces, _ and -",
        issue_rule="EV-001",
        issue_sev="warn",
        issue_locator="row 1 · field claim",
        issue_found="claim, exhibitName both empty",
        issue_expected="at least one of them filled",
    ),
}


def hero(lang: str, skin: str) -> None:
    s = SKIN[skin]
    h = HERO[lang]
    cjk = lang == "zh"
    bold = "cjk_b" if cjk else "en_b"
    body = "cjk" if cjk else "en"
    W, H = 1440, 576
    img = gradient(W, H, s["bg_from"], s["bg_to"])
    img = glow(img, 1120, 80, 430, hx(s["accent"]), s["glow"], 120)
    img = glow(img, 150, 600, 330, hx(s["accent"]), max(8, s["glow"] // 3), 120)
    d = ImageDraw.Draw(img)
    left_w = 604

    # ---- left column --------------------------------------------------------
    pill(img, 56, 54, h["kicker"], s, bold, 14, 32, fg=s["accent"])

    title_size = fit_size(NAME, "mono_b", left_w, 60, 48)
    require_width(NAME, "mono_b", title_size, left_w, "hero title")
    text(d, 54, 100, NAME, "mono_b", title_size, s["text"])

    value_size = fit_size(h["value"][0], bold, left_w, 34 if cjk else 31, 26)
    for line in h["value"]:
        require_width(line, bold, value_size, left_w, "hero value line")
    for i, line in enumerate(h["value"]):
        text(d, 56, 188 + i * 50, line, bold, value_size, s["text"])

    d.rounded_rectangle((56, 292, 124, 296), 2, fill=hx(s["accent"]))

    sub_size = 20 if cjk else 19
    for line in h["sub"]:
        require_width(line, body, sub_size, left_w, "hero subtitle")
    for i, line in enumerate(h["sub"]):
        text(d, 56, 320 + i * 30, line, body, sub_size, s["sub"])

    require_width(h["meta"], "mono", 16, left_w, "hero meta")
    text(d, 56, 404, h["meta"], "mono", 16, s["faint"])

    require_width(h["foot"], body, 15, left_w, "hero footer")
    text(d, 56, 496, h["foot"], body, 15, s["faint"])

    # ---- right: the register -----------------------------------------------
    box = (700, 44, 1384, 500)
    card(img, box, 22, s, blur=22, dy=12, alpha=26 if skin == "light" else 120)
    d = ImageDraw.Draw(img)
    ix0, ix1 = 726, 1354

    text(d, ix0, 68, h["sheet_title"], bold, 16, s["text"])
    text(d, ix1, 70, h["sheet_chip"], body, 11, s["faint"], anchor="rt")
    require_width(h["sheet_meta"], body, 12, ix1 - ix0 - 150, "hero sheet meta")
    text(d, ix0, 96, h["sheet_meta"], body, 12, s["sub"])

    # header band: one declaration, one header rule
    d.rounded_rectangle((ix0, 122, ix1, 164), 11, fill=hx(s["pill"]),
                        outline=hx(s["edge"]), width=1)
    text(d, ix0 + 12, 143, h["header_label"], body, 10, s["faint"], anchor="lm")
    fx = ix0 + 56
    for field, value in h["header_fields"]:
        w0 = mw(field, "mono", 10) + 14
        d.rounded_rectangle((fx, 130, fx + w0, 148), 5, fill=hx(s["card"]),
                            outline=hx(s["edge"]), width=1)
        text(d, fx + w0 / 2, 139, field, "mono", 10, s["accent"], anchor="mm")
        text(d, fx + w0 + 6, 146, value, body, 11.5, s["text"], anchor="lm")
        fx += w0 + 12 + mw(value, body, 11.5) + 22
    rule_id, rule_kind = h["header_rule"]
    chip_w = max(mw(rule_id, "mono_b", 11), mw(rule_kind, "mono", 9)) + 16
    cx1 = ix1 - 10
    d.rounded_rectangle((cx1 - chip_w, 130, cx1, 156), 8, fill=hx(s["accent_soft"]),
                        outline=hx(s["accent"]), width=1)
    text(d, cx1 - chip_w / 2, 138, rule_id, "mono_b", 11, s["accent"], anchor="mm")
    text(d, cx1 - chip_w / 2, 149, rule_kind, "mono", 9, s["sub"], anchor="mm")

    # columns + rows
    widths = [86, 120, 120, 92, 70, 140]
    xs = [ix0]
    for w in widths:
        xs.append(xs[-1] + w)
    assert xs[-1] <= ix1, xs[-1]

    d.rounded_rectangle((ix0, 174, xs[-1], 200), 8, fill=hx(s["column"]))
    for i, label in enumerate(h["headers"]):
        require_width(label, body, 11.5, widths[i] - 8, f"hero column {i}")
        text(d, xs[i] + 7, 187, label, body, 11.5, s["sub"], anchor="lm")

    row_h = 38
    y0 = 200
    for r, row in enumerate(h["rows"]):
        top = y0 + r * row_h
        for c in range(len(widths)):
            cx0, cx1 = xs[c] + 2, xs[c + 1] - 2
            marked = (r, c) in h["marks"] or (c == 5 and (r, 5) in h["marks"])
            if marked:
                d.rounded_rectangle((cx0, top + 4, cx1, top + row_h - 4), 6,
                                    fill=hx(s["warn_soft"]))
                d.rounded_rectangle((cx0, top + 4, cx0 + 3, top + row_h - 4), 1,
                                    fill=hx(s["warn"]))
        for c in range(len(widths)):
            value = row[c]
            cy = top + row_h / 2
            marked = (r, c) in h["marks"] or (c == 5 and (r, 5) in h["marks"])
            if c == 5:
                got, sub = value
                require_width(got, "mono", 10.5, widths[c] - 14, "hero date")
                text(d, xs[c] + 8, cy - 7, got, "mono", 10.5,
                     s["warn"] if marked else s["text"], anchor="lm")
                text(d, xs[c] + 8, cy + 8, sub, "mono", 10.5, s["faint"], anchor="lm")
            elif value == "":
                d.line([(xs[c] + 9, cy), (xs[c] + 21, cy)], fill=hx(s["faint"]), width=2)
            else:
                size = 12.5 if cjk else 12
                require_width(value, body, size, widths[c] - 12, f"hero cell {r},{c}")
                text(d, xs[c] + 8, cy, value, body, size, s["text"], anchor="lm")
        if r < len(h["rows"]) - 1:
            d.line([(ix0, top + row_h), (xs[-1], top + row_h)], fill=hx(s["edge"]))

    # across-row scope: EV-005 compares exhibit numbers between rows
    vdash(d, xs[0] + 4, y0 + 6, y0 + row_h * 2 - 6, s["warn"], 1)
    d.rounded_rectangle((xs[0] + 2, y0 + 6, xs[0] + 6, y0 + 10), 1, fill=hx(s["warn"]))

    # rule rail: each rule hangs under the column it reads
    table_bottom = y0 + row_h * len(h["rows"])
    rail_a = table_bottom + 12
    rail_b = table_bottom + 52
    spans = [(c_from, c_to) for (_r, _k, c_from, c_to, _l, _t) in h["rules"]
             if c_from != c_to]
    for rule_id, kind, c_from, c_to, lane, tag in h["rules"]:
        cx_a, cx_b = xs[c_from], xs[c_to + 1]
        lane_y = rail_a if lane == "A" else rail_b
        bw = max(mw(rule_id, "mono_b", 11.5), mw(kind, "mono", 9)) + 14
        bw = max(bw, 88)
        center = (cx_a + cx_b) / 2
        chip_x0 = max(xs[0], min(center - bw / 2, xs[-1] - bw))
        covered = any(a <= c_to and c_from <= b for a, b in spans)
        if c_from != c_to:
            # one bracket for a rule that holds two columns together
            hbracket(d, cx_a + 3, cx_b - 3, table_bottom + 6, 6, s["sub"])
            leader_top = table_bottom + 6
        else:
            # a single column inside another rule's bracket starts below it,
            # so the two connectors never cross
            leader_top = table_bottom + 11 if covered else table_bottom + 2
        if c_from == c_to and covered:
            # shift the leader to the right half of the column so it cannot
            # run through the chip of the bracket above it
            leader_x = min(chip_x0 + bw - 20, cx_b - 24)
        else:
            leader_x = max(chip_x0 + 10, min(center, chip_x0 + bw - 10))
        d.line([(leader_x, leader_top), (leader_x, lane_y)], fill=hx(s["sub"]))
        skipped = "skipped" in kind
        d.rounded_rectangle((chip_x0, lane_y, chip_x0 + bw, lane_y + 34), 9,
                            fill=hx(s["warn_soft"] if skipped else s["accent_soft"]),
                            outline=hx(s["warn"] if skipped else s["accent"]), width=1)
        text(d, chip_x0 + bw / 2, lane_y + 10, rule_id, "mono_b", 11.5,
             s["warn"] if skipped else s["accent"], anchor="mm")
        text(d, chip_x0 + bw / 2, lane_y + 24, kind, "mono", 9, s["sub"], anchor="mm")

    require_width(h["scope_note"], body, 11, ix1 - ix0, "hero scope note")
    text(d, ix0, table_bottom + 100, h["scope_note"], body, 11, s["sub"])

    # the finding the run produces: rule, severity, row + field, then what the
    # cells say against what the rule asks for
    sy0, sy1 = table_bottom + 112, 482
    d.rounded_rectangle((ix0, sy0, ix1, sy1), 12, fill=hx(s["accent_soft"]),
                        outline=hx(s["accent"]), width=1)
    fy = sy0 + 21
    text(d, ix0 + 14, fy, h["issue_rule"], "mono_b", 12, s["accent"], anchor="lm")
    sev_w = mw(h["issue_sev"], "mono", 9) + 14
    sx = ix0 + 14 + mw(h["issue_rule"], "mono_b", 12) + 10
    d.rounded_rectangle((sx, fy - 9, sx + sev_w, fy + 9), 9, fill=hx(s["warn_soft"]),
                        outline=hx(s["warn"]), width=1)
    text(d, sx + sev_w / 2, fy, h["issue_sev"], "mono", 9, s["warn"], anchor="mm")
    text(d, sx + sev_w + 12, fy, h["issue_locator"], body, 11.5, s["text"], anchor="lm")
    # the two cells the engine reports, and what the rule asked for instead
    found_w = mw(h["issue_found"], body, 11.5)
    text(d, ix0 + 14, fy + 20, h["issue_found"], body, 11.5, s["sub"], anchor="lm")
    text(d, ix0 + 14 + found_w + 10, fy + 20, "→", body, 11.5, s["accent"], anchor="lm")
    text(d, ix0 + 14 + found_w + 30, fy + 20, h["issue_expected"], body, 11.5,
         s["text"], anchor="lm")
    if ix0 + 14 + found_w + 30 + mw(h["issue_expected"], body, 11.5) > ix1 - 12:
        sys.exit("FATAL: hero finding strip overflows")

    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, f"{NAME}-hero-{lang}-{skin}.webp")
    img.convert("RGB").save(path, "WEBP", quality=90, method=6)
    print(f"wrote {os.path.relpath(path, ROOT)}")


# --------------------------------------------------------------------- flow --
# The flow text is language-neutral: field names, rule ids, check kinds, basis
# kinds and report fields joined by middots. That is what lets the same pair
# serve all five README languages, and it keeps the diagram a specification
# rather than a caption.
SVG = {
    "light": dict(bg="#f9f6fd", bg2="#e4eaf8", card="#ffffff", edge="#e3e0ee",
                  text="#15161f", sub="#4f5463", faint="#8b90a0", accent="#4B67B4",
                  accent_soft="#eceffa", warn="#b0490e", warn_soft="#fdf1e7",
                  line="#e8e5f1", pill="#ece7f9", column="#f5f3fb"),
    "dark": dict(bg="#131a2a", bg2="#0c1016", card="#1b2231", edge="#2e374b",
                 text="#f1f4fa", sub="#a9b2c5", faint="#788093", accent="#8496f5",
                 accent_soft="#232c42", warn="#d29922", warn_soft="#2d2637",
                 line="#242d3e", pill="#242d42", column="#1f2839"),
}

MONO_STACK = "ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"
SANS_STACK = "ui-sans-serif,system-ui,-apple-system,Segoe UI,sans-serif"


def svg_width(text: str, size: float, mono: bool) -> float:
    """Conservative advance width, measured with the closest local font."""
    kind = "mono" if mono else "en"
    return mw(text, kind, int(round(size))) * 1.06


class Fig:
    def __init__(self, skin: str):
        self.s = SVG[skin]
        self.parts: list[str] = []

    # -- raw helpers ---------------------------------------------------------
    def add(self, markup: str) -> None:
        self.parts.append(markup)

    def text(self, x: float, y: float, content: str, size: float, fill: str,
             mono: bool = True, weight: int = 400, anchor: str = "start",
             opacity: float = 1.0) -> None:
        family = MONO_STACK if mono else SANS_STACK
        extra = f' opacity="{opacity}"' if opacity < 1 else ""
        self.add(
            f'<text x="{x:.1f}" y="{y:.1f}" font-family="{family}" '
            f'font-size="{size}" font-weight="{weight}" fill="{fill}"'
            f' text-anchor="{anchor}"{extra}>{escape(content)}</text>')

    def rect(self, x: float, y: float, w: float, h: float, radius: float,
             fill: str, stroke: str | None = None, width: float = 1,
             dash: str | None = None) -> None:
        stroke_attr = f' stroke="{stroke}" stroke-width="{width}"' if stroke else ""
        dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
        self.add(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" '
                 f'rx="{radius}" fill="{fill}"{stroke_attr}{dash_attr}/>')

    def line(self, x1: float, y1: float, x2: float, y2: float, stroke: str,
             width: float = 1, dash: str | None = None) -> None:
        dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
        self.add(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
                 f'stroke="{stroke}" stroke-width="{width}"{dash_attr}/>')

    def path(self, d: str, stroke: str, width: float = 1, fill: str = "none") -> None:
        self.add(f'<path d="{d}" fill="{fill}" stroke="{stroke}" '
                 f'stroke-width="{width}" stroke-linecap="round"/>')

    # -- composed ------------------------------------------------------------
    def chip(self, x: float, y: float, h: float, label: str, size: float, fg: str,
             bg: str, stroke: str | None, width: float | None = None,
             mono: bool = True, weight: int = 400, padx: float = 9) -> float:
        need = svg_width(label, size, mono) + padx * 2
        cw = width if width is not None else need
        if need > cw + 0.5:
            sys.exit(f"FATAL: flow chip {label!r} needs {need:.1f}px, box is {cw:.1f}px")
        self.rect(x, y, cw, h, h / 2, bg, stroke, 1)
        self.text(x + cw / 2, y + h / 2 + size * 0.35, label, size, fg, mono,
                  weight, "middle")
        return cw

    def two_line_chip(self, x: float, y: float, w: float, h: float, top: str,
                      bottom: str, accent: str, bg: str, skipped: bool) -> None:
        dash = "4 3" if skipped else None
        self.rect(x, y, w, h, 8, bg, accent, 1, dash)
        for line, size, fill, dy in (
            (top, 13.5, accent, 14.5),
            (bottom, 10, self.s["sub"], 27.5),
        ):
            need = svg_width(line, size, True)
            if need > w - 8:
                sys.exit(f"FATAL: flow chip line {line!r} needs {need:.1f}px in {w:.1f}px")
            self.text(x + w / 2, y + dy + size * 0.35, line, size, fill, True, 700,
                      "middle")


def flow_svg(skin: str) -> str:
    s = SVG[skin]
    W, H = 1100, 660
    f = Fig(skin)

    f.add(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
          f'viewBox="0 0 {W} {H}" role="img" '
          f'aria-labelledby="fig-title fig-desc">')
    f.add('<title id="fig-title">dsh-evidence-check structure: one evidence list, '
          'seven rules mounted on the fields they read</title>')
    f.add('<desc id="fig-desc">A register (header plus rows and columns) is read '
          'with alias matching and a requireAnyOf guard; the seven rules hang '
          'under the exact columns they read, with EV-006 on the header band and '
          'EV-005 the only across-row rule; results leave as issues located by '
          'row and field plus skipped entries carrying a reason; a staircase '
          'shows the severity cap each basis kind imposes.</desc>')
    f.add('<defs><linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">'
          f'<stop offset="0" stop-color="{s["bg"]}"/>'
          f'<stop offset="1" stop-color="{s["bg2"]}"/></linearGradient></defs>')
    f.rect(0, 0, W, H, 20, "url(#bg)")

    # ---- title strip --------------------------------------------------------
    f.text(36, 40, f"{NAME} · structure", 17, s["text"], False, 700)
    right = "evidence_check · rules/evidence-check.yaml · 7 rules · validated on load"
    if svg_width(right, 11, True) > 620:
        sys.exit("FATAL: flow title right token overflows")
    f.text(1064, 40, right, 11, s["faint"], True, 400, "end")

    # ---- card 1: the material ----------------------------------------------
    mx0, mx1 = 32, 672
    my0, my1 = 62, 452
    f.rect(mx0, my0, mx1 - mx0, my1 - my0, 18, s["card"], s["edge"], 1)
    f.text(mx0 + 16, my0 + 26, "MATERIAL", 12, s["accent"], True, 700)
    f.text(mx0 + 82, my0 + 26, "parseMaterial · one list, header + rows × columns",
           11, s["sub"], False)
    f.text(mx1 - 16, my0 + 26, "JSON / YAML", 10.5, s["faint"], True, 400, "end")

    # header band: declared once, checked by the one header rule
    f.rect(mx0 + 16, my0 + 38, mx1 - mx0 - 32, 40, 10, s["pill"], s["edge"], 1)
    f.text(mx0 + 28, my0 + 62, "HEADER", 9, s["faint"], True, 700)
    hx_ = mx0 + 78
    for field in ("caseNo", "party"):
        w = f.chip(hx_, my0 + 47, 22, field, 10, s["accent"], s["card"],
                   s["edge"], padx=7)
        hx_ += w + 14
    f.text(hx_ + 4, my0 + 62, "declared once for the whole list", 9.5,
           s["faint"], False)
    hw = f.chip(mx1 - 16 - 176, my0 + 45, 26, "EV-006 · headerPresence", 9.5,
                s["accent"], s["accent_soft"], s["accent"], 176)
    if hx_ + 4 + svg_width("declared once for the whole list", 9.5, False) > mx1 - 16 - 176 - 6:
        sys.exit("FATAL: flow header chips collide")

    # table
    cols = [86, 90, 92, 82, 64, 94, 94]
    xs = [mx0 + 16]
    for w in cols:
        xs.append(xs[-1] + w)
    if xs[-1] > mx1 - 16 + 0.5:
        sys.exit(f"FATAL: flow table runs past the card: {xs[-1]:.1f}")
    top = my0 + 92
    f.rect(mx0 + 16, top, xs[-1] - mx0 - 16, 28, 8, s["column"])
    headers = ["exhibitNo", "exhibitName", "claim", "source", "form",
               "obtainedAt", "submittedAt"]
    for i, label in enumerate(headers):
        need = svg_width(label, 11.5, True)
        if need > cols[i] - 8:
            sys.exit(f"FATAL: flow header {label!r} needs {need:.1f}px of {cols[i]}")
        f.text(xs[i] + 6, top + 18.5, label, 11.5, s["sub"], True)

    rows = [
        ["E-01", "", "", "", "doc", "2026-04-01", "2026-03-02"],
        ["E-01", "contract", "goods sale", "kept by P", "doc",
         "2025-03-10", "2026-03-02"],
        ["E-03", "slip", "TBD", "bank print", "doc",
         "2025-05-06", "2026-03-02"],
    ]
    marked = {(0, 1), (0, 2), (0, 3), (1, 0), (2, 2), (0, 5)}
    row_h = 44
    ry = top + 28
    for r, row in enumerate(rows):
        rt = ry + r * row_h
        for c, value in enumerate(row):
            cx0, cx1 = xs[c] + 2, xs[c + 1] - 2
            if (r, c) in marked:
                f.rect(cx0, rt + 5, cx1 - cx0, row_h - 10, 6, s["warn_soft"])
                f.rect(cx0, rt + 5, 3, row_h - 10, 1.5, s["warn"])
            if value == "":
                f.line(cx0 + 9, rt + row_h / 2, cx0 + 19, rt + row_h / 2,
                       s["faint"], 2)
                continue
            size = 12.5
            need = svg_width(value, size, False)
            if need > cols[c] - 12:
                sys.exit(f"FATAL: flow cell {value!r} needs {need:.1f}px of {cols[c]}")
            f.text(xs[c] + 7, rt + row_h / 2 + 4.2, value, size,
                   s["warn"] if (r, c) in marked and c == 5 else s["text"], False)
        if r < len(rows) - 1:
            f.line(mx0 + 16, rt + row_h, xs[-1], rt + row_h, s["line"])
    # across-row scope: EV-005 is the only rule comparing rows
    f.line(xs[0] + 5, ry + 8, xs[0] + 5, ry + row_h * 2 - 6, s["warn"], 1.2, "5 4")

    table_bottom = ry + row_h * len(rows)

    # ---- rule rail ----------------------------------------------------------
    bracket_y = table_bottom + 10
    rail_a = table_bottom + 16
    rail_b = table_bottom + 58
    chips = [
        # (rule, kind, first col, last col, lane)
        ("EV-005", "unique · rows", 0, 0, "A"),
        ("EV-001", "presenceAny", 1, 2, "A"),
        ("EV-002", "presence", 3, 3, "A"),
        ("EV-004", "date", 5, 6, "A"),
        ("EV-007", "containsAny", 2, 2, "B"),
        ("EV-003", "enum · skipped", 4, 4, "B"),
    ]
    occupied: dict[str, list[tuple[float, float]]] = {"A": [], "B": []}
    spans = [(c_from, c_to) for (_r, _k, c_from, c_to, _l) in chips
             if c_from != c_to]
    for rule_id, kind, c_from, c_to, lane in chips:
        lane_y = rail_a if lane == "A" else rail_b
        bw = 100
        center = (xs[c_from] + xs[c_to + 1]) / 2
        x0 = max(xs[0], min(center - bw / 2, xs[-1] - bw))
        for lo, hi in occupied[lane]:
            if x0 < hi + 8 and lo < x0 + bw + 8:
                x0 = hi + 10
        occupied[lane].append((x0, x0 + bw))
        skipped = "skipped" in kind
        covered = any(a <= c_to and c_from <= b for a, b in spans)
        if c_from != c_to:
            # a rule that holds two columns together gets the bracket
            f.line(xs[c_from] + 3, table_bottom + 2, xs[c_from] + 3,
                   bracket_y, s["sub"], 1)
            f.line(xs[c_to + 1] - 3, table_bottom + 2, xs[c_to + 1] - 3,
                   bracket_y, s["sub"], 1)
            f.line(xs[c_from] + 3, bracket_y, xs[c_to + 1] - 3, bracket_y,
                   s["sub"], 1)
            leader_top = bracket_y
        else:
            leader_top = bracket_y + 5 if covered else table_bottom + 2
        if c_from == c_to and covered:
            # right half of the column: the bracket's chip sits above the
            # centre, so a centred leader would run through it
            leader_x = min(x0 + bw - 20, xs[c_to + 1] - 24)
        else:
            leader_x = max(x0 + 10, min(center, x0 + bw - 10))
        f.line(leader_x, leader_top, leader_x, lane_y, s["sub"], 1)
        f.two_line_chip(x0, lane_y, bw, 34, rule_id, kind,
                        s["warn"] if skipped else s["accent"],
                        s["warn_soft"] if skipped else s["accent_soft"], skipped)

    f.text(mx0 + 16, table_bottom + 106,
           "RULES · runCheck · each rule hangs on the field it reads", 10,
           s["accent"], True, 700)
    f.text(mx0 + 16, table_bottom + 120,
           "column names match ignoring case, spaces, _ and - ; "
           "requireAnyOf guard on the row columns", 10, s["faint"], True)

    # ---- card 2: the report -------------------------------------------------
    rx0, rx1 = 688, 1068
    ry0, ry1 = 62, 452
    f.rect(rx0, ry0, rx1 - rx0, ry1 - ry0, 18, s["card"], s["edge"], 1)
    f.text(rx0 + 16, ry0 + 26, "REPORT", 12, s["accent"], True, 700)
    f.text(rx1 - 16, ry0 + 26, "buildView · issues + skipped", 10.5, s["faint"], True, 400, "end")

    cx = rx0 + 16
    for label, value, colour in (("error", "0", s["sub"]), ("warn", "5", s["warn"]),
                                 ("info", "0", s["sub"]), ("skipped", "1", s["sub"])):
        need = svg_width(f"{label} {value}", 10, True) + 18
        f.chip(cx, ry0 + 36, 20, f"{label} {value}", 10, colour, s["pill"],
               s["edge"], need)
        cx += need + 6

    f.text(rx0 + 16, ry0 + 84, "issues[] · located by row + field", 10.5,
           s["accent"], True, 700)
    f.rect(rx0 + 16, ry0 + 92, rx1 - rx0 - 32, 92, 10, s["accent_soft"])
    f.text(rx0 + 26, ry0 + 112, "EV-001", 11.5, s["accent"], True, 700)
    f.chip(rx0 + 76, ry0 + 100, 18, "warn", 9.5, s["warn"], s["warn_soft"],
           s["warn"], 46)
    f.text(rx0 + 128, ry0 + 112, "row 1 · field claim", 10.5, s["text"], True)
    for i, (label, value) in enumerate((
        ("found", "claim, exhibitName both empty"),
        ("expected", "at least one of them filled"),
        ("fix", "fill the name and the fact it proves"),
    )):
        y = ry0 + 132 + i * 16
        f.text(rx0 + 26, y, label, 10, s["faint"], True)
        if svg_width(value, 10.5, True) > rx1 - 16 - (rx0 + 88) - 8:
            sys.exit(f"FATAL: flow issue line {value!r} overflows")
        f.text(rx0 + 88, y, value, 10.5, s["sub"], True)

    more = [
        ("EV-002", "row 1 · field source"),
        ("EV-004", "row 1 · field obtainedAt"),
        ("EV-005", "row 2 · field exhibitNo"),
        ("EV-007", "row 3 · field claim"),
    ]
    for i, (rule, where) in enumerate(more):
        y = ry0 + 204 + i * 18
        f.text(rx0 + 16, y, rule, 10.5, s["text"], True, 700)
        f.text(rx0 + 62, y, where, 10.5, s["faint"], True)

    f.text(rx0 + 16, ry0 + 294, "skipped[] · a check that cannot run names why",
           10.5, s["accent"], True, 700)
    f.rect(rx0 + 16, ry0 + 302, rx1 - rx0 - 32, 62, 10, s["warn_soft"], s["warn"], 1, "4 3")
    f.text(rx0 + 26, ry0 + 322, "EV-003", 11, s["warn"], True, 700)
    f.text(rx0 + 26, ry0 + 340, "values unset: the form vocabulary is", 10.5,
           s["sub"], True)
    f.text(rx0 + 26, ry0 + 354, "institutional, the engine hard-codes none",
           10.5, s["sub"], True)
    f.text(rx0 + 16, ry0 + 382, "id = plugin.ruleId.locatorHash", 9.5,
           s["faint"], True)

    # ---- bottom band: caps staircase + the boundaries -----------------------
    f.text(36, 484, "CAPS · severity follows the basis", 11, s["accent"], True, 700)
    rungs = [
        ("direct", "no cap · this pack: warn", "EV-001  EV-002", 36, 500),
        ("derived-from-principle", "cap warn", "EV-004  EV-005  EV-006  EV-007", 52, 484),
        ("institutional-configuration", "cap info", "EV-003", 68, 468),
    ]
    for i, (kind, cap, rules, x, w) in enumerate(rungs):
        y = 494 + i * 30
        f.rect(x, y, w, 24, 7, s["accent_soft"], s["edge"], 1)
        f.text(x + 9, y + 16.5, kind, 10.5, s["accent"], True, 700)
        f.text(x + 9 + svg_width(kind, 10.5, True) + 12, y + 16.5, cap, 10.5,
               s["sub"], True)
        f.text(x + w - 9, y + 16.5, rules, 10, s["faint"], True, 400, "end")
        if svg_width(rules, 10, True) > w - 260:
            sys.exit(f"FATAL: flow cap rung {kind!r} rule list overflows")

    f.text(576, 484, "WHAT IT NEVER DOES", 11, s["accent"], True, 700)
    never = [
        "skipped is not a pass — a check that cannot run names its reason",
        "no verdict — found / expected / fix, never “compliant”",
        "source read-only · no network · no model call",
    ]
    for i, line in enumerate(never):
        y = 506 + i * 22
        f.add(f'<circle cx="580" cy="{y - 3.5}" r="2.4" fill="{s["accent"]}"/>')
        f.text(590, y, line, 10.5, s["sub"], True)

    f.text(36, 626, "Apache-2.0 · pure ESM · no native code · native and ptc "
                    "tool modes · issues sorted by severity, rule id, locator",
           9.5, s["faint"], True)

    f.add("</svg>")
    return "\n".join(f.parts) + "\n"


# --------------------------------------------------------------------- main --
def main() -> None:
    os.makedirs(OUT, exist_ok=True)
    for lang in ("zh", "en"):
        for skin in ("light", "dark"):
            hero(lang, skin)
    for skin in ("light", "dark"):
        path = os.path.join(OUT, f"{NAME}-flow-v5-{skin}.svg")
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(flow_svg(skin))
        print(f"wrote {os.path.relpath(path, ROOT)}")


if __name__ == "__main__":
    main()
