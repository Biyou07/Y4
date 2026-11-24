# check_spelling.py: Darija spelling check (Task 6)

Flags Darija text that is not written the agreed way and says what the agreed spelling is.
The rules come from **darija-spelling-rules-v0** and **slang-glossary-v1**. The same rules are
available as `normalise()`, the first version of the app's text normaliser.

## Run it

1. Export each sheet as CSV (File > Download > CSV) into one folder: `dialogues_<name>.csv`,
   `context-set-v1.csv`, `eval-set-v1.csv`, `crisis-templates-v1.csv`, and `slang-glossary-v1.csv`.
2. Run:

       python check_spelling.py FOLDER                (uses slang-glossary*.csv found in the folder)
       python check_spelling.py FOLDER --real         (also checks messages_real_*, raw comments)

Only Python 3 is needed (no installs).

## What you get

- `spelling-report.csv`: one line per problem: file, row_id, owner, field, script, word_found,
  expected, rule, level, context. Open it in Google Sheets (File > Import).
- `spelling-report_<owner>.csv`: the same list for one owner. Send it to that person.
- `spelling-report.txt`: readable version with counts per owner.

Levels:

| Level | Meaning | What to do |
|---|---|---|
| rule | clear break of an agreed rule | fix it |
| variant | another spelling of a word that has an agreed spelling | use the expected spelling |
| check | probably wrong | look at it; ignore it if the sentence is fine |

## What it checks

Arabic script: no diacritics (also shadda) and no tatweel; ڨ ڤ گ must be ق; ما is written as a
separate word (ما تخليهش, not ماتخليهش); the final ش is attached to the verb (ما تستناش,
not ما تستنا ش); ما + verb without ش is a `check`; words in the rules table and the glossary written
another way (هذا, بزااف, طاكسي) are `variant`.

Arabizi (script arabizi and mixed-fr): 9 / 5 / 8 used as letters (use q / kh / gh); sh must be ch;
`ma` written attached to the verb; a separate `ch`; ma + verb without ch is a `check`; known other
spellings (nbghi, bzaf, wesh, kifah, chokran) are `variant`.

French text is not checked. `CRISIS_TEMPLATE` answers are skipped.

## Not checked

The u / ou vowel, j / dj, ة / ه, short vowels, and Latin letters used for Arabic words that are not in
the tables. A word that is not in the tables or the glossary is never flagged.

## Change the rules

At the top of `check_spelling.py`: `AR_LEXICON` and `LAT_LEXICON` map the agreed spelling to the other
spellings people use (add a word when the team agrees on one), `ARABIC_NEGATION_OK` and
`LATIN_NEGATION_OK` list words that look like a negation but are not, and `KINDS` says which column of
each file is checked. The glossary is read from its columns canonical_arabic, canonical_arabizi,
variants and script; variants of French-script terms are ignored.

## Known limits

- The tables I added list common other spellings, they are not a full list: extend them.
- Glossary variants are suggestions. Some change the meaning (كاشي -> كاشيات, طاكسي -> تاكسي) and place
  names can match (dar el beida -> bayda). They are reported but `normalise()` does not apply them
  unless `use_glossary=True`.
- `check` lines include false alarms, for example ما + subjunctive (بلا ما نتخاصم).
- Real comments (`--real`) are raw, so they produce many findings; that is expected.

## Use as a normaliser

    from check_spelling import Rules, normalise
    rules = Rules()
    normalise("عيّط دروك. ما تستنا ش", "arabic", rules)    # -> 'عيط دروك. ما تستناش'
