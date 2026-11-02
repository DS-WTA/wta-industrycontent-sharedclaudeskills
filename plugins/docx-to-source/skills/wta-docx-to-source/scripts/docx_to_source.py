#!/usr/bin/env python3
"""
WiseTech Academy: Word script (.docx) -> DIY page source code (.html fragment)

Usage:
    python3 docx_to_source.py <script.docx> [-o OUT_DIR] [--ext png] [--cdn https://cdn.wisetechacademy.com]

Output: <CODE>.html  (paste into the DIY editor's source-code view)
Prints a CHECK list to stdout (placeholders, skipped items) for the LD.

Widget detection is driven by the text of the FIRST cell of each script table
("Image", "Graphic", "Call-out", "Scroll animator", "Image hotspot", "Marker N",
"HTML import", "List block", "Question", "Category", "Glossary term", "Text reveal",
"Card N", "Expander", "Video", "Code", ...). Label cells are the blue-shaded cells;
value cells are unshaded / white. Both the older ("Graphic") and newer ("Image")
template versions are supported.
"""
import argparse, html, os, re, sys
import docx
from docx.table import Table
from docx.text.paragraph import Paragraph
from docx.text.hyperlink import Hyperlink
from docx.oxml.ns import qn

CDN = "https://cdn.wisetechacademy.com"
DEFAULT_EXT = "png"
WIDGET_ICON_EXT = "svg"   # scroll animator + text reveal images are SVG uploads
CHECKS = []          # messages for the LD
def check(msg):
    CHECKS.append(msg)

# ── Callout class mapping (edit here if the team's mapping changes) ─────────────
CALLOUT_TYPE_CLASS = [                       # Call-out table "Type" value -> class
    (r"danger|red|warning|important", "alert-danger"),
    (r"success|green|tip", "alert-success"),
    (r"primary|blue|note|info", "alert-primary"),
    (r"highlight|grey|gray", "highlight-box"),
]
CALLOUT_STYLE_CLASS = [                      # Callout paragraph style -> class
    (r"pale blue", "alert-primary"),
    (r"pale grey|pale gray", "alert-primary"),
    (r"red", "alert-danger"),
    (r"green", "alert-success"),
]
DEFAULT_CALLOUT = "alert-primary"
# Blue/grey callouts whose label line contains "case study" become <div class="case-study">
CASE_STUDY_FROM = ("alert-primary", "highlight-box")

INSTRUCTION_PATTERNS = [r"^please (write|complete|add)", r"^add quick quiz", r"^diy\s*:", r"^\[.*\]$"]
STOP_HEADINGS = [r"^assessment questions?$", r"^glossary$", r"^final assessment"]

# ── helpers ─────────────────────────────────────────────────────────────────────
def esc(t):
    return html.escape(t, quote=False)

def esc_attr(t):
    return html.escape(t, quote=True)

def norm(t):
    return re.sub(r"\s+", " ", (t or "").replace("*", "")).strip().lower()

def cell_fill(tc):
    f = tc.xpath("./w:tcPr/w:shd/@w:fill")
    return f[0].upper() if f else ""

def is_label(tc):
    f = cell_fill(tc)
    return bool(f) and f not in ("AUTO", "FFFFFF")

def num_format(doc, p):
    """Return 'ol' / 'ul' / None for a paragraph, plus its list level."""
    numPr = p._p.find(qn("w:pPr") + "/" + qn("w:numPr")) if p._p.pPr is not None else None
    style = (p.style.name or "").lower() if p.style is not None else ""
    if numPr is None:
        if "bullet" in style:
            return "ul", (1 if "2" in style else 0)
        if "number" in style or "list number" in style:
            return "ol", 0
        return None, 0
    ilvl_el = numPr.find(qn("w:ilvl")); numId_el = numPr.find(qn("w:numId"))
    ilvl = int(ilvl_el.get(qn("w:val"))) if ilvl_el is not None else 0
    numId = numId_el.get(qn("w:val")) if numId_el is not None else None
    if numId in (None, "0"):
        return None, 0
    kind = "ol" if "number" in style else "ul"
    try:
        numbering = doc.part.numbering_part.element
        num = numbering.xpath(f'./w:num[@w:numId="{numId}"]')
        if num:
            absId = num[0].xpath("./w:abstractNumId/@w:val")[0]
            fmt = numbering.xpath(f'./w:abstractNum[@w:abstractNumId="{absId}"]/w:lvl[@w:ilvl="{ilvl}"]/w:numFmt/@w:val')
            if fmt:
                kind = "ul" if fmt[0] in ("bullet", "none") else "ol"
    except Exception:
        pass
    return kind, ilvl

def run_html(run):
    parts = []
    for child in run._r.iterchildren():
        tag = child.tag.split("}")[1]
        if tag == "t":
            parts.append(esc(child.text or ""))
        elif tag in ("br", "cr"):
            parts.append("<br>")
        elif tag == "tab":
            parts.append(" ")
    t = "".join(parts)
    if not t.strip("<br> "):
        return t
    if run.italic:
        t = f"<em>{t}</em>"
    if run.bold:
        t = f"<strong>{t}</strong>"
    if run.font.superscript:
        t = f"<sup>{t}</sup>"
    if run.font.subscript:
        t = f"<sub>{t}</sub>"
    return t

def inline_html(p):
    out = []
    for item in p.iter_inner_content():
        if isinstance(item, Hyperlink):
            inner = "".join(run_html(r) for r in item.runs)
            addr = item.address or ""
            if item.fragment:
                addr = (addr + "#" + item.fragment) if addr else "#" + item.fragment
            out.append(f'<a href="{esc_attr(addr)}" target="_blank" rel="noopener">{inner}</a>' if addr else inner)
        else:
            out.append(run_html(item))
    h = "".join(out)
    h = re.sub(r"</strong><strong>", "", h)
    h = re.sub(r"</em><em>", "", h)
    h = re.sub(r"^(<br>\s*)+|(\s*<br>)+$", "", h.strip())
    return h.strip()

def para_is_image_only(p):
    return (not p.text.strip()) and bool(p._p.xpath(".//w:drawing"))

def render_paras(doc, paras, title_first=False, title_tag="h3"):
    """Render a list of Paragraphs to HTML blocks (p / h / ul / ol)."""
    out = []; list_stack = []   # stack of (kind, level)
    def close_lists(to_level=-1):
        while list_stack and list_stack[-1][1] > to_level:
            out.append(f"</li></{list_stack.pop()[0]}>")
    paras = [p for p in paras if p.text.strip()]
    for i, p in enumerate(paras):
        style = (p.style.name or "") if p.style is not None else ""
        content = inline_html(p)
        if not content:
            continue
        kind, lvl = num_format(doc, p)
        m = re.match(r"heading (\d)", style.lower())
        if kind:
            if list_stack and list_stack[-1][1] == lvl and list_stack[-1][0] == kind:
                out.append(f"</li><li>{content}")
            elif list_stack and list_stack[-1][1] >= lvl:
                close_lists(lvl)
                if list_stack and list_stack[-1][1] == lvl:
                    out.append(f"</li><li>{content}")
                else:
                    out.append(f"<{kind}><li>{content}"); list_stack.append((kind, lvl))
            else:
                out.append(f"<{kind}><li>{content}"); list_stack.append((kind, lvl))
            continue
        close_lists()
        if m:
            lvl_h = max(2, min(int(m.group(1)), 5))
            out.append(f"<h{lvl_h}>{esc(p.text.strip())}</h{lvl_h}>")
        elif title_first and i == 0 and len(paras) > 1 and len(p.text.split()) <= 8 and not re.search(r"[.?!:;,]$", p.text.strip()):
            plain = esc(p.text.strip())
            out.append(f"<{title_tag}>{plain}</{title_tag}>" if title_tag.startswith("h") else f"<p><strong>{plain}</strong></p>")
        else:
            out.append(f"<p>{content}</p>")
    close_lists()
    h = "\n".join(out)
    return re.sub(r"\n(</li>)", r"\1", h)

def case_study_fix(block):
    """Blue/grey callout whose first line mentions 'case study' -> <div class="case-study">.
    Title and first body paragraph share one <p>: <p><strong>Case study: X</strong>&nbsp;<br>Body</p>"""
    m = re.match(r'^<div class="(%s)">\n(.*)\n</div>$' % "|".join(CASE_STUDY_FROM), block, re.S)
    if not m:
        return block
    inner = m.group(2)
    first = re.match(r'^<p>(.*?)</p>', inner, re.S)
    if not first or not re.search(r"case\s*stud(y|ies)", re.sub(r"<[^>]+>", "", first.group(1)), re.I):
        return block
    title = first.group(1).strip()
    if not title.startswith("<strong>"):
        title = f"<strong>{title}</strong>"
    rest = inner[first.end():].lstrip("\n")
    nxt = re.match(r'^<p>(.*?)</p>', rest, re.S)
    if nxt:
        merged = f"<p>{title}&nbsp;<br>{nxt.group(1)}</p>"
        rest = rest[nxt.end():].lstrip("\n")
    else:
        merged = f"<p>{title}</p>"
    body = merged + ("\n" + rest if rest else "")
    return f'<div class="case-study">\n{body}\n</div>'

def split_label_line(block_html):
    """'<p><strong>Take note</strong><br>Text' -> '<p><strong>Take note</strong></p><p>Text'"""
    return re.sub(r"^<p>(<strong>[^<]{1,40}</strong>)<br>", r"<p>\1</p>\n<p>", block_html)

# ── table reading ───────────────────────────────────────────────────────────────
class Cell:
    def __init__(self, tc, parent):
        self.tc = tc
        self.label = is_label(tc)
        self.paras = [Paragraph(p, parent) for p in tc.iterchildren(qn("w:p"))]
        self.text = "\n".join(p.text for p in self.paras).strip()
        self.has_img = bool(tc.xpath(".//w:drawing"))

def table_rows(tbl):
    rows = []
    for tr in tbl._tbl.iterchildren(qn("w:tr")):
        cells = []
        for tc in tr.iterchildren(qn("w:tc")):
            vm = tc.xpath("./w:tcPr/w:vMerge")
            if vm and vm[0].get(qn("w:val")) in (None, "continue"):
                continue      # continuation of a vertical merge
            cells.append(Cell(tc, tbl))
        # collapse visually-merged duplicates (same text repeated across split cells)
        dedup = []
        for c in cells:
            if dedup and c.label == dedup[-1].label and c.text == dedup[-1].text and c.text:
                continue
            dedup.append(c)
        rows.append(dedup)
    return rows

def kv_sequence(rows):
    """Flatten a table to an ordered list of (key, Cell) pairs. A label cell sets the
    current key; each following value cell is emitted under that key."""
    seq = []; key = None
    for row in rows:
        for c in row:
            if c.label:
                key = norm(c.text)
                seq.append((key, None))       # key marker (lets handlers split repeated blocks)
            else:
                seq.append((key, c))
    return seq

def first_text(rows):
    for row in rows:
        for c in row:
            if c.text:
                return norm(c.text.split("\n")[0])
    return ""

def values(seq, *keys):
    ks = [norm(k) for k in keys]
    return [c for k, c in seq if c is not None and k in ks]

def val(seq, *keys, default=""):
    for c in values(seq, *keys):
        if c.text.strip():
            return c.text.strip()
    return default

# ── URL builders ────────────────────────────────────────────────────────────────
def asset_folder(fname):
    m = re.match(r"^(.*?)-M\d+P\d+", fname, re.I)
    return m.group(1) if m else fname

def image_url(fname, ext):
    fname = fname.strip()
    if not fname:
        return ""
    if fname.startswith("http") or fname.startswith("/"):
        return fname if fname.startswith("http") else CDN + fname
    if not re.search(r"\.(png|jpe?g|svg|gif|webp)$", fname, re.I):
        fname = f"{fname}.{ext}"
    base = re.sub(r"\.[a-z]+$", "", fname, flags=re.I)
    return f"{CDN}/resources/wta/{asset_folder(base)}/{fname}"

def img_tag(fname, alt, ext, align="center", decorative=False):
    cls = {"center": "block-center", "centre": "block-center", "left": "float-left", "right": "float-right"}.get(align.lower().strip(), "block-center") if align else "block-center"
    alt = "" if decorative else alt
    return f'<img src="{esc_attr(image_url(fname, ext))}" class="{cls}" width="" height="" alt="{esc_attr(alt)}">'

# ── main converter ─────────────────────────────────────────────────────────────
class Converter:
    def __init__(self, path, ext=DEFAULT_EXT):
        self.doc = docx.Document(path)
        self.ext = ext
        self.code = ""; self.title = ""
        self.blocks = []            # rendered html blocks, or ("QQ", [ids]) / ("QQMARK", n)
        self.image_meta = {}        # file name -> dict(alt, align, decorative)
        self.widget_images = set()  # file names used inside widgets (not emitted standalone)
        self.pending_reveal = None
        self.pending_hotspot = None
        self.stopped = False        # past "Assessment questions" / "Glossary"
        self.dropdown = False; self.dd_open = False
        self.qq_marked = {}         # quick quiz number -> [ids] (placed at 'Add Quick Quiz N here')
        self.final_qs = []
        self.list_buf = []

    # pre-scan: collect image metadata + quick-quiz placement markers
    def prescan(self):
        body = self.doc.element.body
        self.qq_markers = set()
        for el in body.iterchildren():
            if el.tag == qn("w:p"):
                m = re.match(r"add quick quiz\s*(\d*)", norm(Paragraph(el, self.doc).text))
                if m:
                    self.qq_markers.add(m.group(1) or "1")
            elif el.tag == qn("w:tbl"):
                rows = table_rows(Table(el, self.doc))
                t = first_text(rows)
                if t in ("image", "graphic"):
                    for img in self.split_images(kv_sequence(rows)):
                        if img["file"]:
                            self.image_meta[img["file"]] = img

    def split_images(self, seq):
        items = []; cur = None
        for k, c in seq:
            if c is None and k in ("image", "graphic"):
                cur = {"file": "", "alt": "", "align": "center", "decorative": False, "caption": ""}; items.append(cur); continue
            if cur is None or c is None:
                continue
            t = c.text.strip()
            if k in ("file name", "filename") and t: cur["file"] = t
            elif k == "alt text" and t: cur["alt"] = re.sub(r"\s+", " ", t)
            elif k == "alignment" and t: cur["align"] = t
            elif k == "decorative": cur["decorative"] = t.lower().startswith("y")
            elif k == "caption" and t: cur["caption"] = t
        return items

    def alt_for(self, fname):
        meta = self.image_meta.get(fname)
        if meta:
            return "" if meta["decorative"] else meta["alt"]
        return ""

    def emit(self, h):
        if h:
            self.blocks.append(h)

    # ── paragraphs ──
    def handle_para(self, p):
        text = p.text.strip()
        style = (p.style.name or "") if p.style is not None else ""
        if not text:
            if para_is_image_only(p) and not self.stopped:
                check("A loose image (not in an Image table) was found in the body and skipped.")
            return
        n = norm(text)
        m = re.match(r"add quick quiz\s*(\d*)", n)
        if m:
            self.blocks.append(("QQMARK", m.group(1) or "1")); return
        if any(re.search(pat, n) for pat in INSTRUCTION_PATTERNS):
            return
        if style.lower().startswith("heading") and any(re.search(pat, n) for pat in STOP_HEADINGS):
            self.close_dropdown(); self.stopped = True; return
        if self.stopped:
            return
        is_heading2 = style.lower() in ("heading 1", "heading 2")
        if is_heading2:
            if self.has_dropdown_comment(p):
                self.dropdown = True
            if self.dropdown:
                self.close_dropdown()
                self.emit(f'<wta-expander class="">\n<div slot="title">{esc(text)}</div>\n<div slot="content">')
                self.dd_open = True
                return
        if "call out" in style.lower() or "callout" in style.lower():
            cls = self.map_class(style.lower(), CALLOUT_STYLE_CLASS)
            h = split_label_line(render_paras(self.doc, [p]))
            # merge consecutive callout paragraphs of the same class
            if self.blocks and isinstance(self.blocks[-1], str) and self.blocks[-1].startswith(f'<div class="{cls}">') and getattr(self, "_last_was_callout", False):
                self.blocks[-1] = self.blocks[-1][: -len("</div>")] + h + "\n</div>"
            else:
                self.emit(f'<div class="{cls}">\n{h}\n</div>')
            self._last_was_callout = True
            return
        self._last_was_callout = False
        if num_format(self.doc, p)[0]:
            self.list_buf.append(p); return
        self.emit(render_paras(self.doc, [p]))

    def flush_list(self):
        if self.list_buf:
            buf, self.list_buf = self.list_buf, []
            self.emit(render_paras(self.doc, buf))

    def has_dropdown_comment(self, p):
        ids = p._p.xpath(".//w:commentRangeStart/@w:id") + p._p.xpath(".//w:commentReference/@w:id")
        if not ids:
            return False
        try:
            texts = {str(c.comment_id): c.text for c in self.doc.comments}
        except Exception:
            texts = {}
        for cid in ids:
            if "dropdown" in texts.get(str(cid), "").lower():
                check(f"Dropdown set starts at heading '{p.text.strip()}'. It and every following section heading became expanders; check where the set should end.")
                return True
        return False

    def close_dropdown(self):
        if self.dd_open:
            self.emit("</div>\n</wta-expander>")
            self.dd_open = False

    @staticmethod
    def map_class(value, table):
        for pat, cls in table:
            if re.search(pat, value.lower()):
                return cls
        return DEFAULT_CALLOUT

    # ── tables ──
    def handle_table(self, tbl):
        self._last_was_callout = False
        rows = table_rows(tbl)
        t = first_text(rows)
        seq = kv_sequence(rows)
        if t in ("code",):
            for row in rows:
                if len(row) >= 2:
                    k = norm(row[0].text)
                    if k == "code" and not self.code: self.code = row[1].text.strip()
                    if k == "title" and not self.title: self.title = row[1].text.strip()
            return
        if t in ("question", "category"):
            return self.question(seq)
        if t.startswith("glossary"):
            return
        if self.stopped:
            return
        if t in ("image", "graphic"):
            return self.images(seq)
        if t.startswith("call-out") or t.startswith("callout") or t.startswith("call out"):
            return self.callout(seq)
        if t.startswith("scroll animator"):
            return self.scroll_animator(seq)
        if t.startswith("image hotspot"):
            return self.hotspot_start(seq)
        if re.match(r"marker \d+", t):
            return self.hotspot_marker(seq)
        if t.startswith("html import"):
            return self.html_import(seq)
        if t.startswith("list block"):
            return self.list_block(seq)
        if t.startswith("text reveal"):
            return self.reveal_start(seq)
        if re.match(r"card \d+", t):
            return self.reveal_cards(rows)
        if t.startswith("expander") or t.startswith("dropdown") or t.startswith("accordion"):
            return self.expander(seq)
        if t.startswith("video"):
            return self.video(seq)
        return self.generic_table(rows)

    def flush_pending(self):
        if self.pending_hotspot:
            hs = self.pending_hotspot; self.pending_hotspot = None
            if not hs["markers"]:
                check(f"Image hotspot {hs['file']} has no markers.")
            parts = [f'<wta-hotspot src="{esc_attr(image_url(hs["file"], self.ext))}">']
            for i, m in enumerate(hs["markers"], 1):
                parts.append(f'<wta-hotspot-marker x="50" y="50" type="{m["type"]}" title="{esc_attr(m["title"])}" answerstatus="{m["status"]}">\n{m["desc"]}\n</wta-hotspot-marker>')
                check(f"Hotspot {hs['file']} marker {i} '{m['title']}': x/y set to 50/50. Drag it to: {m['location'] or '(no location given)'}.")
            parts.append("</wta-hotspot>")
            self.emit("\n".join(parts))
        if self.pending_reveal:
            rv = self.pending_reveal; self.pending_reveal = None
            if not rv["cards"]:
                check("Text reveal table found with no cards."); return
            attrs = rv["attrs"]
            parts = [f'<wta-text-reveal paddingtop="{attrs["pt"]}" paddingbottom="{attrs["pb"]}" borderradius="{attrs["br"]}" cardimageheight="{attrs["h"]}" widecards="{attrs["wide"]}" backgroundcolour="{attrs["bg"]}">']
            for c in rv["cards"]:
                src = image_url(c["file"], WIDGET_ICON_EXT) if c["file"] else ""
                alt = c["alt"] or self.alt_for(c["file"])
                parts.append(f'<wta-text-reveal-card src="{esc_attr(src)}" height="" alt="{esc_attr(alt)}"><div slot="buttontext">{esc(c["title"])}</div>\n<div slot="trcontent">{c["content"]}</div></wta-text-reveal-card>')
                if c["file"]:
                    self.widget_images.add(c["file"])
            parts.append("</wta-text-reveal>")
            self.emit("\n".join(parts))

    def images(self, seq):
        for img in self.split_images(seq):
            f = img["file"]
            if not f:
                check("An Image/Graphic table has no file name; skipped."); continue
            if f in self.widget_images:
                continue      # asset spec for an icon already used in a widget
            h = f"<p>{img_tag(f, img['alt'], self.ext, img['align'], img['decorative'])}</p>"
            if img["caption"]:
                h += f'\n<p class="text-center"><em>{esc(img["caption"])}</em></p>'
            if not img["alt"] and not img["decorative"]:
                check(f"Image {f} has no alt text.")
            self.emit(h)

    def callout(self, seq):
        typ = val(seq, "type")
        cls = self.map_class(typ, CALLOUT_TYPE_CLASS) if typ else DEFAULT_CALLOUT
        paras = [p for c in values(seq, "text") for p in c.paras]
        body = render_paras(self.doc, paras, title_first=True, title_tag="strong")
        self.emit(f'<div class="{cls}">\n{split_label_line(body)}\n</div>')

    def scroll_animator(self, seq):
        anim = val(seq, "animation", default="Fade left").lower().replace(" ", "-")
        dur = re.sub(r"\D", "", val(seq, "duration (ms)", "duration", default="500")) or "500"
        rep = "true" if val(seq, "repeat", default="No").lower().startswith("y") else "false"
        trig = val(seq, "trigger", default="Auto").lower()
        delay = re.sub(r"\D", "", val(seq, "delay (ms)", "delay", default="200"))
        widths = [re.sub(r"[^\d%]", "", c.text) for c in values(seq, "width")] or []
        colspec = val(seq, "column")
        if not widths and colspec:
            nums = re.findall(r"\d+", colspec); widths = [n + "%" for n in nums]
        widths = [w if w.endswith("%") else w + "%" for w in widths if w] or ["25%", "75%"]
        w1, w2 = (widths + ["75%"])[:2]
        items = []
        # newer template: Graphic*/Text* pairs; formatter template: File name + merged content cell
        cur = None; last_key_cell = None
        for k, c in seq:
            if c is None:
                last_key_cell = k; continue
            if k in ("graphic", "file name", "image"):
                if cur is not None and cur["file"] is not None and cur["content"] is None and k == "file name" and last_key_cell is None:
                    cur["content"] = c        # formatter variant: merged content cell beside File name
                elif cur is None or cur["file"] is not None:
                    cur = {"file": c.text.strip(), "content": None}; items.append(cur)
                else:
                    cur["file"] = c.text.strip()
            elif k in ("text", "content"):
                if cur is None or cur["content"] is not None:
                    cur = {"file": None, "content": None}; items.append(cur)
                cur["content"] = c
            last_key_cell = None
        alt_global = val(seq, "alt text")
        for it in items:
            f = (it.get("file") or "").strip()
            content = render_paras(self.doc, it["content"].paras, title_first=True) if it.get("content") else ""
            if not content and not f:
                continue
            h = [f'<wta-scroll-animator animation="{anim}" duration="{dur}" repeat="{rep}" trigger="{trig}" delay="{delay}">']
            if f:
                self.widget_images.add(f)
                alt = self.alt_for(f) or alt_global
                if f not in self.image_meta and not alt:
                    check(f"Scroll animator graphic {f}: no alt text found.")
                h.append(f'<wta-column-set><wta-column width="{w1}"><img src="{esc_attr(image_url(f, WIDGET_ICON_EXT))}" class="" width="" height="" alt="{esc_attr(alt)}"></wta-column><wta-column width="{w2}">\n{content}\n</wta-column></wta-column-set>')
            else:
                h.append(content)
            h.append("</wta-scroll-animator>")
            self.emit("\n".join(h))

    def hotspot_start(self, seq):
        self.flush_pending()
        f = val(seq, "file name")
        self.widget_images.add(f)
        self.pending_hotspot = {"file": f, "markers": []}

    def hotspot_marker(self, seq):
        if not self.pending_hotspot:
            check("Hotspot marker table found without an Image hotspot table before it; skipped."); return
        desc_paras = [p for c in values(seq, "description") for p in c.paras]
        self.pending_hotspot["markers"].append({
            "type": val(seq, "type", default="plus").lower().split()[0],
            "title": val(seq, "title"),
            "status": val(seq, "answer status", default="neutral").lower(),
            "location": val(seq, "location on image", "location"),
            "desc": render_paras(self.doc, desc_paras),
        })

    def html_import(self, seq):
        url = val(seq, "file name", "html file url", "url", "html url")
        url = re.sub(r"\s+", "", url)
        if not url:
            check("HTML import table has no file URL; placeholder used."); url = "TODO-HTML-IMPORT-URL"
        elif not url.lower().endswith("_launcher.html"):
            check(f"HTML import URL is not a _launcher.html file: {url}. Check this is the file the LMS should load.")
        self.emit(f'<wta-html-import contenteditable="false" url="{esc_attr(url)}"></wta-html-import>')

    def list_block(self, seq):
        typ = norm(val(seq, "type", default="Course resource"))
        cls = re.sub(r"[^a-z0-9]+", "-", typ).strip("-") or "course-resource"
        items = []
        for c in values(seq, "text"):
            for p in c.paras:
                h = inline_html(p)
                if h:
                    items.append(f"<li>{h}</li>")
        if items and "<a " not in "".join(items) and cls == "course-resource":
            check("Course resource list block has no hyperlink. Add the resource link in the editor.")
        tag = "ol" if cls in ("key-points",) else "ul"
        self.emit(f'<{tag} class="{cls}">\n' + "\n".join(items) + f"\n</{tag}>")

    def reveal_start(self, seq):
        self.flush_pending()
        disp = val(seq, "display", default="Normal").lower()
        h = re.sub(r"\D", "", val(seq, "card height", default="180")) or "180"
        pt = val(seq, "padding before", default="auto").lower() or "auto"
        pb = val(seq, "padding after", default="auto").lower() or "auto"
        br = val(seq, "border radius", default="auto").lower() or "auto"
        bg = val(seq, "background colour", "background color", default="#DCDCD7")
        self.pending_reveal = {"attrs": {"pt": pt, "pb": pb, "br": br, "h": h, "wide": "true" if "wide" in disp else "false", "bg": bg}, "cards": []}

    def reveal_cards(self, rows):
        if not self.pending_reveal:
            self.reveal_start([])
        cards = self.pending_reveal["cards"]; cur = None
        for row in rows:
            labels = [c for c in row if c.label]; vals_ = [c for c in row if not c.label]
            if labels and re.match(r"card \d+", norm(labels[0].text)):
                cur = {"title": "", "file": "", "alt": "", "content": ""}; cards.append(cur); continue
            if cur is None or not labels:
                continue
            key = norm(labels[0].text).rstrip(":")
            if key == "title":
                cur["title"] = vals_[0].text.strip() if vals_ else ""
            elif key == "file name":
                if vals_: cur["file"] = vals_[0].text.strip()
                if len(vals_) > 1: cur["content"] = render_paras(self.doc, vals_[1].paras)
            elif key == "alt text":
                cur["alt"] = " ".join(v.text.strip() for v in vals_).strip()
            elif key in ("content", "text", "description"):
                cur["content"] = render_paras(self.doc, [p for v in vals_ for p in v.paras])
        # text reveal is complete once its cards table is read
        self.flush_pending()

    def expander(self, seq):
        titles = values(seq, "title"); contents = values(seq, "content", "text")
        for t, c in zip(titles, contents):
            self.emit(f'<wta-expander class="">\n<div slot="title">{esc(t.text.strip())}</div>\n<div slot="content">\n{render_paras(self.doc, c.paras)}\n</div>\n</wta-expander>')

    def video(self, seq):
        vid = val(seq, "video id", "videoid", "id"); tok = val(seq, "token")
        if not vid or not tok:
            check("Video table is missing a video ID or token; placeholders used.")
        self.emit(f'<wta-video-23 contenteditable="false" videoid="{esc_attr(vid or "TODO")}" token="{esc_attr(tok or "TODO")}" aspect="ratio16x9" playerid=""></wta-video-23>')

    def question(self, seq):
        qid = re.sub(r"\D", "", val(seq, "question id"))
        use = norm(val(seq, "question use", "question appears in"))
        qtext = val(seq, "question")[:60]
        if "quick quiz" in use or "quickquiz" in use:
            m = re.search(r"quick quiz\s*(\d+)", use)
            n = m.group(1) if m else None
            if not qid:
                check(f"Quick Quiz question has no Question ID: '{qtext}...'. Placeholder qids='TODO' used.")
                qid = "TODO"
            if n and n in self.qq_markers:
                self.qq_marked.setdefault(n, []).append(qid)
            elif self.stopped:
                self.qq_marked.setdefault(n or "1", []).append(qid)
                if (n or "1") not in self.qq_markers:
                    check(f"Quick Quiz question {qid} sits in the assessment section and there is no 'Add Quick Quiz' marker, so it was placed at the end of the page.")
            else:
                self.blocks.append(("QQ", [qid]))
        else:
            self.final_qs.append(qid or "(no ID)")

    def generic_table(self, rows):
        if not rows:
            return
        out = ['<table class="default">']
        body_rows = rows
        if all(c.label for c in rows[0]) and len(rows) > 1:
            out.append("<thead><tr>" + "".join(f'<th scope="col">{" ".join(inline_html(p) for p in c.paras if p.text.strip())}</th>' for c in rows[0]) + "</tr></thead>")
            body_rows = rows[1:]
        out.append("<tbody>")
        for r in body_rows:
            cells = []
            for c in r:
                inner = render_paras(self.doc, c.paras)
                inner = re.sub(r"^<p>(.*)</p>$", r"\1", inner, flags=re.S) if inner.count("<p>") == 1 and "<ul" not in inner and "<ol" not in inner else inner
                cells.append(f"<td>{inner}</td>")
            out.append("<tr>" + "".join(cells) + "</tr>")
        out.append("</tbody></table>")
        check(f"Table starting '{first_text(rows)[:40]}' is not a known widget, so it was converted to a standard table (class default). Check it.")
        self.emit("\n".join(out))

    # ── run ──
    def run(self):
        self.prescan()
        body = self.doc.element.body
        for el in body.iterchildren():
            if el.tag == qn("w:p"):
                p = Paragraph(el, self.doc)
                if self.list_buf and (not num_format(self.doc, p)[0] or self.stopped):
                    if p.text.strip(): self.flush_list()
                if (self.pending_hotspot or self.pending_reveal) and p.text.strip():
                    self.flush_pending()
                self.handle_para(p)
            elif el.tag == qn("w:tbl"):
                tbl = Table(el, self.doc)
                self.flush_list()
                t = first_text(table_rows(tbl))
                if self.pending_hotspot and not re.match(r"marker \d+", t):
                    self.flush_pending()
                self.handle_table(tbl)
        self.flush_list(); self.flush_pending(); self.close_dropdown()
        return self.assemble()

    def assemble(self):
        out = []; qq_buf = []
        def flush_qq():
            if qq_buf:
                out.append(f'<wta-question qqtype="QuickQuiz" qids="{", ".join(qq_buf)}" title="" contenteditable="false"></wta-question>')
                qq_buf.clear()
        placed = set()
        for b in self.blocks:
            if isinstance(b, tuple) and b[0] == "QQ":
                qq_buf.extend(b[1]); continue
            if isinstance(b, tuple) and b[0] == "QQMARK":
                flush_qq()
                ids = self.qq_marked.get(b[1], [])
                if ids:
                    out.append(f'<wta-question qqtype="QuickQuiz" qids="{", ".join(ids)}" title="" contenteditable="false"></wta-question>')
                    placed.add(b[1])
                else:
                    check(f"'Add Quick Quiz {b[1]} here' marker has no matching Quick Quiz question; placeholder used.")
                    out.append('<wta-question qqtype="QuickQuiz" qids="TODO" title="" contenteditable="false"></wta-question>')
                continue
            flush_qq(); out.append(b)
        flush_qq()
        for n, ids in self.qq_marked.items():
            if n not in placed:
                out.append(f'<wta-question qqtype="QuickQuiz" qids="{", ".join(ids)}" title="" contenteditable="false"></wta-question>')
        if self.final_qs:
            check(f"Final-assessment questions not placed on the page (they belong in the assessment pool): {', '.join(self.final_qs)}")
        # widget images that appeared before the widget used them are removed here
        final = []
        for b in out:
            if isinstance(b, str):
                b = case_study_fix(b)
            m = re.match(r'^<p><img src="[^"]*/([^/"]+)\.\w+" class', b)
            if m and m.group(1) in self.widget_images:
                continue
            final.append(b)
        h = "\n".join(final) + "\n"
        h = re.sub(r'<p>\s*(<img\b[^>]*>)\s*</p>', r'\1', h)          # images are not wrapped in <p>
        h = re.sub(r'<p>(\s|&nbsp;|<br\s*/?>)*</p>\n?', '', h)          # no empty paragraphs
        return h


def main():
    global CDN
    ap = argparse.ArgumentParser()
    ap.add_argument("docx"); ap.add_argument("-o", "--out", default=".")
    ap.add_argument("--ext", default=DEFAULT_EXT, help="image extension when the script gives none (default png)")
    ap.add_argument("--cdn", default=CDN)
    a = ap.parse_args()
    CDN = a.cdn.rstrip("/")
    conv = Converter(a.docx, a.ext)
    src = conv.run()
    code = conv.code or re.sub(r"[ _].*$", "", os.path.splitext(os.path.basename(a.docx))[0])
    if not conv.code:
        check(f"No Code table found; file named from the docx: {code}")
    os.makedirs(a.out, exist_ok=True)
    out = os.path.join(a.out, f"{code}.html")
    with open(out, "w", encoding="utf-8") as fh:
        fh.write(src)
    print(f"WROTE {out}")
    print(f"CODE {code} | TITLE {conv.title}")
    print(f"CHECKS {len(CHECKS)}")
    for c in dict.fromkeys(CHECKS):
        print(f"- {c}")

if __name__ == "__main__":
    main()
