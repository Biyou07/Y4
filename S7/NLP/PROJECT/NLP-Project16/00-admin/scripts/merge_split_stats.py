#!/usr/bin/env python3
"""
merge_split_stats.py - Project 16, Task 8: merge, split and statistics

Builds the dataset-v1 folder from the team's CSV exports, but only when validate_dataset.py
reports no error ("nothing is merged while it reports errors").

Usage
    python merge_split_stats.py FOLDER                  # release: validator must report 0 errors
    python merge_split_stats.py FOLDER --draft          # test run: ignores validator errors, writes dataset-v1-DRAFT
    options: -o OUTDIR   --dev-share 0.15   --seed 42   --report validation-report.txt

FOLDER holds the CSV exports (same names as for the validator). validate_dataset.py must be in the same
folder as this script.

Output (OUTDIR/dataset-v1, or dataset-v1-DRAFT)
    knowledge_base/passages.csv + .jsonl     every passage_*, duplicates stay and keep redundant_with
    train/ and dev/                          dialogues.csv, messages_real.csv and <part>.jsonl
    test/eval-set-v1.csv + test.jsonl        the held-out evaluation set (never used for training)
    language/darija-general-v1.csv + .jsonl  general Darija lines
    support/                                 crisis templates, emergency contacts, context set, source register
    stats.csv                                part | dimension | value | count
    split-manifest.csv                       which id went to train or dev, with its danger level

Split: dialogues and labelled real messages are pooled and split 85% train / 15% dev, separately for each
danger level, with a fixed seed so the result can be repeated. A real message is "labelled" when drug_sense,
drug, user_type, request and danger are all filled and none is Skip.
"""
import argparse
import csv
import json
import random
import re
import shutil
import sys
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import validate_dataset as vd  # noqa: E402

DANGERS = vd.DANGERS
LABELS = ["drug_sense", "drug", "user_type", "request", "danger"]


def norm(s):
    s = unicodedata.normalize("NFKC", s).lower()
    return re.sub(r"\s+", " ", re.sub(r"[^\w\s]", " ", s)).strip()


def load(folder):
    rep = vd.Report()
    tables = []
    for f in vd.collect_files([folder], False):
        kind, who = vd.detect_kind(f)
        if kind is None:
            continue
        res = vd.read_table(f, rep)
        if res:
            header, rows = res
            tables.append(vd.Table(f.stem, kind, who, f, header, rows))
    return tables


def write_csv(path, header, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(header)
        for r in rows:
            w.writerow([r.get(h, "") for h in header])


def write_jsonl(path, records):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        for r in records:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")


def merged(tables, kind):
    ts = [t for t in tables if t.kind == kind]
    if not ts:
        return None, []
    header = ts[0].header
    rows = []
    for t in ts:
        for _, r in t.rows:
            rows.append({**r, "_file": t.name})
    return header, rows


def is_labelled(r):
    return all(r.get(c, "").strip() and r.get(c, "").strip() != vd.SKIP for c in LABELS) and \
        all(x.strip() in DANGERS for x in [r["danger"]])


def stratified_split(pool, dev_share, seed):
    """pool: list of dict with keys id, danger. Returns {id: 'train'|'dev'}."""
    by = defaultdict(list)
    for r in pool:
        by[r["danger"]].append(r)
    rnd = random.Random(seed)
    out = {}
    for lvl in DANGERS:
        items = sorted(by.get(lvl, []), key=lambda r: r["id"])
        rnd.shuffle(items)
        n = len(items)
        n_dev = round(n * dev_share)
        if n >= 2 and n_dev == 0:
            n_dev = 1
        if n < 2:
            n_dev = 0
        for i, r in enumerate(items):
            out[r["id"]] = "dev" if i < n_dev else "train"
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description="Merge, split and statistics for dataset-v1")
    ap.add_argument("folder")
    ap.add_argument("-o", "--outdir", default=".")
    ap.add_argument("--draft", action="store_true", help="test run: ignore validator errors, write dataset-v1-DRAFT")
    ap.add_argument("--dev-share", type=float, default=0.15)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--report", default="validation-report.txt")
    a = ap.parse_args(argv)

    # 1. validator gate
    rc = vd.main([a.folder, "-o", a.report])
    if rc != 0 and not a.draft:
        print("\nBLOCKED: the validator reports errors (see %s). Nothing was merged." % a.report)
        print("Fix the errors and run again, or use --draft for a test run that is not a release.")
        return 1
    draft = rc != 0 or a.draft
    out = Path(a.outdir) / ("dataset-v1-DRAFT" if draft else "dataset-v1")
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)

    tables = load(a.folder)
    stats = []  # (part, dimension, value, count)

    def add(part, dim, counter):
        for k, v in sorted(counter.items(), key=lambda kv: (-kv[1], str(kv[0]))):
            stats.append((part, dim, k, v))

    def multi(values):
        c = Counter()
        for v in values:
            for x in re.split(r"[;,|]", v):
                if x.strip():
                    c[x.strip()] += 1
        return c

    # 2. knowledge base
    h, passages = merged(tables, "passages")
    if h:
        cols = h
        write_csv(out / "knowledge_base" / "passages.csv", cols, passages)
        write_jsonl(out / "knowledge_base" / "passages.jsonl",
                    [{k: r.get(k, "") for k in cols} for r in passages])
        stats.append(("knowledge_base", "passages", "total", len(passages)))
        stats.append(("knowledge_base", "passages", "marked redundant (redundant_with filled)",
                      sum(1 for r in passages if r.get("redundant_with", "").strip())))
        for dim in ("source_id", "type", "drug", "language"):
            add("knowledge_base", dim, Counter(r[dim] for r in passages))
    else:
        print("WARNING: no passages_* file found")

    # 3. pool of dialogues and labelled real messages
    hd, dialogues = merged(tables, "dialogues")
    hm, messages = merged(tables, "messages")
    pool = []
    for r in dialogues or []:
        pool.append(dict(id=r["dialogue_id"], danger=r["danger"].strip(), type="dialogue", row=r))
    skipped = Counter()
    for r in messages or []:
        if is_labelled(r):
            pool.append(dict(id=r["msg_id"], danger=r["danger"].strip(), type="message", row=r))
        elif any(r.get(c, "").strip() == vd.SKIP for c in LABELS):
            skipped["Skip (not about drugs)"] += 1
        else:
            skipped["not labelled yet"] += 1
    bad = [p for p in pool if p["danger"] not in DANGERS]
    if bad:
        print(f"WARNING: {len(bad)} record(s) with an invalid danger level are left out of the split")
        pool = [p for p in pool if p["danger"] in DANGERS]
    split = stratified_split(pool, a.dev_share, a.seed)

    # 4. eval set (test) and leakage double check
    he, evals = merged(tables, "eval")
    if evals:
        ev_norm = {norm(r["message"]) for r in evals}
        leaks = [p["id"] for p in pool
                 if norm(p["row"].get("user_message", p["row"].get("text", ""))) in ev_norm]
        if leaks:
            print("ERROR: eval-set message also found in train/dev: " + ", ".join(leaks[:10]))
            return 2

    for part in ("train", "dev"):
        d_rows = [p["row"] for p in pool if p["type"] == "dialogue" and split[p["id"]] == part]
        m_rows = [p["row"] for p in pool if p["type"] == "message" and split[p["id"]] == part]
        if hd:
            write_csv(out / part / "dialogues.csv", hd, d_rows)
        if hm:
            write_csv(out / part / "messages_real.csv", hm, m_rows)
        recs = [{"id": p["row"].get("dialogue_id") or p["row"].get("msg_id"), "type": p["type"], "split": part,
                 **{k: v for k, v in p["row"].items() if not k.startswith("_")}}
                for p in pool if split[p["id"]] == part]
        write_jsonl(out / part / f"{part}.jsonl", recs)
        stats.append((part, "records", "total", len(recs)))
        stats.append((part, "records", "dialogues", len(d_rows)))
        stats.append((part, "records", "real messages", len(m_rows)))
        rows_all = d_rows + m_rows
        add(part, "danger", Counter(r["danger"].strip() for r in rows_all))
        add(part, "drug", multi(r["drug"] for r in rows_all))
        add(part, "script", Counter(r["script"].strip() for r in rows_all))
        add(part, "source", Counter(r.get("source_id") or r.get("_file", "") for r in rows_all))
        add(part, "request", Counter(r["request"].strip() for r in rows_all))
    if skipped:
        add("real messages not in the split", "reason", skipped)

    if evals:
        write_csv(out / "test" / "eval-set-v1.csv", he, evals)
        write_jsonl(out / "test" / "test.jsonl", [{k: r.get(k, "") for k in he} for r in evals])
        stats.append(("test", "records", "total", len(evals)))
        for dim in ("danger", "script", "expected_behaviour"):
            add("test", dim, Counter(r[dim].strip() for r in evals))
        add("test", "drug", multi(r["drug"] for r in evals))
    else:
        print("WARNING: no eval-set file found: test part is empty")

    # 5. language corpus
    hg, lines = merged(tables, "general")
    if hg:
        write_csv(out / "language" / "darija-general-v1.csv", hg, lines)
        write_jsonl(out / "language" / "language.jsonl", [{k: r.get(k, "") for k in hg} for r in lines])
        stats.append(("language", "lines", "total", len(lines)))
        add("language", "source", Counter(r["source_id"] for r in lines))
        add("language", "script", Counter(r["script"] for r in lines))
    else:
        print("WARNING: no darija-general file found: language part is empty")

    # 6. support files
    for kind in ("crisis", "contacts", "context", "register"):
        for t in (x for x in tables if x.kind == kind):
            write_csv(out / "support" / (t.path.name), t.header, [r for _, r in t.rows])

    # 7. stats and manifest
    with open(out / "stats.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["part", "dimension", "value", "count"])
        w.writerows(stats)
    write_csv(out / "split-manifest.csv", ["id", "type", "danger", "split"],
              [dict(id=p["id"], type=p["type"], danger=p["danger"], split=split[p["id"]]) for p in
               sorted(pool, key=lambda p: (split[p["id"]], p["id"]))])
    if draft:
        (out / "README_DRAFT.txt").write_text(
            "DRAFT: made with --draft or while the validator reported errors. Do not use these counts in the paper.\n"
            f"Validator report: {a.report}\n", encoding="utf-8")

    n_tr = sum(1 for v in split.values() if v == "train")
    n_dv = sum(1 for v in split.values() if v == "dev")
    print(f"\n{'DRAFT' if draft else 'RELEASE'} written to {out}")
    print(f"  passages {len(passages)}, dialogues {len(dialogues or [])}, labelled real messages "
          f"{sum(1 for p in pool if p['type'] == 'message')}, eval {len(evals)}, language lines {len(lines)}")
    print(f"  train {n_tr}, dev {n_dv} (dev share {n_dv / max(1, n_tr + n_dv):.0%})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
