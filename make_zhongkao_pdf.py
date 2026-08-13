"""Generate 英语中考高频单词彩色背诵版(优化).pdf from entries_full.json."""
import json
import re
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

FONT_PATH = "/Library/Fonts/Arial Unicode.ttf"
FONT = "ArialUni"
pdfmetrics.registerFont(TTFont(FONT, FONT_PATH))

BLUE = HexColor("#1f5fa8")
GRAY = HexColor("#666666")
ROOT_COLOR = HexColor("#8B4513")

PAGE_W, PAGE_H = A4
MARGIN = 1.5 * cm
GUTTER = 0.8 * cm
COL_W = (PAGE_W - 2 * MARGIN - GUTTER) / 2

ROOT = Path(__file__).parent
SRC = ROOT / "intermediate" / "entries_full.json"
OUT = ROOT / "英语中考高频单词彩色背诵版(优化).pdf"

TITLE = "英语中考真题高频词汇"
SUBTITLE = "彩色背诵版 · top 688 · 按真题频次排序"
INTRO = (
    "中考高频词汇背诵版：\n"
    "共 688 词，按历年中考真题出现频次排序，分为 6 个 Section。\n"
    "包含音标、音节划分、词根（如有）、释义及例句。\n"
    "\n"
    "作者：yiyisheh@outlook.com\n"
    "GitHub：https://github.com/yiyisheh/CET4-vocabulary"
)


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def make_styles(accent):
    return {
        "word": ParagraphStyle("word", fontName=FONT, fontSize=11,
                               textColor=accent, spaceBefore=7, spaceAfter=1,
                               leading=13),
        "ipa": ParagraphStyle("ipa", fontName=FONT, fontSize=7.5,
                              textColor=GRAY, leading=10),
        "field": ParagraphStyle("field", fontName=FONT, fontSize=8.5,
                                leading=11.5),
        "root": ParagraphStyle("root", fontName=FONT, fontSize=8,
                               textColor=ROOT_COLOR, leading=10.5),
        "section": ParagraphStyle("section", fontName=FONT, fontSize=13,
                                  textColor=accent, alignment=1,
                                  spaceBefore=6, spaceAfter=14, leading=16),
        "title": ParagraphStyle("title", fontName=FONT, fontSize=26,
                                textColor=accent, alignment=1, leading=34),
        "sub": ParagraphStyle("sub", fontName=FONT, fontSize=12,
                              textColor=GRAY, alignment=1, leading=20),
        "intro": ParagraphStyle("intro", fontName=FONT, fontSize=10.5,
                                leading=19),
    }


def entry_flowables(e, st):
    blk = [Paragraph(f'<b>{e["rank"]}. {esc(e["word"])}</b>', st["word"])]

    uk = e.get("uk", "")
    us = e.get("us", "")
    if uk or us:
        blk.append(Paragraph(f'英[{esc(uk)}]  美[{esc(us)}]', st["ipa"]))

    syl = e.get("syl", "")
    if syl:
        blk.append(Paragraph(f'<b>音节</b>: {esc(syl)}', st["field"]))

    root = e.get("root")
    if root:
        blk.append(Paragraph(f'<b>词根</b>: {esc(root)}', st["root"]))

    d = e.get("def", "")
    if d:
        blk.append(Paragraph(f'<b>释义</b>: {esc(d)}', st["field"]))

    ex = e.get("ex", "")
    if ex:
        label = e.get("ex_label", "例句")
        blk.append(Paragraph(f'<b>{esc(label)}</b>: {esc(ex)}', st["field"]))

    blk.append(Spacer(1, 3))
    return KeepTogether(blk)


def build():
    st = make_styles(BLUE)

    def on_page(canvas, doc):
        canvas.setFont(FONT, 8)
        canvas.setFillColor(GRAY)
        canvas.drawCentredString(PAGE_W / 2, 0.8 * cm, str(doc.page))

    cover = Frame(MARGIN, MARGIN, PAGE_W - 2 * MARGIN, PAGE_H - 2 * MARGIN,
                  id="cover")
    body = [Frame(MARGIN, MARGIN, COL_W, PAGE_H - 2 * MARGIN, id="L"),
            Frame(MARGIN + COL_W + GUTTER, MARGIN, COL_W,
                  PAGE_H - 2 * MARGIN, id="R")]
    doc = BaseDocTemplate(
        str(OUT), pagesize=A4,
        pageTemplates=[PageTemplate(id="cover", frames=[cover]),
                       PageTemplate(id="body", frames=body, onPage=on_page)])

    story = [Spacer(1, 4 * cm),
             Paragraph(esc(TITLE), st["title"]),
             Spacer(1, 0.8 * cm),
             Paragraph(esc(SUBTITLE), st["sub"])]
    if INTRO:
        story.append(Spacer(1, 1.5 * cm))
        story.append(Paragraph(esc(INTRO).replace("\n", "<br/>"),
                               st["intro"]))
    story += [NextPageTemplate("body"), PageBreak()]

    with open(SRC, encoding="utf-8") as f:
        entries = json.load(f)

    cur_section = 0
    for e in entries:
        if e["section"] != cur_section:
            cur_section = e["section"]
            story.append(Paragraph(f"Section {cur_section}", st["section"]))
        story.append(entry_flowables(e, st))

    OUT.parent.mkdir(parents=True, exist_ok=True)
    doc.build(story)
    print(f"-> {OUT}")


if __name__ == "__main__":
    build()
