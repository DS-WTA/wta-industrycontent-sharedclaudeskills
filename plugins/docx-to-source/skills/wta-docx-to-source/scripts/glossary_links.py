"""Green-highlighted text in a WTA script -> <wta-glossary-link>.
mark: copy the .docx, wrapping each run of green-highlighted text in ⟦ ⟧ markers.
link: in the converted .html, turn ⟦text⟧ into <wta-glossary-link term="…" text="…">
      (markers inside attribute values are just removed)."""
import re, sys, html
OPEN, CLOSE = "⟦", "⟧"
GREENS = {"green", "brightGreen"}

def mark(src, dst):
    import docx
    from docx.oxml.ns import qn
    d = docx.Document(src)
    def is_green(r):
        h = r.find(qn("w:rPr") + "/" + qn("w:highlight"))
        return h is not None and h.get(qn("w:val")) in GREENS
    def texts(r):
        return [t for t in r.iter(qn("w:t"))]
    n = 0
    for p in d.element.body.iter(qn("w:p")):
        runs = [r for r in p.iter(qn("w:r")) if texts(r)]
        i = 0
        while i < len(runs):
            if not is_green(runs[i]):
                i += 1; continue
            j = i
            while j + 1 < len(runs) and is_green(runs[j + 1]):
                j += 1
            group = runs[i:j + 1]
            if "".join(t.text or "" for r in group for t in texts(r)).strip():
                first, last = texts(group[0])[0], texts(group[-1])[-1]
                # keep leading/trailing spaces outside the link
                m = re.match(r"^(\s*)(.*)$", first.text or "", re.S)
                first.text = m.group(1) + OPEN + m.group(2)
                m = re.match(r"^(.*?)(\s*)$", last.text or "", re.S)
                last.text = m.group(1) + CLOSE + m.group(2)
                for t in (first, last):
                    t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
                n += 1
            i = j + 1
    d.save(dst)
    print(f"GLOSSARY marked {n} green-highlighted item(s)")

def term_of(text):
    plain = html.unescape(re.sub(r"<[^>]+>", "", text))
    return re.sub(r"[^0-9a-z]", "", plain.lower())

def glossary_terms(docx_path):
    """{term id: entry} from the script's 'Glossary term' table."""
    import docx
    d = docx.Document(docx_path)
    out = {}
    for t in d.tables:
        rows = t.rows
        if rows and rows[0].cells[0].text.strip().lower().startswith("glossary term"):
            for r in rows[1:]:
                k = r.cells[0].text.replace(OPEN, "").replace(CLOSE, "").strip()
                if k: out[term_of(k)] = k
    return out

def match_term(text, known):
    """Exact glossary id first; else the closest entry (plural/singular, leading 'the'); else derived."""
    t = term_of(text)
    if t in known: return t, "exact"
    t2 = re.sub(r"^the", "", t)
    if t2 in known: return t2, "fuzzy"
    best, score = None, 0
    for k in known:
        n = 0
        while n < min(len(t2), len(k)) and t2[n] == k[n]: n += 1
        if n >= 5 and n >= 0.8 * min(len(t2), len(k)) and (n > score or (n == score and len(k) < len(best))):
            best, score = k, n
    if best: return best, "fuzzy"
    return t, "none"

def link(path, docx_path=None):
    known = glossary_terms(docx_path) if docx_path else {}
    s = open(path, encoding="utf-8").read()
    # 1) strip markers inside attribute values (alt="", title="", src="" ...)
    s = re.sub(r'="([^"]*)"', lambda m: '="' + m.group(1).replace(OPEN, "").replace(CLOSE, "") + '"', s)
    # 2) convert the rest; inline tags inside the marked text are dropped from text=""
    linked, fuzzy, unmatched = [], [], []
    def rep(m):
        inner = m.group(1)
        text = html.unescape(re.sub(r"<[^>]+>", "", inner)).strip()
        if not text:
            return inner
        term, how = match_term(text, known) if known else (term_of(text), "none")
        linked.append(text)
        if how == "fuzzy": fuzzy.append(f"'{text}' -> {term} (glossary entry '{known[term]}')")
        if how == "none" and known: unmatched.append(f"'{text}' -> {term}")
        return f'<wta-glossary-link term="{term}" text="{html.escape(text, quote=True)}"></wta-glossary-link>'
    s = re.sub(OPEN + "(.*?)" + CLOSE, rep, s, flags=re.S)
    s = s.replace(OPEN, "").replace(CLOSE, "")
    open(path, "w", encoding="utf-8").write(s)
    print(f"GLOSSARY linked {len(linked)}: " + "; ".join(linked))
    for f in dict.fromkeys(fuzzy): print("CHECK glossary link matched to a similar glossary entry: " + f)
    for u in dict.fromkeys(unmatched): print("CHECK glossary link not in the script's glossary table, term id derived from the text: " + u)

if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "mark": mark(sys.argv[2], sys.argv[3])
    elif cmd == "link": link(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None)
