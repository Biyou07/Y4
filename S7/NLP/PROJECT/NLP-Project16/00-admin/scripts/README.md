# validate_dataset.py - Project 16 dataset validator

Checks every dataset file against **dataset-format-v1** so mistakes are found before the merge, not after.
**Nothing is merged while the report contains errors.**

## Run it

1. Each teammate exports their Google Sheet as CSV (File > Download > Comma-separated values) and puts the
   file in one folder, keeping the sheet name as the file name (for example `passages_souha.csv`).
2. Run (Python 3.9+, no installation needed):

```
python validate_dataset.py path/to/folder
python validate_dataset.py path/to/folder -o validation-report.txt
```

Options: `-r` also look in sub-folders, `--leak-threshold 0.9` similarity above which an eval message counts as
"almost the same" as a training message, `--no-leak-check`, `--strict` (warnings make the exit code 1 too).
`pip install rapidfuzz` makes the near-duplicate check faster (optional).

The script prints one line per file, writes `validation-report.txt`, and exits with code 1 if there is any error.

## File names it recognises

| Part | File name |
|---|---|
| Passages | `passages_<firstname>.csv` |
| Dialogues | `dialogues_<firstname>.csv` |
| Real messages | `messages_real_<firstname>.csv` |
| Context set | `context-set-v1.csv` |
| Evaluation set | `eval-set-v1.csv` |
| Source register | `source-register.csv` |
| General Darija corpus | `darija-general-v1.csv` (only privacy is checked, its columns are not fixed yet) |
| Crisis templates | `crisis-templates-v1.csv` |
| Emergency contacts | `emergency-contacts-v1.csv` |

Other CSV files in the folder are skipped (for example the merged `passages.csv`).

## Reading the report

One line per problem. The row number is the **spreadsheet row** (row 1 is the header):

```
passages_souha, row 12: text has 172 words (must be 50-150)
dialogues_abdellah, row 4: danger is crisis: assistant_answer must be exactly CRISIS_TEMPLATE, not a written answer
```

Lines starting with `WARNING` do not block the merge but should be looked at (for example a real message
that Ahmed has not labelled yet, or a source with no file name).

## What it checks

- Columns are exactly those of dataset-format-v1, in the right order.
- Ids are unique and follow the patterns: `P-S08-001`, `D-AG-001`, `M-S25-0001`, `E-001`; the source inside a
  passage or message id matches its `source_id`; dialogue initials match the file's author (warning).
- Values of type, drug, language, script, user_type, request, danger, drug_sense, sense and
  expected_behaviour are in the allowed lists. Write them in lower case as in the format document
  (`low`, `person who uses`).
- Passage text is 50-150 words; assistant answers are at most 80 words.
- Danger `crisis` means `assistant_answer` is exactly `CRISIS_TEMPLATE` (and the other way round).
- Every `passage_id` cited in dialogues and eval-set-v1, every `redundant_with`, and every `source_id`
  exists; every message `origin` in the context set is `invented` or an existing `msg_id`.
- Source register has no blank language, licence, reliability, type or status.
- No email, link, @mention or phone number in any text. Note: a helpline number inside a passage is also
  flagged. If a passage must keep an official number, move it to emergency-contacts-v1.
- Crisis templates: 9 rows (3 situations x 3 versions) and every `contacts_used` id exists in
  emergency-contacts-v1, whose rows must have an official source link and a check date.
- No eval-set-v1 message appears, exactly or almost exactly, in dialogues, real messages, the context set
  or the general corpus (text is compared after lower-casing and removing punctuation and Arabic diacritics).

## Changing the rules

All allowed lists, word limits and id patterns are at the top of `validate_dataset.py`. If the label guide
moves to v1 (new drug, request or danger values), edit the lists there and tell the team.

## Limits

It checks the format, not the content: it cannot tell whether a Darija answer is correct, whether the facts
come from the cited passage, or whether a phone number is right. Those are checked at the team meeting.
