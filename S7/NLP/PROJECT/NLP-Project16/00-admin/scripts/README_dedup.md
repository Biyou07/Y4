# dedup_passages.py (Task 5, knowledge-base deduplication)

Finds near-duplicate passages across all passages*.csv files, keeps the clearer one and writes its id in
`redundant_with` on the other. Nothing is deleted.

## Run it (once Souha's AND Malak's passages are in the folder)

    pip install sentence-transformers scikit-learn numpy
    python dedup_passages.py FOLDER -o dedup-out

FOLDER holds the CSV exports (passages_souha.csv, passages_malak.csv, ...). The first run downloads the
model paraphrase-multilingual-MiniLM-L12-v2 (about 470 MB) from Hugging Face, so it needs internet access.
Google Colab works.

## What you get (dedup-out)
- knowledge_base/passages.csv : all passages, duplicates marked in redundant_with
- dedup-report.csv / .txt     : every pair, similarity, which passage is kept and why

## Rules
- Threshold 0.85: pairs at or above it are marked. Pairs between 0.70 and 0.85 are listed as "review" and
  NOT marked: read them and mark by hand if they are the same fact.
- Kept passage = the one closest to 100 words, then the lower id. This is only a suggestion: read the pairs,
  and if the other passage is clearer, swap the ids by hand.
- Existing redundant_with values are never overwritten.
- The validator checks that redundant_with points to an existing passage, not to itself.

## Fallback mode (read this)
If the model cannot be loaded, the script does not stop: it uses TF-IDF on character n-grams and prints
WARNING. In that mode it only finds near-copies written in the same language. It does NOT find the same
fact in English and in French. A "no duplicates" result in fallback mode means nothing for a release.

## State on 2026-11-23
Only Souha's 20 passages exist. It was run in fallback mode on them: no pair above 0.49, so nothing was
marked. Malak's passages are not in Drive yet, and the real model could not be downloaded in the
environment used (Hugging Face blocked). The real run is still to do.
