# merge_split_stats.py: merge, split and statistics (Task 8)

Builds the `dataset-v1` folder from the team's CSV exports. It first runs `validate_dataset.py` and
**stops if the validator reports any error**, so nothing is merged while there are errors.

## Run it

1. Put all final CSV exports in one folder (same names as for the validator): `passages_<name>`,
   `dialogues_<name>`, `messages_real_<name>`, `eval-set-v1`, `darija-general-v1`, `context-set-v1`,
   `crisis-templates-v1`, `emergency-contacts-v1`, `source-register`.
2. Keep `validate_dataset.py` in the same folder as this script, then:

       python merge_split_stats.py FOLDER -o OUTPUT_FOLDER            # release
       python merge_split_stats.py FOLDER -o OUTPUT_FOLDER --draft    # test run

   `--draft` ignores validator errors and writes `dataset-v1-DRAFT` with a README_DRAFT.txt. Do not use
   draft numbers in the paper.

## What it writes

| Path | Content |
|---|---|
| `knowledge_base/passages.csv` and `.jsonl` | all passages; duplicates stay, with `redundant_with` filled (Task 5) |
| `train/`, `dev/` | `dialogues.csv`, `messages_real.csv` and `train.jsonl` / `dev.jsonl` |
| `test/` | `eval-set-v1.csv` and `test.jsonl` (the held-out evaluation set, never used for training) |
| `language/` | `darija-general-v1.csv` and `language.jsonl` |
| `support/` | crisis templates, emergency contacts, context set, source register |
| `stats.csv` | part, dimension, value, count: totals and counts per danger level, drug, script, source, request |
| `split-manifest.csv` | the split of every dialogue and message (id, type, danger, train or dev) |

## How the split works

Dialogues and labelled real messages are pooled, then split about 85% train / 15% dev **separately for each
danger level** (none, low, high, crisis), so each level has the same share in both parts. The seed is fixed
(`--seed 42`), so the same input gives the same split. Rounding means the share is close to 15%, not exact.

A real message is *labelled* when drug_sense, drug, user_type, request and danger are all filled and none is
`Skip`. Messages that are `Skip` or not yet labelled stay out of the split; their counts are in `stats.csv`.

The script also checks that no eval-set message is identical to a train or dev message (the validator
checks near matches too).

## Limits

- It does not clean or deduplicate: run Task 5 first so `redundant_with` is filled.
- It does not check content, only format (that is the validator's job).
- The three parts that need other people's files (eval-set, darija-general, labelled messages) are empty
  until those files exist; the script prints a warning for each.
