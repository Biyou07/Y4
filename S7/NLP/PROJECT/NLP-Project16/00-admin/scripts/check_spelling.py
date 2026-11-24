#!/usr/bin/env python3
"""
check_spelling.py - Project 16 Darija spelling check (Task 6)

Flags Darija text that is not written the agreed way (darija-spelling-rules-v0 +
slang-glossary-v1) and says what the agreed spelling is. The same rules are
available as normalise() so the app can reuse them as its text normaliser.

Usage
    python check_spelling.py FOLDER --glossary slang-glossary-v1.csv [-o spelling-report] [--real]

FOLDER holds the CSV exports (File > Download > CSV) of the sheets. Recognised by
file name: dialogues_*, context-set*, eval-set*, crisis-templates*, and with --real
also messages_real_* (raw real comments: expect many findings, they are not normalised).

Output (in the current folder, or --outdir)
    spelling-report.csv          one line per problem: file, row_id, owner, field, script,
                                 word_found, expected, rule, level, context
    spelling-report.txt          readable summary and counts per owner
    spelling-report_<owner>.csv  the list to send to each owner

Levels
    rule     clear break of an agreed rule (diacritics, ڨ, 9/5/8 letters, sh, ...)
    variant  a known other spelling of a word; the agreed form is given
    check    probably wrong, a person should look (negation without ش / ch)

Only the Python standard library is needed. Edit the tables below to change the rules.
"""
import argparse
import csv
import io
import os
import re
import sys
import unicodedata

# --------------------------------------------------------------------------------------
# 1. RULE TABLES (edit here)
# --------------------------------------------------------------------------------------

# Which column holds the text to check, per file kind: (text column, script column or fixed script)
KINDS = {
    "dialogues": dict(
        pattern=r"^dialogues[_-]", id="dialogue_id", owner="written_by",
        fields=[("user_message", "script"), ("assistant_answer", "arabic")]),
    "context": dict(
        pattern=r"^context[_-]set", id="ctx_id", owner="written_by",
        fields=[("sentence", "script")]),
    "eval": dict(
        pattern=r"^eval[_-]set", id="eval_id", owner=None,
        fields=[("message", "script")]),
    "crisis": dict(
        pattern=r"^crisis[_-]templates", id="template_id", owner=None,
        fields=[("text", "script")]),
    "messages": dict(
        pattern=r"^messages[_-]real", id="msg_id", owner="collected_by",
        fields=[("text", "script")], only_with_real=True),
}

SKIP_VALUES = {"CRISIS_TEMPLATE"}

# Words that look like a rule break but are agreed (Arabic script)
ARABIC_NEGATION_OK = {"ماشي", "ماكاش", "ماذا", "مايا", "مادام", "ماما", "مانيش"}
# Words that may follow ما without a final ش (not verbs)
ARABIC_NOT_VERB = {"تاع", "نتا", "نتي", "نتوما", "ناس", "نهار", "تعب", "نص", "تلفون", "تعافي", "تلاتة"}
LATIN_NEGATION_OK = {"machi", "makach", "mama", "mataa", "matin", "match", "mars", "marche", "maghreb", "maroc"}
LATIN_NOT_VERB = {"ta3", "nta", "nti", "nta3", "ntouma", "houa", "hiya", "houma", "nas", "nhar", "tfel",
                  "3and", "3andi", "mere", "vie", "famille", "faute"}
# English or French words that contain "sh"/digits legitimately
LATIN_OK_WORDS = {"shit", "shop", "show", "shift", "shut", "shy", "she", "shoot", "short", "shot", "shock",
                  "sheet", "ship", "shirt", "shoe", "shower", "wish", "fish", "dish", "english", "finish",
                  "polish", "publish", "brush", "flash", "fashion", "sushi", "smash", "crash", "trash", "splash"}

# Agreed spelling of common words (from the table in darija-spelling-rules-v0) and the other
# spellings people use. Extend this table when the team agrees a new form.
AR_LEXICON = {
    "بزاف": ["بزااف", "بزف", "بزاااف", "بزفف"],
    "شوية": ["شويا", "شوي", "شويه", "شوايا"],
    "دروك": ["درك", "ضرك", "دوك", "ضروك", "دورك", "دروق"],
    "كيفاش": ["كيفاه", "كفاش", "كيفاه"],
    "علاش": ["علاه", "علاش؟"],
    "واش": ["وش"],
    "ديما": ["دايما", "دما", "ديماا", "دائما"],
    "تاع": ["تع", "متاع", "تاا"],
    "ماشي": ["ماشى", "ماشيي"],
    "ماكاش": ["مكانش", "ماكانش", "مكاش", "ماكاشي"],
    "باش": ["بش", "باه"],
    "غير": ["غي", "غيير"],
    "قداش": ["كداش", "قداااش"],
    "بصح": ["بصاح", "بصحح"],
    "وقتاش": ["وقتاش"],
    "هادا": ["هذا", "هاذا", "هدا"],
    "هادي": ["هذي", "هاذي", "هدي"],
    "هادوك": ["هذوك", "هاذوك", "هدوك"],
    "خويا": ["اخويا", "خوية"],
    "سبيطار": ["سبيتار", "سبيطر", "سبيطال", "سبيتال"],
    "عافاك": ["عفاك", "عافاك"],
    "شكرا": ["شكراا", "شكراً"],
    "لاباس": ["لاباس", "لابأس", "لباس"],
    "إن شاء الله": [],
    "الحمد لله": [],
    "والله": ["والله", "ولله", "وللاه"],
    "ياسر": ["ياسرر"],
    "نبغي": ["نبغى", "نبقي"],
    "نقدر": ["نقدرر"],
    "ساعدني": ["ساعدنى"],
}
LAT_LEXICON = {
    "wach": ["wesh", "wech", "wash", "wach"],
    "kifach": ["kifah", "kifech", "kifash", "kifache", "kifeh", "kifech"],
    "3lach": ["3lah", "3lash", "alach", "3lech", "3lache"],
    "bezzaf": ["bzaf", "bezaf", "bzzaf", "bezzef", "bzef", "bzeff"],
    "chwiya": ["chwiyya", "chwia", "chouia", "chwaya", "shwiya", "chwiy", "chwiyaa"],
    "drouk": ["drok", "dork", "dorok", "derk", "drouka", "drouq"],
    "berk": ["bark", "berka", "berkk"],
    "dima": ["dimaa", "dayma", "dayman"],
    "kayen": ["kayn", "kayan", "kain", "kaayen", "kayenn"],
    "bach": ["bech", "bash", "besh", "bch"],
    "ta3": ["mta3", "nta3", "ta33"],
    "machi": ["mashi", "mchi", "machee", "machy", "machi"],
    "ghir": ["ghi", "ghair", "ghiir"],
    "bsa7": ["bsah", "bessah", "besah", "bessa7", "bsa7"],
    "khater": ["5ater", "khatr", "khater"],
    "wella": ["wlla", "wela", "wala", "walla"],
    "waqtach": ["waqtech", "waktach", "waqtash", "wa9tach", "waktech"],
    "qdach": ["kdach", "qdech", "gdach", "9dach", "qdash"],
    "ch7al": ["chhal", "shhal", "chal", "chhel", "ch7el"],
    "chkoun": ["chkon", "shkoun", "chkoune", "chkun", "chkonn"],
    "sbitar": ["spitar", "sbitaar", "sbitat", "sbitr", "sbitale"],
    "nebghi": ["nbghi", "nabghi", "nebgi", "nbghy", "nbghi"],
    "nqder": ["nqdr", "n9der", "nqdar", "nqeder"],
    "n3ref": ["n3rf", "n3raf", "na3raf", "n3arf"],
    "n7es": ["nhess", "n7ess", "nhes", "nhas"],
    "choukran": ["chokran", "shukran", "chokrane", "choukrane", "chukran", "shokran", "cokran"],
    "labas": ["labes", "laabas", "labass", "labaas"],
    "inchallah": ["inchaallah", "inshallah", "inchalah", "inchaalah", "insha", "inchaalla", "incha"],
    "l7amdoulillah": ["hamdoulah", "alhamdoulillah", "lhamdoulillah", "l7amdolillah", "hamdulillah",
                      "7amdoulah", "alhamdolilah", "hamdolilah"],
    "wallah": ["walah", "wellah", "wlh", "wlah", "wala7", "wallahi", "wllh", "wallh"],
    "sa7": ["sah"],
    "khouya": ["khoya", "5ouya", "khouia", "khoia", "khouiya", "khouyaa", "khoy"],
    "weldi": ["ouldi", "wldi", "waldi", "oldi"],
    "drari": ["drary", "drarii"],
    "idman": ["idmane", "edman", "idmen"],
    "ta3afi": ["ta3afy", "taafi", "ta3ffi"],
    "djor3a": ["jor3a", "djor3a"],
}

AR_DIACRITICS = re.compile("[ً-ٰٟۖ-ۭـ]")  # includes shadda, tatweel
AR_G_LETTERS = {"ڨ": "ق", "ڤ": "ق", "گ": "ق", "ݣ": "ق"}
AR_RUN = re.compile(r"[؀-ۿݐ-ݿࢠ-ࣿ]+")
LAT_RUN = re.compile(r"[A-Za-z0-9À-ſ][A-Za-z0-9À-ſ'’]*")
UNIT_NUMBER = re.compile(r"^\d+(min|km|kg|dh|da|dzd|h|ans?|eme|ème|e|g|ml|mg|cm|m|s)$", re.I)

# --------------------------------------------------------------------------------------
# 2. SMALL HELPERS
# --------------------------------------------------------------------------------------

def strip_ar(s):
    """Remove diacritics and tatweel, replace the Algerian g letters by ق."""
    s = AR_DIACRITICS.sub("", s)
    return "".join(AR_G_LETTERS.get(c, c) for c in s)


def strip_ar_article(s):
    return s[2:] if s.startswith("ال") and len(s) > 3 else s


def strip_lat_article(s):
    s = s.lower().replace("’", "'")
    for p in ("l'", "el-", "el", "al", "l"):
        if s.startswith(p) and len(s) > len(p) + 2:
            return s[len(p):]
    return s


def is_arabic_word(s):
    return bool(AR_RUN.fullmatch(s))


def _snippet(text, start, end, width=22):
    a = max(0, start - width)
    b = min(len(text), end + width)
    return ("…" if a else "") + text[a:b].replace("\n", " ") + ("…" if b < len(text) else "")


# --------------------------------------------------------------------------------------
# 3. RULE ENGINE
# --------------------------------------------------------------------------------------

class Rules:
    def __init__(self, glossary_rows=None):
        self.ar_lex = {}      # variant -> (agreed, source)
        self.lat_lex = {}
        for agreed, variants in AR_LEXICON.items():
            for v in variants:
                if v and v != agreed:
                    self.ar_lex[strip_ar(v)] = (agreed, "rules table")
        for agreed, variants in LAT_LEXICON.items():
            for v in variants:
                if v and v != agreed:
                    self.lat_lex[v.lower()] = (agreed, "rules table")
        self.glossary_terms = 0
        if glossary_rows:
            self._load_glossary(glossary_rows)

    def _load_glossary(self, rows):
        canon_ar, canon_lat = set(), set()
        for r in rows:
            if (r.get("canonical_arabic") or "").strip():
                canon_ar.add(strip_ar(r["canonical_arabic"].strip()))
            if (r.get("canonical_arabizi") or "").strip():
                canon_lat.add(r["canonical_arabizi"].strip().lower())
        ar, lat = {}, {}
        conflict_ar, conflict_lat = set(), set()
        for r in rows:
            term = (r.get("term") or "").strip()
            c_ar = strip_ar((r.get("canonical_arabic") or "").strip())
            c_lat = (r.get("canonical_arabizi") or "").strip().lower()
            script = (r.get("script") or "").strip().lower()
            if not term:
                continue
            self.glossary_terms += 1
            cands = [v.strip() for v in (r.get("variants") or "").split(";") if v.strip()]
            if term not in cands:
                cands.append(term)
            for v in cands:
                if " " in v:
                    continue  # one-word variants only
                if is_arabic_word(v):
                    key = strip_ar(v)
                    if not c_ar or " " in c_ar:
                        continue
                    if key == c_ar or strip_ar_article(key) == c_ar or key in canon_ar:
                        continue
                    if key in ar and ar[key][0] != c_ar:
                        conflict_ar.add(key)
                    ar.setdefault(key, (c_ar, "glossary " + (r.get("term_id") or "")))
                else:
                    if script == "french" or not c_lat or " " in c_lat:
                        continue
                    key = v.lower().replace("’", "'")
                    stripped = strip_lat_article(key)
                    if key == c_lat or stripped == c_lat or key in canon_lat or stripped in canon_lat:
                        continue
                    if re.search(r"[^a-z0-9'à-ÿ]", key):
                        continue
                    if key in lat and lat[key][0] != c_lat:
                        conflict_lat.add(key)
                    lat.setdefault(key, (c_lat, "glossary " + (r.get("term_id") or "")))
        for k in conflict_ar:
            ar.pop(k, None)
        for k in conflict_lat:
            lat.pop(k, None)
        for k, v in ar.items():
            self.ar_lex.setdefault(k, v)
        for k, v in lat.items():
            self.lat_lex.setdefault(k, v)

    # ---- one Arabic-script word --------------------------------------------------------
    def fix_arabic(self, w):
        reasons = []
        new = w
        if AR_DIACRITICS.search(new):
            new = AR_DIACRITICS.sub("", new)
            reasons.append(("rule", "no diacritics (rule 2)"))
        if any(c in new for c in AR_G_LETTERS):
            new = "".join(AR_G_LETTERS.get(c, c) for c in new)
            reasons.append(("rule", "write ق for every q/g sound (rule 1)"))
        hit = self.ar_lex.get(new)
        if hit is None:
            art = strip_ar_article(new)
            if art != new and art in self.ar_lex:
                hit = (("ال" + self.ar_lex[art][0]), self.ar_lex[art][1])
        if hit and hit[0] != new:
            new = hit[0]
            reasons.append(("variant", "one spelling per word (rule 5): " + hit[1]))
        return new, reasons

    # ---- one Latin word (Arabizi) -------------------------------------------------------
    def fix_latin(self, w):
        reasons = []
        low = w.lower().replace("’", "'")
        new = low
        hit = self.lat_lex.get(low)
        if hit is None:
            st = strip_lat_article(low)
            if st != low and st in self.lat_lex:
                prefix = low[: len(low) - len(st)]
                hit = (prefix + self.lat_lex[st][0], self.lat_lex[st][1])
        if hit and hit[0] != low:
            new = hit[0]
            reasons.append(("variant", "one spelling per word (rule 5): " + hit[1]))
        if low in LATIN_OK_WORDS or UNIT_NUMBER.match(low) or not re.search(r"[a-z]", low):
            return (w if not reasons else new), reasons
        # digits used as letters
        if re.search(r"[a-zà-ÿ]", new) and re.search(r"[958]", new) and not hit:
            repl = {"9": "q", "5": "kh", "8": "gh"}
            fixed = re.sub(r"[958]", lambda m: repl[m.group()], new)
            if fixed != new:
                names = {"9": "q", "5": "kh", "8": "gh"}
                used = sorted({names[c] for c in new if c in names})
                reasons.append(("rule", "use " + "/".join(used) + " not the digit (rule 3: kh, gh, q)"))
                new = fixed
                hit2 = self.lat_lex.get(new)
                if hit2 and hit2[0] != new:
                    new = hit2[0]
        if "sh" in new and not hit:
            fixed = new.replace("sh", "ch")
            reasons.append(("rule", "write ch for ش, not sh (rule 3)"))
            new = fixed
            hit2 = self.lat_lex.get(new)
            if hit2 and hit2[0] != new:
                new = hit2[0]
        if new == low:
            return w, reasons
        return (new if w == low else (new[0].upper() + new[1:] if w[:1].isupper() else new)), reasons


# --------------------------------------------------------------------------------------
# 4. CHECK ONE TEXT
# --------------------------------------------------------------------------------------

def check_text(text, script, rules):
    """Return a list of findings: dict(word, expected, rule, level, context)."""
    out = []
    script = (script or "").strip().lower()
    if script in ("french", "fr", "en"):
        return out
    latin_ok = script in ("arabizi", "mixed-fr")
    # tokens in reading order
    toks = []
    for m in AR_RUN.finditer(text):
        toks.append(("ar", m.group(), m.start(), m.end()))
    if latin_ok:
        for m in LAT_RUN.finditer(text):
            toks.append(("lat", m.group(), m.start(), m.end()))
    toks.sort(key=lambda t: t[2])

    def add(word, expected, level, why, s, e):
        out.append(dict(word=word, expected=expected, rule=why, level=level, context=_snippet(text, s, e)))

    for i, (kind, w, s, e) in enumerate(toks):
        prev = toks[i - 1] if i else None
        nxt = toks[i + 1] if i + 1 < len(toks) else None
        adj_prev = prev and prev[3] <= s and re.fullmatch(r"[ \t]+", text[prev[3]:s] or " ") is not None
        if kind == "ar":
            core = strip_ar(w)
            # separated negation ش
            if core == "ش" and adj_prev and prev[0] == "ar":
                add(prev[1] + " ش", strip_ar(prev[1]) + "ش", "rule",
                    "attach the final ش to the verb (rule 4)", prev[2], e)
                continue
            new, reasons = rules.fix_arabic(w)
            # ما attached to the verb
            c = strip_ar(w)
            if (c.startswith("ما") and len(c) >= 5 and c.endswith("ش") and c not in ARABIC_NEGATION_OK
                    and not reasons):
                new = "ما " + c[2:]
                reasons.append(("rule", "write ما as a separate word (rule 4)"))
            for level, why in reasons:
                add(w, new, level, why, s, e)
            # negation without ش
            nxt2 = toks[i + 2] if i + 2 < len(toks) else None
            if c == "ما" and nxt and nxt[0] == "ar" and text[e:nxt[2]].strip() == "" \
                    and not (nxt2 and nxt2[0] == "ar" and strip_ar(nxt2[1]) == "ش" and text[nxt[3]:nxt2[2]].strip() == ""):
                n = strip_ar(nxt[1])
                if (n[:1] in "نتيأ" and len(n) >= 3 and not n.endswith("ش") and n not in ARABIC_NOT_VERB
                        and n not in ARABIC_NEGATION_OK):
                    add("ما " + nxt[1], "ما " + n + "ش", "check",
                        "negation needs the final ش (rule 4); ignore if ما means 'what'", s, nxt[3])
        else:
            low = w.lower()
            if low in ("ch", "sh") and adj_prev and prev[0] == "lat" and prev[1].lower() != "ma":
                add(prev[1] + " " + w, prev[1] + "ch", "rule",
                    "attach the final ch to the verb (rule 4)", prev[2], e)
                continue
            new, reasons = rules.fix_latin(w)
            if (low.startswith("ma") and len(low) >= 6 and low.endswith("ch") and low not in LATIN_NEGATION_OK
                    and script == "arabizi" and not reasons):
                new = "ma " + low[2:]
                reasons.append(("rule", "write ma as a separate word (rule 4)"))
            for level, why in reasons:
                add(w, new, level, why, s, e)
            nxt2 = toks[i + 2] if i + 2 < len(toks) else None
            if low == "ma" and script == "arabizi" and nxt and nxt[0] == "lat" and text[e:nxt[2]].strip() == "" \
                    and not (nxt2 and nxt2[0] == "lat" and nxt2[1].lower() in ("ch", "sh") and text[nxt[3]:nxt2[2]].strip() == ""):
                n = nxt[1].lower()
                if (n[:1] in "nty" and len(n) >= 4 and not n.endswith("ch") and n not in LATIN_NOT_VERB
                        and n not in LATIN_NEGATION_OK):
                    add("ma " + nxt[1], "ma " + n + "ch", "check",
                        "negation needs the final ch (rule 4); ignore if ma means 'what'", s, nxt[3])
    return out


def normalise(text, script="arabizi", rules=None, use_glossary=False):
    """Return text rewritten in the agreed spelling (first version of the app's normaliser).
    Applies the 'rule' fixes and the rules-table variants. Never touches 'check' items, and does not
    apply glossary variants (they can change the meaning, e.g. singular -> plural) unless use_glossary=True."""
    rules = rules or Rules()
    findings = [f for f in check_text(text, script, rules) if f["level"] != "check"
                and (use_glossary or "glossary" not in f["rule"])]
    # apply from the end so positions stay valid: find each word again by its context order
    pos = 0
    pieces, last = [], 0
    for f in findings:
        w = f["word"]
        k = text.find(w, pos)
        if k < 0:
            continue
        pieces.append(text[last:k])
        pieces.append(f["expected"])
        last = pos = k + len(w)
    pieces.append(text[last:])
    return "".join(pieces)


# --------------------------------------------------------------------------------------
# 5. FILES
# --------------------------------------------------------------------------------------

def read_csv(path):
    with open(path, "rb") as fh:
        raw = fh.read()
    text = raw.decode("utf-8-sig", errors="replace")
    sample = text[:4000]
    delim = ";" if sample.count(";") > sample.count(",") * 2 and sample.count(";") > 3 else ","
    rows = list(csv.reader(io.StringIO(text, newline=""), delimiter=delim))
    rows = [r for r in rows if any(c.strip() for c in r)]
    if not rows:
        return [], []
    head = [h.strip() for h in rows[0]]
    return head, rows[1:]


def kind_of(name):
    base = os.path.splitext(name)[0].lower()
    for k, spec in KINDS.items():
        if re.match(spec["pattern"], base):
            return k
    return None


def main(argv=None):
    ap = argparse.ArgumentParser(description="Darija spelling check against darija-spelling-rules and the slang glossary")
    ap.add_argument("folder")
    ap.add_argument("--glossary", help="slang-glossary CSV (default: slang-glossary*.csv in the folder)")
    ap.add_argument("-o", "--output", default="spelling-report", help="report name without extension")
    ap.add_argument("--outdir", default=".")
    ap.add_argument("--real", action="store_true", help="also check messages_real_* (raw comments)")
    ap.add_argument("--no-glossary", action="store_true")
    a = ap.parse_args(argv)

    gl_rows = None
    if not a.no_glossary:
        gpath = a.glossary
        if not gpath:
            for n in sorted(os.listdir(a.folder)):
                if n.lower().startswith("slang-glossary") and n.lower().endswith(".csv"):
                    gpath = os.path.join(a.folder, n)
        if gpath:
            head, body = read_csv(gpath)
            gl_rows = [dict(zip(head, r)) for r in body]
            print(f"glossary: {os.path.basename(gpath)} ({len(gl_rows)} rows)")
        else:
            print("WARNING: no slang-glossary CSV found: only the rules table and the rules of darija-spelling-rules are used")
    rules = Rules(gl_rows)

    findings = []
    checked = []
    for name in sorted(os.listdir(a.folder)):
        if not name.lower().endswith(".csv") or name.lower().startswith(("spelling-report", "validation-report")):
            continue
        k = kind_of(name)
        if not k:
            continue
        spec = KINDS[k]
        if spec.get("only_with_real") and not a.real:
            continue
        head, body = read_csv(os.path.join(a.folder, name))
        idx = {h: i for i, h in enumerate(head)}
        stem = os.path.splitext(name)[0]
        if spec["id"] not in idx:
            print(f"WARNING {name}: no {spec['id']} column, skipped")
            continue
        n_rows = 0
        for ri, r in enumerate(body, start=2):
            r = r + [""] * (len(head) - len(r))
            n_rows += 1
            rid = r[idx[spec["id"]]].strip()
            owner = (r[idx[spec["owner"]]].strip() if spec["owner"] and spec["owner"] in idx else "") or \
                    (stem.split("_", 1)[1] if "_" in stem else stem)
            for fld, sc in spec["fields"]:
                if fld not in idx:
                    continue
                txt = r[idx[fld]]
                if not txt.strip() or txt.strip() in SKIP_VALUES:
                    continue
                script = r[idx[sc]] if sc in idx else sc
                for f in check_text(txt, script, rules):
                    f.update(file=stem, row=ri, row_id=rid, owner=owner, field=fld, script=script.strip())
                    findings.append(f)
        checked.append((stem, k, n_rows))

    if not checked:
        print("ERROR: no recognised CSV (dialogues_*, context-set*, eval-set*, crisis-templates*) found in " + a.folder)
        return 2

    os.makedirs(a.outdir, exist_ok=True)
    cols = ["file", "row_id", "owner", "field", "script", "word_found", "expected", "rule", "level", "context"]

    def write(path, rows):
        with open(path, "w", newline="", encoding="utf-8-sig") as fh:
            w = csv.writer(fh)
            w.writerow(cols)
            for f in rows:
                w.writerow([f["file"], f["row_id"], f["owner"], f["field"], f["script"], f["word"],
                            f["expected"], f["rule"], f["level"], f["context"]])

    order = {"rule": 0, "variant": 1, "check": 2}
    findings.sort(key=lambda f: (f["file"], f["row"], order[f["level"]]))
    base = os.path.join(a.outdir, a.output)
    write(base + ".csv", findings)
    owners = sorted({f["owner"] for f in findings})
    for ow in owners:
        safe = re.sub(r"[^A-Za-z0-9_-]+", "_", ow)
        write(f"{base}_{safe}.csv", [f for f in findings if f["owner"] == ow])

    lines = ["# check_spelling.py report (levels: rule = clear break, variant = other spelling of an agreed word, check = please look)"]
    for stem, k, n in checked:
        lines.append(f"# checked {stem} ({k}, {n} rows)")
    for f in findings:
        lines.append(f"{f['file']}, row {f['row']} ({f['row_id']}), {f['field']}: [{f['level']}] "
                     f"'{f['word']}' -> '{f['expected']}'  ({f['rule']})")
    cnt = {}
    for f in findings:
        cnt.setdefault(f["owner"], {"rule": 0, "variant": 0, "check": 0})[f["level"]] += 1
    lines.append("# findings per owner: " + (", ".join(
        f"{o}: {c['rule']} rule / {c['variant']} variant / {c['check']} check" for o, c in sorted(cnt.items())) or "none"))
    lines.append(f"# {len(findings)} finding(s) in {sum(n for _, _, n in checked)} row(s)")
    with open(base + ".txt", "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
    print("\n".join(l for l in lines if l.startswith("#")))
    print(f"-> {base}.csv, {base}.txt" + (f" and {len(owners)} owner file(s)" if owners else ""))
    return 1 if any(f["level"] != "check" for f in findings) else 0


if __name__ == "__main__":
    sys.exit(main())
