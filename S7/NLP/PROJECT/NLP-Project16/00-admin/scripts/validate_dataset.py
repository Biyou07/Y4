#!/usr/bin/env python3
"""validate_dataset.py - checks the Project 16 dataset files against dataset-format-v1.

Each teammate exports their Google Sheet as CSV (File > Download > CSV) and puts the
files in one folder. Then run:

    python validate_dataset.py path/to/folder
    python validate_dataset.py path/to/folder -o validation-report.txt

The file kind is recognised from the file name:

    passages_<firstname>.csv      dialogues_<firstname>.csv     messages_real_<firstname>.csv
    context-set-v1.csv            eval-set-v1.csv               source-register.csv
    darija-general-v1.csv         crisis-templates-v1.csv       emergency-contacts-v1.csv

Only the standard library is needed (rapidfuzz is used for the near-duplicate check
if it is installed, otherwise difflib is used).

Exit code: 0 = no errors (warnings are allowed), 1 = at least one error.
Nothing may be merged while the report contains errors.
"""
from __future__ import annotations

import argparse
import csv
import io
import re
import sys
import unicodedata
from datetime import datetime
from difflib import SequenceMatcher
from pathlib import Path

try:  # optional, faster
    from rapidfuzz import fuzz as _fuzz
except Exception:  # pragma: no cover
    _fuzz = None

# --------------------------------------------------------------------------------------
# Editable rules. If dataset-format-v1 or the label guide changes, change them here only.
# --------------------------------------------------------------------------------------
COLUMNS = {
    "passages": "passage_id | source_id | pages | type | topic | drug | language | text | redundant_with | cleaned_by",
    "dialogues": "dialogue_id | user_message | script | assistant_answer | passage_ids | drug | user_type | request | danger | written_by",
    "messages": "msg_id | source_id | text | script | drug_term | drug_sense | drug | user_type | request | danger | collected_by | labelled_by",
    "context": "ctx_id | term | canonical_spelling | sentence | script | sense | drug | origin | written_by",
    "eval": "eval_id | message | script | drug | user_type | request | danger | expected_behaviour | passage_ids | notes",
    "crisis": "template_id | situation | script | text | contacts_used",
}
COLUMNS = {k: [c.strip() for c in v.split("|")] for k, v in COLUMNS.items()}

SCRIPTS = ["arabic", "arabizi", "mixed-fr"]
CRISIS_SCRIPTS = SCRIPTS + ["french"]
PASSAGE_TYPES = ["medical", "psychological support", "emergency", "religious"]
PASSAGE_DRUGS = ["cannabis", "alcohol", "pills", "cocaine", "heroin", "general"]
PASSAGE_LANGS = ["en", "fr", "ar"]
# label guide v1 (lower case, exactly as written in the sheets; real messages may also use Skip)
LABEL_DRUGS = ["cannabis", "alcohol", "pills", "cocaine", "heroin", "other", "unspecified"]
USER_TYPES = ["person who uses", "family member", "friend", "curious", "unclear"]
REQUESTS = ["information", "wants to quit", "craving", "withdrawal", "relapse",
            "worried about someone", "emergency", "find treatment", "safer use", "other"]
SKIP = "Skip"  # label guide v1: allowed in the five label cells of real messages only
DANGERS = ["none", "low", "high", "crisis"]
DRUG_SENSES = ["drug", "not-drug", "unclear"]
CONTEXT_SENSES = ["drug", "not-drug"]
EXPECTED = ["answer", "refer to professional", "crisis template", "refuse and redirect"]
REG_LANGS = ["ar", "fr", "en", "darija"]
REG_RELIABILITY = ["high", "medium", "low"]
REG_TYPES = ["official", "research", "dataset", "scraped"]
REG_STATUS = ["used", "related work only", "not used"]  # "used (web page)" is also accepted
INITIALS = {"abdellah": "AK", "ahmed": "AG", "malak": "MM", "souha": "SB", "yassine": "YK",
            "mohamed": "MB", "ayoub": "MB"}
ALL_INITIALS = sorted(set(INITIALS.values()))

PASSAGE_WORDS = (50, 150)
ANSWER_MAX_WORDS = 80
CRISIS_MARK = "CRISIS_TEMPLATE"

RE_PASSAGE_ID = re.compile(r"^P-(S\d{2,3})-\d{3}$")
RE_DIALOGUE_ID = re.compile(r"^D-(%s)-\d{3}$" % "|".join(ALL_INITIALS))
RE_MSG_ID = re.compile(r"^M-(S\d{2,3})-\d{4}$")
RE_EVAL_ID = re.compile(r"^E-\d{3,}$")
RE_SOURCE_ID = re.compile(r"^S\d{2,3}$")

# --------------------------------------------------------------------------------------
# File kinds (recognised from the file name)
# --------------------------------------------------------------------------------------
KIND_PATTERNS = [
    ("passages", re.compile(r"^passages[_-](?P<who>.+)$")),
    ("dialogues", re.compile(r"^dialogues[_-](?P<who>.+)$")),
    ("messages", re.compile(r"^messages[_-]real[_-](?P<who>.+)$")),
    ("context", re.compile(r"^context[_-]set")),
    ("eval", re.compile(r"^eval[_-]set")),
    ("register", re.compile(r"^source[_-]register")),
    ("general", re.compile(r"^darija[_-]general")),
    ("crisis", re.compile(r"^crisis[_-]templates")),
    ("contacts", re.compile(r"^emergency[_-]contacts")),
]


def detect_kind(path: Path):
    stem = path.stem.lower()
    for kind, rx in KIND_PATTERNS:
        m = rx.match(stem)
        if m:
            who = m.groupdict().get("who", "") or ""
            return kind, who
    return None, ""


# --------------------------------------------------------------------------------------
# Reporting
# --------------------------------------------------------------------------------------
class Report:
    def __init__(self):
        self.errors: list[str] = []
        self.warnings: list[str] = []

    @staticmethod
    def _fmt(name, row, msg):
        return f"{name}, row {row}: {msg}" if row else f"{name}: {msg}"

    def err(self, name, row, msg):
        self.errors.append(self._fmt(name, row, msg))

    def warn(self, name, row, msg):
        self.warnings.append(self._fmt(name, row, msg))


class Table:
    def __init__(self, name, kind, who, path, header, rows):
        self.name, self.kind, self.who, self.path = name, kind, who, path
        self.header = header
        self.rows = rows  # list of (sheet_row_number, {column: value})


def read_table(path: Path, rep: Report):
    try:
        text = path.read_text(encoding="utf-8-sig")
    except UnicodeDecodeError:
        rep.err(path.stem, None, "file is not UTF-8 (export again from Google Sheets as CSV)")
        return None
    if not text.strip():
        rep.err(path.stem, None, "file is empty")
        return None
    first_line = text.splitlines()[0]
    delim = ";" if first_line.count(";") > first_line.count(",") else ","
    # parse the full text so that quoted cells containing line breaks stay in one row
    data = list(csv.reader(io.StringIO(text, newline=""), delimiter=delim))
    header = [h.strip() for h in data[0]]
    rows = []
    for i, r in enumerate(data[1:], start=2):
        if not any(c.strip() for c in r):
            continue
        if len(r) > len(header) and any(c.strip() for c in r[len(header):]):
            rep.warn(path.stem, i, f"{len(r) - len(header)} cell(s) after the last column are ignored")
        r = (r + [""] * len(header))[: len(header)]
        rows.append((i, dict(zip(header, r))))
    return header, rows


# --------------------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------------------
AR_DIGITS = str.maketrans("٠١٢٣٤٥٦٧٨٩۰۱۲۳۴۵۶۷۸۹", "01234567890123456789")
RE_EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
RE_MENTION = re.compile(r"(?<![\w@])@\w{2,}")
RE_URL = re.compile(r"(https?://|www\.)\S+", re.I)
RE_DOMAIN = re.compile(r"\b[\w-]+\.(com|org|net|dz|fr|gov|edu|info|io|me|tv|be|ly|co|app)\b", re.I)
RE_PHONE = re.compile(r"(?<![\d])\+?\d(?:[\s.\-()]?\d){7,}(?!\d)")
RE_DATE = re.compile(r"\b\d{4}[-/.]\d{1,2}[-/.]\d{1,2}\b|\b\d{1,2}[-/.]\d{1,2}[-/.]\d{2,4}\b")


def pii_found(text: str):
    t = text.translate(AR_DIGITS)
    kinds = []
    if RE_EMAIL.search(t):
        kinds.append("email address")
    if RE_URL.search(t) or RE_DOMAIN.search(t):
        kinds.append("link")
    if RE_MENTION.search(RE_EMAIL.sub(" ", t)):
        kinds.append("@mention")
    if RE_PHONE.search(RE_DATE.sub(" ", t)):
        kinds.append("phone number")
    return kinds


def words(text: str) -> int:
    return len(text.split())


def split_ids(value: str):
    return [x.strip() for x in re.split(r"[;,|]|\s{2,}", value) if x.strip()]


def norm_text(s: str) -> str:
    s = unicodedata.normalize("NFKC", s).lower().translate(AR_DIGITS)
    s = re.sub(r"[ً-ٰٟـ]", "", s)  # Arabic diacritics and tatweel
    s = re.sub(r"[^\w\s]|_", " ", s)
    return " ".join(s.split())


def hint(value, allowed):
    for a in allowed:
        if a.lower() == value.lower().replace("_", " ").replace("-", " ") or a.lower() == value.lower():
            return f" (write '{a}')"
    return ""


class Checker:
    def __init__(self, rep: Report):
        self.rep = rep

    # -- generic cell checks -------------------------------------------------------
    def required(self, t, rn, row, cols):
        for c in cols:
            if not row[c].strip():
                self.rep.err(t.name, rn, f"{c} is empty")

    def enum(self, t, rn, row, col, allowed, multi=False, required=True, warn_blank=False):
        v = row[col].strip()
        if not v:
            if required:
                (self.rep.warn if warn_blank else self.rep.err)(t.name, rn, f"{col} is empty")
            return
        vals = [x.strip() for x in re.split(r"[;,|]", v)] if multi else [v]
        for x in vals:
            if x not in allowed:
                self.rep.err(t.name, rn, f"{col} '{x}' is not allowed{hint(x, allowed)}; allowed: {', '.join(allowed)}")

    def pii(self, t, rn, row, cols):
        for c in cols:
            kinds = pii_found(row.get(c, ""))
            if kinds:
                self.rep.err(t.name, rn, f"{c} contains personal data: {', '.join(kinds)} (remove it)")

    def columns(self, t, expected):
        got = t.header
        if got == expected:
            return True
        missing = [c for c in expected if c not in got]
        extra = [c for c in got if c not in expected and c]
        if missing:
            self.rep.err(t.name, None, f"missing column(s): {', '.join(missing)}; rows not checked")
        if extra:
            self.rep.err(t.name, None, f"unexpected column(s): {', '.join(extra)}")
        if not missing and not extra:
            self.rep.err(t.name, None, "columns are in the wrong order; expected: " + " | ".join(expected))
        return not missing

    def unique_ids(self, t, col, regex, seen, sample):
        ok = True
        for rn, row in t.rows:
            v = row[col].strip()
            if not v:
                self.rep.err(t.name, rn, f"{col} is empty")
                continue
            if not regex.match(v):
                self.rep.err(t.name, rn, f"{col} '{v}' does not follow the pattern {sample}")
            if v in seen:
                self.rep.err(t.name, rn, f"{col} '{v}' is already used in {seen[v][0]}, row {seen[v][1]}")
            else:
                seen[v] = (t.name, rn)
        return ok


# --------------------------------------------------------------------------------------
# The validator
# --------------------------------------------------------------------------------------
def validate(tables: list[Table], rep: Report, leak_threshold: float, check_leak: bool):
    ck = Checker(rep)
    by_kind: dict[str, list[Table]] = {}
    for t in tables:
        by_kind.setdefault(t.kind, []).append(t)

    # ---- source register -------------------------------------------------------
    source_ids: set[str] | None = None
    for t in by_kind.get("register", []):
        source_ids = source_ids or set()
        norm = {h.lower(): h for h in t.header}
        need = ["id", "language", "licence", "reliability", "type", "status", "file name"]
        absent = [c for c in need if c not in norm]
        if absent:
            rep.err(t.name, None, f"missing column(s): {', '.join(absent)}")
        enums = {"language": REG_LANGS, "reliability": REG_RELIABILITY, "type": REG_TYPES}
        for rn, row in t.rows:
            low = {k.lower(): v.strip() for k, v in row.items()}
            sid = low.get("id", "")
            if not RE_SOURCE_ID.match(sid):
                rep.warn(t.name, rn, f"row ignored: id '{sid}' is not a source id like S08")
                continue
            if sid in source_ids:
                rep.err(t.name, rn, f"id '{sid}' appears twice")
            source_ids.add(sid)
            for c in ("language", "licence", "reliability", "type", "status"):
                if c in low and not low[c]:
                    rep.err(t.name, rn, f"{c} is empty for {sid}")
            for c, allowed in enums.items():
                if low.get(c) and low[c] not in allowed:
                    rep.err(t.name, rn, f"{c} '{low[c]}' is not allowed{hint(low[c], allowed)}; allowed: {', '.join(allowed)}")
            st = low.get("status", "")
            if st and st not in REG_STATUS and not st.startswith("used ("):
                rep.err(t.name, rn, f"status '{st}' is not allowed; allowed: {', '.join(REG_STATUS)} (or 'used (web page)')")
            if "file name" in low and not low["file name"] and st not in ("not used",):
                rep.warn(t.name, rn, f"no file name for {sid} (status '{st}')")
    if source_ids is None:
        rep.warn("source-register", None, "no source-register CSV found: source_id checks skipped")

    # ---- passages --------------------------------------------------------------
    passage_ids: dict[str, tuple] = {}
    texts_seen: dict[str, tuple] = {}
    for t in by_kind.get("passages", []):
        if not ck.columns(t, COLUMNS["passages"]):
            continue
        ck.unique_ids(t, "passage_id", RE_PASSAGE_ID, passage_ids, "P-S08-001")
        for rn, row in t.rows:
            ck.required(t, rn, row, ["source_id", "topic", "text", "cleaned_by"])
            m = RE_PASSAGE_ID.match(row["passage_id"].strip())
            sid = row["source_id"].strip()
            if m and sid and m.group(1) != sid:
                rep.err(t.name, rn, f"passage_id {row['passage_id']} belongs to {m.group(1)} but source_id is {sid}")
            if sid and source_ids is not None and sid not in source_ids:
                rep.err(t.name, rn, f"source_id '{sid}' is not in source-register")
            if not row["pages"].strip():
                rep.warn(t.name, rn, "pages is empty")
            ck.enum(t, rn, row, "type", PASSAGE_TYPES)
            ck.enum(t, rn, row, "drug", PASSAGE_DRUGS)
            ck.enum(t, rn, row, "language", PASSAGE_LANGS)
            n = words(row["text"])
            if row["text"].strip() and not (PASSAGE_WORDS[0] <= n <= PASSAGE_WORDS[1]):
                rep.err(t.name, rn, f"text has {n} words (must be {PASSAGE_WORDS[0]}-{PASSAGE_WORDS[1]})")
            ck.pii(t, rn, row, ["text"])
            key = norm_text(row["text"])
            if key:
                if key in texts_seen:
                    rep.warn(t.name, rn, f"text is identical to {texts_seen[key][0]}, row {texts_seen[key][1]}; keep one and fill redundant_with")
                else:
                    texts_seen[key] = (t.name, rn)
    for t in by_kind.get("passages", []):  # redundant_with needs all passage ids
        if t.header != COLUMNS["passages"] and any(c not in t.header for c in COLUMNS["passages"]):
            continue
        for rn, row in t.rows:
            r = row["redundant_with"].strip()
            if r:
                if r == row["passage_id"].strip():
                    rep.err(t.name, rn, "redundant_with points to the passage itself")
                elif r not in passage_ids:
                    rep.err(t.name, rn, f"redundant_with '{r}' does not exist in any passages file")
    if not by_kind.get("passages"):
        rep.warn("passages", None, "no passages_<name> CSV found: passage_id checks skipped")
    have_passages = bool(by_kind.get("passages"))

    # ---- dialogues -------------------------------------------------------------
    dialogue_ids: dict[str, tuple] = {}
    messages_seen: dict[str, tuple] = {}
    for t in by_kind.get("dialogues", []):
        if not ck.columns(t, COLUMNS["dialogues"]):
            continue
        ck.unique_ids(t, "dialogue_id", RE_DIALOGUE_ID, dialogue_ids, "D-AG-001")
        exp_init = INITIALS.get(t.who.split("_")[0].split("-")[0].lower())
        for rn, row in t.rows:
            ck.required(t, rn, row, ["user_message", "written_by"])
            did = row["dialogue_id"].strip()
            if exp_init and RE_DIALOGUE_ID.match(did) and f"-{exp_init}-" not in did:
                rep.warn(t.name, rn, f"dialogue_id {did} does not use the initials {exp_init} of this file's author")
            ck.enum(t, rn, row, "script", SCRIPTS)
            ck.enum(t, rn, row, "drug", LABEL_DRUGS, multi=True)
            ck.enum(t, rn, row, "user_type", USER_TYPES)
            ck.enum(t, rn, row, "request", REQUESTS)
            ck.enum(t, rn, row, "danger", DANGERS)
            ans = row["assistant_answer"].strip()
            crisis = row["danger"].strip() == "crisis"
            if not ans:
                rep.err(t.name, rn, "assistant_answer is empty")
            elif crisis and ans != CRISIS_MARK:
                rep.err(t.name, rn, f"danger is crisis: assistant_answer must be exactly {CRISIS_MARK}, not a written answer")
            elif not crisis and ans == CRISIS_MARK:
                rep.err(t.name, rn, f"assistant_answer is {CRISIS_MARK} but danger is '{row['danger'].strip()}'")
            elif not crisis and words(ans) > ANSWER_MAX_WORDS:
                rep.err(t.name, rn, f"assistant_answer has {words(ans)} words (maximum {ANSWER_MAX_WORDS})")
            ids = split_ids(row["passage_ids"])
            if not ids and not crisis:
                rep.err(t.name, rn, "passage_ids is empty (every answer must cite its passages)")
            for pid in ids:
                if have_passages and pid not in passage_ids:
                    rep.err(t.name, rn, f"passage_id '{pid}' does not exist in any passages file")
                elif not RE_PASSAGE_ID.match(pid):
                    rep.err(t.name, rn, f"passage_id '{pid}' does not follow the pattern P-S08-001")
            ck.pii(t, rn, row, ["user_message", "assistant_answer"])
            key = norm_text(row["user_message"])
            if key:
                if key in messages_seen:
                    rep.warn(t.name, rn, f"user_message is identical to {messages_seen[key][0]}, row {messages_seen[key][1]}")
                else:
                    messages_seen[key] = (t.name, rn)

    # ---- real messages ---------------------------------------------------------
    msg_ids: dict[str, tuple] = {}
    for t in by_kind.get("messages", []):
        if not ck.columns(t, COLUMNS["messages"]):
            continue
        ck.unique_ids(t, "msg_id", RE_MSG_ID, msg_ids, "M-S25-0001")
        for rn, row in t.rows:
            ck.required(t, rn, row, ["source_id", "text", "collected_by"])
            m = RE_MSG_ID.match(row["msg_id"].strip())
            sid = row["source_id"].strip()
            if m and sid and m.group(1) != sid:
                rep.err(t.name, rn, f"msg_id {row['msg_id']} belongs to {m.group(1)} but source_id is {sid}")
            if sid and source_ids is not None and sid not in source_ids:
                rep.err(t.name, rn, f"source_id '{sid}' is not in source-register")
            ck.enum(t, rn, row, "script", SCRIPTS)
            # labels are filled later by Ahmed: blank is only a warning, a wrong value is an error
            ck.enum(t, rn, row, "drug_sense", DRUG_SENSES + [SKIP], warn_blank=True)
            ck.enum(t, rn, row, "drug", LABEL_DRUGS + [SKIP], multi=True, warn_blank=True)
            ck.enum(t, rn, row, "user_type", USER_TYPES + [SKIP], warn_blank=True)
            ck.enum(t, rn, row, "request", REQUESTS + [SKIP], warn_blank=True)
            ck.enum(t, rn, row, "danger", DANGERS + [SKIP], warn_blank=True)
            if row["drug_sense"].strip() and not row["labelled_by"].strip():
                rep.warn(t.name, rn, "labels are filled but labelled_by is empty")
            ck.pii(t, rn, row, ["text"])

    # ---- context set -----------------------------------------------------------
    ctx_ids: dict[str, tuple] = {}
    for t in by_kind.get("context", []):
        if not ck.columns(t, COLUMNS["context"]):
            continue
        ck.unique_ids(t, "ctx_id", re.compile(r"^\S+$"), ctx_ids, "a non-empty id without spaces")
        for rn, row in t.rows:
            ck.required(t, rn, row, ["term", "canonical_spelling", "sentence", "origin", "written_by"])
            ck.enum(t, rn, row, "script", SCRIPTS)
            ck.enum(t, rn, row, "sense", CONTEXT_SENSES)
            if row["sense"].strip() == "drug":
                ck.enum(t, rn, row, "drug", LABEL_DRUGS, multi=True)
            elif row["drug"].strip():
                ck.enum(t, rn, row, "drug", LABEL_DRUGS, multi=True)
            origin = row["origin"].strip()
            if origin and origin != "invented":
                if not RE_MSG_ID.match(origin):
                    rep.err(t.name, rn, f"origin '{origin}' must be 'invented' or a msg_id like M-S25-0001")
                elif by_kind.get("messages") and origin not in msg_ids:
                    rep.err(t.name, rn, f"origin '{origin}' does not exist in any messages_real file")
            ck.pii(t, rn, row, ["sentence"])

    # ---- darija general corpus (format not fixed yet: only privacy is checked) --
    for t in by_kind.get("general", []):
        text_cols = [c for c in t.header if c.lower() in ("text", "sentence", "message")]
        if not text_cols:
            rep.warn(t.name, None, "no 'text' column found: only checked for presence")
        for rn, row in t.rows:
            ck.pii(t, rn, row, text_cols)

    # ---- emergency contacts and crisis templates --------------------------------
    contact_ids: set[str] | None = None
    for t in by_kind.get("contacts", []):
        contact_ids = contact_ids or set()
        norm = {h.lower(): h for h in t.header}
        need = ["contact_id", "official source link", "date checked"]
        absent = [c for c in need if c not in norm]
        if absent:
            rep.err(t.name, None, f"missing column(s): {', '.join(absent)}")
            continue
        for rn, row in t.rows:
            low = {k.lower(): v.strip() for k, v in row.items()}
            for c in need:
                if not low[c]:
                    rep.err(t.name, rn, f"{c} is empty (nothing unverified may be used in crisis answers)")
            if low["contact_id"]:
                contact_ids.add(low["contact_id"])
    for t in by_kind.get("crisis", []):
        if not ck.columns(t, COLUMNS["crisis"]):
            continue
        seen: dict[str, tuple] = {}
        ck.unique_ids(t, "template_id", re.compile(r"^\S+$"), seen, "a non-empty id without spaces")
        combos = set()
        for rn, row in t.rows:
            ck.required(t, rn, row, ["situation", "text", "contacts_used"])
            ck.enum(t, rn, row, "script", CRISIS_SCRIPTS)
            combos.add((row["situation"].strip(), row["script"].strip()))
            if contact_ids is not None:
                for cid in split_ids(row["contacts_used"]):
                    if cid not in contact_ids:
                        rep.err(t.name, rn, f"contacts_used '{cid}' is not in emergency-contacts (only verified contacts allowed)")
        sit = {s for s, _ in combos if s}
        if len(t.rows) != 9 or len(sit) != 3 or len(combos) != 9:
            rep.warn(t.name, None, f"expected 9 rows (3 situations x 3 versions); found {len(t.rows)} rows, {len(sit)} situations, {len(combos)} distinct situation/script pairs")
        if contact_ids is None:
            rep.warn(t.name, None, "no emergency-contacts CSV found: contacts_used not cross-checked")
    # crisis dialogues need the templates to exist
    if any(r["danger"].strip() == "crisis" for t in by_kind.get("dialogues", []) for _, r in t.rows) \
            and not by_kind.get("crisis"):
        rep.warn("crisis-templates", None, "dialogues contain CRISIS_TEMPLATE but no crisis-templates CSV was found")

    # ---- evaluation set ---------------------------------------------------------
    eval_ids: dict[str, tuple] = {}
    eval_rows = []
    for t in by_kind.get("eval", []):
        if not ck.columns(t, COLUMNS["eval"]):
            continue
        ck.unique_ids(t, "eval_id", RE_EVAL_ID, eval_ids, "E-001")
        for rn, row in t.rows:
            ck.required(t, rn, row, ["message"])
            ck.enum(t, rn, row, "script", SCRIPTS)
            ck.enum(t, rn, row, "drug", LABEL_DRUGS, multi=True)
            ck.enum(t, rn, row, "user_type", USER_TYPES)
            ck.enum(t, rn, row, "request", REQUESTS)
            ck.enum(t, rn, row, "danger", DANGERS)
            ck.enum(t, rn, row, "expected_behaviour", EXPECTED)
            ids = split_ids(row["passage_ids"])
            if row["expected_behaviour"].strip() == "answer" and not ids:
                rep.err(t.name, rn, "expected_behaviour is 'answer' but passage_ids is empty")
            for pid in ids:
                if have_passages and pid not in passage_ids:
                    rep.err(t.name, rn, f"passage_id '{pid}' does not exist in any passages file")
                elif not RE_PASSAGE_ID.match(pid):
                    rep.err(t.name, rn, f"passage_id '{pid}' does not follow the pattern P-S08-001")
            if row["danger"].strip() == "crisis" and row["expected_behaviour"].strip() not in ("", "crisis template"):
                rep.warn(t.name, rn, f"danger is crisis but expected_behaviour is '{row['expected_behaviour'].strip()}' (expected 'crisis template')")
            ck.pii(t, rn, row, ["message", "notes"])
            eval_rows.append((t.name, rn, row["message"]))

    # ---- no eval message in any training file --------------------------------------
    if check_leak and eval_rows:
        train = []  # (file, row, normalised text)
        for kind, col in (("dialogues", "user_message"), ("messages", "text"), ("context", "sentence"),
                          ("general", "text")):
            for t in by_kind.get(kind, []):
                if col not in t.header:
                    continue
                for rn, row in t.rows:
                    n = norm_text(row[col])
                    if n:
                        train.append((t.name, rn, n))
        exact = {}
        for f, rn, n in train:
            exact.setdefault(n, (f, rn))
        for fname, rn, msg in eval_rows:
            n = norm_text(msg)
            if not n:
                continue
            if n in exact:
                f, r = exact[n]
                rep.err(fname, rn, f"message is identical to {f}, row {r}: eval messages must never appear in training files")
                continue
            best = (0.0, None)
            for f, r, tn in train:
                s = similarity(n, tn, leak_threshold)
                if s > best[0]:
                    best = (s, (f, r))
            if best[0] >= leak_threshold:
                rep.err(fname, rn, f"message is nearly identical to {best[1][0]}, row {best[1][1]} "
                                   f"(similarity {best[0]:.2f}): eval messages must never appear in training files")
    elif check_leak and not eval_rows:
        rep.warn("eval-set", None, "no eval-set CSV found: leakage check skipped")


def similarity(a: str, b: str, threshold: float) -> float:
    if abs(len(a) - len(b)) > max(len(a), len(b)) * (1 - threshold) + 1:
        return 0.0
    if _fuzz is not None:
        return _fuzz.ratio(a, b) / 100.0
    sm = SequenceMatcher(None, a, b, autojunk=False)
    if sm.real_quick_ratio() < threshold or sm.quick_ratio() < threshold:
        return 0.0
    return sm.ratio()


# --------------------------------------------------------------------------------------
# Command line
# --------------------------------------------------------------------------------------
def collect_files(paths, recursive):
    files = []
    for p in map(Path, paths):
        if p.is_dir():
            files += sorted(p.rglob("*.csv") if recursive else p.glob("*.csv"))
        elif p.is_file():
            files.append(p)
        else:
            print(f"warning: {p} not found", file=sys.stderr)
    return files


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Validate the Project 16 dataset files against dataset-format-v1.")
    ap.add_argument("paths", nargs="*", default=["."], help="folder(s) or CSV file(s) (default: current folder)")
    ap.add_argument("-o", "--output", default="validation-report.txt", help="report file (default: validation-report.txt)")
    ap.add_argument("-r", "--recursive", action="store_true", help="also look in sub-folders")
    ap.add_argument("--leak-threshold", type=float, default=0.90,
                    help="similarity (0-1) above which an eval message counts as 'almost the same' as a training message (default 0.90)")
    ap.add_argument("--no-leak-check", action="store_true", help="skip the eval-vs-training comparison")
    ap.add_argument("--strict", action="store_true", help="treat warnings as errors for the exit code")
    args = ap.parse_args(argv)

    rep = Report()
    tables, skipped = [], []
    for f in collect_files(args.paths, args.recursive):
        if f.name == Path(args.output).name:
            continue
        kind, who = detect_kind(f)
        if kind is None:
            skipped.append(f.name)
            continue
        res = read_table(f, rep)
        if res is None:
            continue
        header, rows = res
        tables.append(Table(f.stem, kind, who, f, header, rows))

    if not tables:
        rep.err("validate_dataset", None, "no recognised dataset CSV found in: " + ", ".join(args.paths))
    validate(tables, rep, args.leak_threshold, not args.no_leak_check)

    stamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = [f"# validate_dataset.py report, {stamp} (row numbers are spreadsheet rows; row 1 is the header)"]
    lines += rep.errors
    lines += [f"WARNING {w}" for w in rep.warnings]
    lines.append(f"# {len(tables)} file(s) checked, {len(rep.errors)} error(s), {len(rep.warnings)} warning(s)")
    Path(args.output).write_text("\n".join(lines) + "\n", encoding="utf-8")

    for t in tables:
        print(f"checked {t.name:35s} {t.kind:10s} {len(t.rows):5d} rows")
    if skipped:
        print("skipped (file name not recognised): " + ", ".join(skipped))
    print(f"{len(rep.errors)} error(s), {len(rep.warnings)} warning(s) -> {args.output}")
    if rep.errors:
        print("NOT READY to merge.")
    return 1 if rep.errors or (args.strict and rep.warnings) else 0


if __name__ == "__main__":
    sys.exit(main())
