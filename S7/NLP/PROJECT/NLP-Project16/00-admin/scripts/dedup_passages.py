#!/usr/bin/env python3
"""
dedup_passages.py - Project 16, Task 5: knowledge-base deduplication

Reads every passages*.csv in FOLDER (Souha's, Malak's, ...), compares all passages with each other,
lists every pair above the threshold, keeps the clearer passage of each pair and writes the id of the
kept passage in the other passage's redundant_with cell. Nothing is deleted: duplicates stay in the file
and are only marked (the merge keeps them, the retrieval index skips rows with a redundant_with).

Usage
    python dedup_passages.py FOLDER                       # default model, threshold 0.85
    python dedup_passages.py FOLDER -o OUTDIR --threshold 0.85 --review-floor 0.70
    python dedup_passages.py FOLDER --model paraphrase-multilingual-MiniLM-L12-v2
    python dedup_passages.py FOLDER --fallback            # force the model-free fallback (see below)

Needs   pip install sentence-transformers scikit-learn numpy
The model is downloaded from Hugging Face the first time (about 470 MB). If it cannot be loaded the script
does NOT stop: it switches to a model-free fallback (TF-IDF on character n-grams) and says so loudly in the
report. The fallback only finds near-copies in the same language. It cannot find the same fact written in
English and in French. Run the real model before trusting "no duplicates found".

Output (OUTDIR, default ./dedup-out)
    knowledge_base/passages.csv   all passages, same 10 columns as dataset-format-v1, duplicates marked
    dedup-report.csv              one row per pair: ids, similarity, which one is kept, why, status
    dedup-report.txt              the same, readable, with the mode used and the counts

Decision rule ("keep the clearer passage"): inside a group of duplicates, keep the passage whose length is
closest to 100 words (the middle of the 50-150 range), then the lower id. This is a suggestion: the report
marks pairs between the review floor and the threshold as "review" and does not mark them. A person
reads the pairs before the merge. Existing redundant_with values are never overwritten.
"""
import argparse
import csv
import re
import sys
from pathlib import Path

import numpy as np

COLS = ["passage_id", "source_id", "pages", "type", "topic", "drug", "language", "text", "redundant_with", "cleaned_by"]
DEFAULT_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"


def read_passages(folder):
    rows, seen = [], {}
    files = sorted(p for p in Path(folder).glob("passages*.csv"))
    if not files:
        sys.exit(f"no passages*.csv found in {folder}")
    for f in files:
        with open(f, newline="", encoding="utf-8-sig") as fh:
            rd = csv.DictReader(fh)
            miss = [c for c in COLS if c not in (rd.fieldnames or [])]
            if miss:
                sys.exit(f"{f.name}: missing column(s) {', '.join(miss)}")
            for r in rd:
                pid = r["passage_id"].strip()
                if not pid:
                    continue
                if pid in seen:
                    sys.exit(f"passage_id {pid} appears in {seen[pid]} and {f.name}")
                seen[pid] = f.name
                r = {c: (r.get(c) or "").strip() for c in COLS}
                r["_file"] = f.name
                rows.append(r)
    return rows, [f.name for f in files]


def embed(texts, model_name, force_fallback):
    """Returns (unit-length matrix, mode description)."""
    if not force_fallback:
        try:
            from sentence_transformers import SentenceTransformer
            m = SentenceTransformer(model_name)
            v = m.encode(texts, normalize_embeddings=True, show_progress_bar=False)
            return np.asarray(v), f"model: {model_name}"
        except Exception as e:  # missing package, no network, wrong name...
            print(f"WARNING: could not load '{model_name}' ({type(e).__name__}: {str(e)[:120]}).", file=sys.stderr)
            print("WARNING: using the model-free fallback (TF-IDF char n-grams): near-copies in the same language only.",
                  file=sys.stderr)
    from sklearn.feature_extraction.text import TfidfVectorizer
    x = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), sublinear_tf=True).fit_transform(texts)
    return x.toarray(), "FALLBACK: TF-IDF character n-grams (no multilingual model; cross-language duplicates NOT detected)"


def words(t):
    return len(re.findall(r"\S+", t))


def clarity_key(r):
    w = words(r["text"])
    return (0 if 50 <= w <= 150 else 1, abs(w - 100), r["passage_id"])


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("folder")
    ap.add_argument("-o", "--out", default="dedup-out")
    ap.add_argument("--threshold", type=float, default=0.85)
    ap.add_argument("--review-floor", type=float, default=None,
                    help="pairs from here up to the threshold are listed as 'review' (default 0.70, fallback 0.50)")
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--fallback", action="store_true", help="skip the model, use TF-IDF")
    a = ap.parse_args(argv)

    rows, files = read_passages(a.folder)
    vecs, mode = embed([r["text"] for r in rows], a.model, a.fallback)
    fallback = mode.startswith("FALLBACK")
    floor = a.review_floor if a.review_floor is not None else (0.50 if fallback else 0.70)

    sim = vecs @ vecs.T
    n = len(rows)
    pairs = [(float(sim[i, j]), i, j) for i in range(n) for j in range(i + 1, n) if sim[i, j] >= floor]
    pairs.sort(reverse=True)

    # union-find over the pairs that reach the threshold
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for s, i, j in pairs:
        if s >= a.threshold:
            parent[find(i)] = find(j)
    groups = {}
    for i in range(n):
        groups.setdefault(find(i), []).append(i)
    keep = {}  # index -> index of the kept passage of its group
    for g in groups.values():
        best = min(g, key=lambda k: clarity_key(rows[k]))
        for k in g:
            keep[k] = best

    marked = 0
    for k, b in keep.items():
        if k != b and not rows[k]["redundant_with"]:
            rows[k]["redundant_with"] = rows[b]["passage_id"]
            marked += 1

    out = Path(a.out)
    (out / "knowledge_base").mkdir(parents=True, exist_ok=True)
    with open(out / "knowledge_base" / "passages.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=COLS, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)

    rep_rows = []
    for s, i, j in pairs:
        ri, rj = rows[i], rows[j]
        if s >= a.threshold:
            b = keep[i]  # i and j are in the same group, so keep[i] == keep[j]
            kept = rows[b]
            others = [rows[x] for x in (i, j) if x != b]
            dropped = {"passage_id": " + ".join(o["passage_id"] for o in others)}
            status = "marked"
            reason = ("closer to 100 words (%d words)" % words(kept["text"]))
            if len(groups[find(i)]) > 2:
                reason += "; group of %d passages" % len(groups[find(i)])
        else:
            kept = dropped = None
            status = "review (not marked)"
            reason = "below threshold: a person decides"
        rep_rows.append({
            "passage_a": ri["passage_id"], "passage_b": rj["passage_id"], "similarity": f"{s:.3f}",
            "source_a": ri["source_id"], "source_b": rj["source_id"], "language_a": ri["language"], "language_b": rj["language"],
            "kept": kept["passage_id"] if kept else "", "redundant_with_set_on": dropped["passage_id"] if dropped else "",
            "status": status, "reason": reason,
        })
    cols = list(rep_rows[0].keys()) if rep_rows else ["passage_a", "passage_b", "similarity", "status"]
    with open(out / "dedup-report.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        w.writerows(rep_rows)

    n_marked_pairs = sum(1 for r in rep_rows if r["status"] == "marked")
    lines = [f"# dedup_passages.py report",
             f"mode: {mode}",
             f"files: {', '.join(files)}",
             f"passages: {n}   threshold: {a.threshold}   review floor: {floor}",
             f"pairs at or above the threshold: {n_marked_pairs}   passages newly marked redundant: {marked}",
             f"pairs in the review band: {len(rep_rows) - n_marked_pairs}"]
    if fallback:
        lines.append("WARNING: fallback mode. Same fact in two languages is NOT detected. Rerun with the model before release.")
    lines.append("")
    for r in rep_rows:
        lines.append(f"{r['passage_a']} ~ {r['passage_b']}  sim {r['similarity']}  [{r['source_a']}/{r['language_a']} vs {r['source_b']}/{r['language_b']}]  "
                     + (f"keep {r['kept']}, redundant_with set on {r['redundant_with_set_on']} ({r['reason']})" if r['status'] == 'marked' else r['status']))
    if not rep_rows:
        lines.append("no pair reaches the review floor")
    (out / "dedup-report.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines[:6]))
    print(f"-> {out}/knowledge_base/passages.csv, dedup-report.csv, dedup-report.txt")
    return 0


if __name__ == "__main__":
    sys.exit(main())
