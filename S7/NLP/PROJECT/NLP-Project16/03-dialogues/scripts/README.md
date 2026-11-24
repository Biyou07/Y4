# filter_darija.py

Builds two sheets of dataset-format-v1 from the public Darija datasets registered as S30–S33:

| Mode | Output (in `03-dialogues/`) | What it keeps |
|---|---|---|
| `messages` | `messages_real_malak.csv` / `.xlsx` | Darija or Arabizi lines that contain a glossary term, columns `msg_id` to `drug_term` filled, the labelling columns left empty for Ahmed |
| `general` | `darija-general-v1.csv` / `.xlsx` | 5,000 ordinary Darija lines (1,800 from S30, 1,500 from S31, 500 from S32, 1,200 from S33) with no glossary term; the `.xlsx` has the count per source in row 1 |

## Glossary version used

**`slang-glossary-v1.csv` applied.** Updated with the official team slang glossary v1 (108 terms, 56 marked ambiguous/polysemic). Reads `term`, `canonical_arabic`, `canonical_arabizi`, and `variants`, excludes out-of-place false-positive homographs and prefix collisions (lottery *قرعة*, hidden-camera *كاميرا كاشي*, `rouge a levres` / `pasport rouge`, *كوكا* / Coca-Cola, *فروج*, *لحقن*, *جوان كيلاص*, *جامبو*, *كفالي*, *ليريك*, *افيون* = *avion*, *chrabt* verb, *canon* cameras, *joint de culasse*, biology *COX*, *فاليوم* = "per day", *كراك* = "كي راك", *marto* = "his wife", *wed* = Oued, etc.), and uses a two-tier selector to keep **185 balanced rows** (**143** genuine drug/drug-context rows + **42** curated normal-meaning context rows from `TIER2_ALLOWED_TERMS` for Mohamed Ayoub).

Both `messages` and `general` modes have been rerun with `slang-glossary-v1.csv`.

## How to run

Needs Python 3.10+ with `pandas`, `pyarrow` and `openpyxl`. The raw data must be in `01-sources/raw/` (see `01-sources/register_rows_malak.csv` for links).

```
python filter_darija.py messages --glossary slang-glossary-v1.csv
python filter_darija.py general  --glossary slang-glossary-v1.csv
```

The glossary CSV needs a `term` column. Optional columns: `canonical_arabic`, `canonical_arabizi`, `variants` (spellings separated by `;`), `ambiguous` (`yes`/`no`).

Options for `messages`: `--target` (rows to keep, default 185), `--per-term-cap` (Tier 1 max rows per term, default 18), `--ambig-cap` (Tier 2 max normal-meaning rows per term, default 3), `--seed` (default 15, the same seed gives the same sheet).

## What the filter does

1. **Reads** S30 (`v1` split only; the `train` split is 2,324 long, uncleaned blocks), S31 (the `text` column only, never the video URL or like count), S32 (the `# text` lines of the CoNLL-U files), and S33 (`DarjaCore/algerian-darja-sample` Telegram corpus parquet).
2. **Anonymises**: removes links, e-mail addresses, `@mentions`, Latin-script reply handles at the start of Arabic-script comments, and standalone numbers. Digits inside words are kept because Arabizi uses them as letters (`ta3`, `7aja`, `9al`).
3. **Filters profanity**: excludes obscene terms, sexual profanities, and vulgar slurs in both Arabic script and Arabizi (while preserving innocent words like *زبدة* and *بسباس*).
4. **Script**: `arabic` if Arabic letters dominate; otherwise `mixed-fr` when at least two words and a fifth of the words are common French words, else `arabizi`.
5. **Darija check**: an Arabic-script line needs two different Darija marker words in `general` mode (or one in `messages` mode to improve recall) or the ما…ش negation (مانديرش); a Latin-script line needs one Arabizi marker (wach, rani, bzaf, ta3, …), a digit-letter like `3` or `7` inside a word, or the ma…ch negation. Mostly-MSA, French-only and other-language lines are dropped.
6. **Removes duplicates** after normalising spelling (hamza forms, ة/ه, ى/ي, ڨ/ق, accents, repeated letters), and drops lines longer than 60 words in `general` mode (90 words in `messages` mode).
7. **Matches terms & filters false positives**: matches phrases first (`قرعة شراب`, `morceau zatla`, `la roche`), then whole words with attached Arabic prefixes (`ال`, `بال`, `وال`, `فال`, `لل`, `و`, `ب`, `ف`, `ل`) excluding `DROP_PREFIXED_FORMS` (`فروج`, `بروج`, `لروج`, `لحقن`), rejecting known out-of-place homographs (US visa lottery *قرعة*, *كاميرا كاشي*, `rouge a levres`, *كوكا* / Coca-Cola, *جوان كيلاص*, *جامبو*, *كفالي*, *canon*, *cox*, *joint de culasse*, *فاليوم* = "per day", *marto* = "his wife"). `drug_term` records the matched spelling.
8. `general` additionally drops lines under 4 words and every line matching any raw glossary term (without false-positive exceptions), so the two sheets never overlap.

## Known limits

- Personal names inside a sentence (for example "خويا رمزي", "هشام") are **not** removed automatically. The anonymisation rules mentioned in dataset-format-v1 were not available; check the `text` column by hand before freezing.
- The Darija check is a word-list heuristic: a few Moroccan or MSA-leaning lines and some French-heavy code-switched lines can pass.
- S30 `v1` lines are sometimes cut mid-word by the dataset author.
- S32 is CC BY-SA 4.0: anything published that reuses those sentences must keep that licence.
