"""Render the 中考 optimized 背诵版 PDF from intermediate/entries_full.json.

由主项目 scripts/make_pdf_optimized.py 拷贝而来，仅改动数据路径、输出名与文案。

  * no 词频 line, no 变形 line
  * 释义 shown without the "释义:" label (just the text)
  * adds a 词根/词缀 block below the example (screenshot-style tags + summary)

Generates three PDFs:
  1. 彩色背诵版 — 有音节点（原版）
  2. 彩色打印版 — 无音节点
  3. 黑白打印版 — 无音节点
"""
import json
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor, black
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame,
                                Paragraph, Spacer, KeepTogether, PageBreak,
                                NextPageTemplate)

ROOT = Path(__file__).parent
DATA = json.loads((ROOT / "intermediate" / "entries_full.json").read_text())

FONT_PATH = "/Library/Fonts/Arial Unicode.ttf"
FONT = "ArialUni"
pdfmetrics.registerFont(TTFont(FONT, FONT_PATH))

BLUE = HexColor("#1f5fa8")
GRAY = HexColor("#666666")

PAGE_W, PAGE_H = A4
MARGIN = 1.5 * cm
GUTTER = 0.8 * cm
COL_W = (PAGE_W - 2 * MARGIN - GUTTER) / 2


def make_styles(accent, secondary):
    return {
        "word": ParagraphStyle("word", fontName=FONT, fontSize=11,
                               textColor=accent, spaceBefore=7, spaceAfter=1,
                               leading=13),
        "ipa": ParagraphStyle("ipa", fontName=FONT, fontSize=7.5,
                              textColor=secondary, leading=10),
        "field": ParagraphStyle("field", fontName=FONT, fontSize=8.5,
                                leading=11.5),
        "root": ParagraphStyle("root", fontName=FONT, fontSize=8, leading=11,
                               textColor=secondary, leftIndent=6),
        "rootsum": ParagraphStyle("rootsum", fontName=FONT, fontSize=8,
                                  leading=11, textColor=secondary, leftIndent=6,
                                  spaceBefore=1),
        "section": ParagraphStyle("section", fontName=FONT, fontSize=13,
                                  textColor=accent, alignment=1, spaceBefore=6,
                                  spaceAfter=14, leading=16),
        "title": ParagraphStyle("title", fontName=FONT, fontSize=26,
                                textColor=accent, alignment=1, leading=34),
        "sub": ParagraphStyle("sub", fontName=FONT, fontSize=12,
                              textColor=secondary, alignment=1, leading=20),
        "intro": ParagraphStyle("intro", fontName=FONT, fontSize=10.5,
                                leading=19),
    }


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def entry_block(e, st, use_syl):
    head = (e["syl"] or e["word"]) if use_syl else e["word"]
    blk = [Paragraph(f'<b>{e["rank"]}. {esc(head)}</b>', st["word"])]
    if e["uk"] or e["us"]:
        blk.append(Paragraph(f'英[{esc(e["uk"])}]&nbsp;&nbsp;美[{esc(e["us"])}]',
                             st["ipa"]))
    if e["def"]:
        blk.append(Paragraph(esc(e["def"]), st["field"]))
    if e["ex"]:
        blk.append(Paragraph(f'<b>{e["ex_label"]}</b>: {esc(e["ex"])}',
                             st["field"]))
    if e["root"]:
        for p in e["root"]["parts"]:
            tag = esc(p["type"])
            txt = esc(p["text"])
            mean = esc(p["meaning"])
            blk.append(Paragraph(
                f'{tag} <b>{txt}</b> = {mean}', st["root"]))
        if e["root"]["summary"]:
            blk.append(Paragraph(f'▸ {esc(e["root"]["summary"])}',
                                 st["rootsum"]))
    blk.append(Spacer(1, 3))
    return KeepTogether(blk)


INTRO_SYL = (
    "中考高频词汇背诵版（优化版）：\n"
    "共 688 词，按历年中考真题出现频次排序，分为 6 个 Section——\n"
    "· 词头改用音节点划分（如 dif·fer·ent），便于拼读；\n"
    "· 释义、例句取自真题；\n"
    "· 为可拆解的单词补充了「词根/词缀」助记块。\n"
    "\n"
    "词根拆解由 AI 生成，仅供助记参考。\n"
    "\n"
    "作者：yiyisheh@outlook.com\n"
    "GitHub：https://github.com/yiyisheh/ZK-vocabulary"
)

INTRO_NOSYL = (
    "中考高频词汇背诵版（优化版）：\n"
    "共 688 词，按历年中考真题出现频次排序，分为 6 个 Section——\n"
    "· 释义、例句取自真题；\n"
    "· 为可拆解的单词补充了「词根/词缀」助记块。\n"
    "\n"
    "词根拆解由 AI 生成，仅供助记参考。\n"
    "\n"
    "作者：yiyisheh@outlook.com\n"
    "GitHub：https://github.com/yiyisheh/ZK-vocabulary"
)


def build_pdf(out_path, st, subtitle, intro, use_syl):
    secondary = st["ipa"].textColor

    def on_page(canvas, doc):
        canvas.setFont(FONT, 8)
        canvas.setFillColor(secondary)
        canvas.drawCentredString(PAGE_W / 2, 0.8 * cm, str(doc.page))

    cover = Frame(MARGIN, MARGIN, PAGE_W - 2 * MARGIN, PAGE_H - 2 * MARGIN,
                  id="cover")
    body = [Frame(MARGIN, MARGIN, COL_W, PAGE_H - 2 * MARGIN, id="L"),
            Frame(MARGIN + COL_W + GUTTER, MARGIN, COL_W, PAGE_H - 2 * MARGIN,
                  id="R")]
    doc = BaseDocTemplate(
        str(out_path), pagesize=A4,
        pageTemplates=[PageTemplate(id="cover", frames=[cover]),
                       PageTemplate(id="body", frames=body, onPage=on_page)])

    story = [Spacer(1, 3.5 * cm),
             Paragraph("英语中考真题高频词汇", st["title"]),
             Spacer(1, 0.8 * cm),
             Paragraph(subtitle, st["sub"]),
             Spacer(1, 1.3 * cm),
             Paragraph(esc(intro).replace("\n", "<br/>"), st["intro"]),
             NextPageTemplate("body"), PageBreak()]

    last_section = None
    for e in DATA:
        if e["section"] != last_section:
            story.append(Paragraph(f'Section {e["section"]}', st["section"]))
            last_section = e["section"]
        story.append(entry_block(e, st, use_syl))
    doc.build(story)
    print(f"-> {out_path}")


def main():
    color_st = make_styles(BLUE, GRAY)
    bw_st = make_styles(black, GRAY)

    build_pdf(
        ROOT / "英语中考高频单词彩色背诵版(优化).pdf",
        color_st,
        "彩色背诵版（优化）· 含词根词缀 · top 688 · 按真题频次排序",
        INTRO_SYL,
        use_syl=True,
    )

    build_pdf(
        ROOT / "英语中考高频单词彩色打印版.pdf",
        color_st,
        "彩色打印版 · 含词根词缀 · top 688 · 按真题频次排序",
        INTRO_NOSYL,
        use_syl=False,
    )

    build_pdf(
        ROOT / "英语中考高频单词黑白打印版.pdf",
        bw_st,
        "黑白打印版 · 含词根词缀 · top 688 · 按真题频次排序",
        INTRO_NOSYL,
        use_syl=False,
    )


if __name__ == "__main__":
    main()
