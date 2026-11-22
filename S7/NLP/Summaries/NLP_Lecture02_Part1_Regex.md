# Natural Language Processing: Regular Expressions (Lecture 2, Part 1)
**Metacharacters, Shorthands, Modular Grouping, Lookaround Assertions & Pattern Engineering**  
*Course: Natural Language Processing (ENSIA 2026–2027) — Prof. Ahmed Guessoum*

---

## Overview & Scope: Regular Expressions in Text Processing Pipelines

A **Regular Expression (regex)** is a formal algebraic language designed for specifying, searching, and manipulating string patterns within text. While modern NLP relies on statistical classifiers and large neural language models for high-level semantic reasoning, regular expressions remain an indispensable foundational tool across both industry and academia.

```
                      Raw Unstructured Text Corpus
                                   │
                                   ▼
          ┌─────────────────────────────────────────────────┐
          │  Regular Expression Processing Engine            │
          │  • Data Ingestion, Scraping & Normalization     │
          │  • Tokenization & Sentence Segmentation Rules   │
          │  • Rule-Based Entity & Structural Extraction    │
          └─────────────────────────────────────────────────┘
                                   │
                                   ▼
              Downstream NLP Systems & Neural Pipelines
```

Regexes drive early-stage text pre-processing pipelines, data cleaning, entity extraction, web scraping, and rule-based conversational heuristics (such as ELIZA). Developing effective patterns is an empirical craft governed by the tension between **precision** (minimizing false positives) and **recall** (eliminating false negatives).

---

## 1. Basic Matching & Literal Semantics

Regex engines process text sequentially from left to right. By default, regular expressions perform exact, byte-level character matching:

* **Case-Sensitivity:** Plain text patterns demand exact character-for-character agreement, including case.

> ### 🔍 Standout Example: Literal Matching
> **Pattern:** `woodchuck`  
> **Target Text:** `"A woodchuck saw Woodchuck."`  
> * $\checkmark$ **Matches:** The first token `"woodchuck"` (exact character and casing match).  
> * $\times$ **Rejects:** The capitalized token `"Woodchuck"` (fails because `'W'` $\ne$ `'w'`).

---

## 2. Disjunction & Character Classes (`[...]`)

When text can contain alternative characters at a specific string index, square brackets `[...]` define a **character class** matching any single character from the enclosed set.

| Expression Type | Syntax & Formal Definition | Prominent Example | Match Verdict |
| :--- | :--- | :--- | :--- |
| **Explicit Disjunction** | `[wW]` matches lowercase `w` or uppercase `W`. Character order is arbitrary. | `[wW]oodchuck` | $\checkmark$ `"woodchuck"`, `"Woodchuck"`<br>$\times$ `"WOODCHUCK"` (interior letters are uppercase) |
| **Digit Character Set** | `[0123456789]` matches any single decimal digit from 0 to 9. | `Box [0-9]` | $\checkmark$ `"Box 1"`, `"Box 9"`<br>$\times$ `"Box 10"` (contains two digits) |
| **Lowercase Range** | `[a-z]` matches any lowercase ASCII letter using hyphen `-` range syntax. | `[a-z]eans` | $\checkmark$ `"beans"`, `"jeans"`<br>$\times$ `"Beans"` |
| **Uppercase Range** | `[A-Z]` matches any single uppercase ASCII letter. | `[A-Z]own` | $\checkmark$ `"Down"`, `"Town"`<br>$\times$ `"down"` |
| **Concatenated Ranges** | `[A-Za-z0-9]` matches any alphanumeric character without delimiters. | `ID-[A-Za-z0-9]` | $\checkmark$ `"ID-a"`, `"ID-7"`, `"ID-Z"`<br>$\times$ `"ID-$"` |
| **Pipe Operator (`\|`)** | Alternatives across multi-character strings. Has the **lowest operator precedence**. | `groundhog\|woodchuck` | $\checkmark$ `"groundhog"`, `"woodchuck"`<br>$\times$ `"groundchuck"` |

---

## 3. Negated Character Classes (`[^...]`) & Syntactic Exceptions

The caret symbol `^` inverts a character class, matching any single character **not** contained within the set.

* **The Caret Position Rule:** The caret negates **only** when placed as the **very first character** immediately following the opening bracket `[`. Placed anywhere else, it is evaluated strictly as a literal caret symbol!
* **Metacharacter Escaping Inside Brackets:** Special metacharacters (`.`, `*`, `+`, `?`) automatically **lose their special meaning** inside square brackets and are evaluated as plain literal characters.

> ### 🔍 Standout Contrasting Examples: Bracket Negation & Escaping Rules
> 
> * **`[^A-Z]` (Negated Uppercase):**  
>   Matches any single character that is **not** an uppercase letter.  
>   *Target Text:* `"Oyfn pripetchik"`  
>   * $\checkmark$ **Matches:** `"y"`, `"f"`, punctuation, spaces.  
>   * $\times$ **Rejects:** Uppercase `"O"`.
> 
> * **`[^Ss]` (Negated S):**  
>   Matches any character other than uppercase `'S'` or lowercase `'s'`.  
>   *Target Text:* `"I have no exquisite reason"`  
>   * $\checkmark$ **Matches:** `"I"`, `"h"`, `"a"`, spaces.  
>   * $\times$ **Rejects:** Lowercase `"s"` in `"exquisite"`.
> 
> * **`[e^]` (Caret Not at First Position):**  
>   Matches either the letter `'e'` or the literal caret symbol `'^'`.  
>   *Target Text:* `"Look up ^ now"`  
>   * $\checkmark$ **Matches:** Literal `"^"` and letter `"e"`.
> 
> * **`[^.]` (Period Inside Brackets):**  
>   Matches any character that is **not** a literal period (the dot is **not** a wildcard inside brackets!).  
>   *Target Text:* `"End."`  
>   * $\checkmark$ **Matches:** `"E"`, `"n"`, `"d"`.  
>   * $\times$ **Rejects:** The final literal period `"."`.
> 
> * **`[.*+?]` (Metacharacters as Literals):**  
>   Matches a literal dot, asterisk, plus, or question mark. Special quantifiers lose their meaning inside brackets.

---

## 4. Shorthand Character Classes (Convenient Aliases)

Standard regex implementations provide predefined shorthand aliases for frequent character classes:

| Alias | Class Expansion | Semantic Definition | Standalone Example | Target Match Verdict |
| :---: | :--- | :--- | :--- | :--- |
| `\d` | `[0-9]` | Any single decimal digit | `\d\d\d` | $\checkmark$ `"451"` in `"Fahrenheit 451"` |
| `\D` | `[^0-9]` | Any character that is **not** a decimal digit | `\D+` | $\checkmark$ `"Blue Moon"` in `"Blue Moon 1934"` |
| `\w` | `[a-zA-Z0-9_]` | Alphanumeric character or underscore (word token) | `\w+` | $\checkmark$ `"Daiyu"`, $\checkmark$ `"user_2"` |
| `\W` | `[^\w]` | Non-alphanumeric and non-underscore character | `\W` | $\checkmark$ `"!"` in `"Look!"`, spaces, commas |
| `\s` | `[ \r\t\n\f]` | Any whitespace symbol (space, tab, newline, return) | `Look\s+up` | $\checkmark$ `"Look up"`, $\checkmark$ `"Look\t\tup"` |
| `\S` | `[^\s]` | Any non-whitespace symbol | `\S+` | $\checkmark$ `"NLP"` in `"  NLP  "` |

---

## 5. Anchors & Boundary Conditions

Anchors do not consume characters from the text stream; they are **zero-width assertions** enforcing positional constraints where matching must initiate or terminate.

| Anchor Type | Positional Assertion | Prominent Example | Match Analysis |
| :--- | :--- | :--- | :--- |
| **Caret Anchor (`^`)** | Asserts match begins at the **start of a line or string**. | `^[A-Z]` | $\checkmark$ Matches `"Palo Alto"`<br>$\times$ Rejects `"in Palo Alto"` (uppercase not at line start) |
| **Negated Class at Line Start** | `^` outside brackets is anchor; `^` inside brackets is negation. | `^[^A-Za-z]` | $\checkmark$ Matches `"1st Step"` (starts with digit `1`)<br>$\times$ Rejects `"First Step"` |
| **Dollar Anchor (`$`)** | Asserts match terminates at the **end of a line or string**. | `\.$` | $\checkmark$ Matches literal period in `"The end."`<br>$\times$ Rejects `"The end. More text"` |
| **Wildcard at Line End** | Wildcard `.` followed by line end anchor `$`. | `.$` | $\checkmark$ Matches `"?"` in `"The end?"`<br>$\checkmark$ Matches `"!"` in `"The end!"` |
| **Word Boundary (`\b`)** | Zero-width boundary between word (`\w`) and non-word (`\W`). | `\bthe\b` | $\checkmark$ Matches `"the"` in `"the cat"`<br>$\times$ Rejects `"other"`, `"theology"`, `"then"` |
| **Non-Word Boundary (`\B`)** | Asserts current index is **not** at a word boundary. | `\Bon\B` | $\checkmark$ Matches `"on"` inside `"continue"`<br>$\times$ Rejects standalone `"on"`, `"only"` |

---

## 6. Wildcards, Optionality & Repetition Quantifiers

Quantifiers define how many times the preceding symbol, bracket class, or grouped block must appear.

* **Any-Character Wildcard (`.`):** Matches any single character except a newline character (`\n`).
* **Optionality Quantifier (`?`):** Matches **zero or one** occurrence of the preceding item ($0$ or $1$).
* **Kleene Star (`*`):** Formally defined by Stephen Cole Kleene, matches **zero or more** occurrences ($0, 1, 2, \dots$).
* **Kleene Plus (`+`):** Matches **one or more** occurrences ($1, 2, 3, \dots$). Equivalent to $aa^*$.
* **Explicit Range Counters (`{n,m}`):** `{n}` matches exactly $n$ times; `{n,m}` matches between $n$ and $m$ times inclusive.

> ### 🔍 Standout Quantifier Demonstrations
> 
> * **Wildcard (`beg.n`):**  
>   * $\checkmark$ **Matches:** `"begin"`, `"begun"`, `"beg3n"`, `"beg n"`.  
>   * $\times$ **Rejects:** `"begnn"` (missing character) and `"begoon"` (two characters).
> 
> * **Optionality (`woodchucks?`):**  
>   * $\checkmark$ **Matches:** `"woodchuck"` ($s$ occurs 0 times) and `"woodchucks"` ($s$ occurs 1 time).
> 
> * **Kleene Star (`to*`):**  
>   * $\checkmark$ **Matches:** `"t"` (zero $o$'s), `"to"` (one $o$), `"too"` (two $o$'s), `"tooo"`.
> 
> * **Kleene Plus (`to+`):**  
>   * $\checkmark$ **Matches:** `"to"`, `"too"`, `"tooo"`.  
>   * $\times$ **Rejects:** Lone `"t"` (requires $\ge 1$ occurrence of $o$).
> 
> * **Range Counters (`A{2,4}`):**  
>   * $\checkmark$ **Matches:** `"AA"`, `"AAA"`, `"AAAA"`.  
>   * $\times$ **Rejects:** `"A"` (below minimum of 2).

---

## 7. Quantifier Mechanics: Greedy vs. Lazy Matching

* **Greedy Evaluation (Default):** Standard quantifiers (`*`, `+`, `{n,m}`) consume as much text as possible, backtracking only when needed.
* **Lazy / Reluctant Evaluation (`*?`, `+?`):** Appending `?` instructs the engine to consume the minimal text necessary to satisfy the match.

> ### 🔍 Side-by-Side Demonstration: Extracting HTML Paragraph Tags
> **Target Text:** `<p>First paragraph.</p><p>Second paragraph.</p>`
> 
> * **Greedy Pattern:** `<p>.*</p>`  
>   * $\checkmark$ **Output Match:** `<p>First paragraph.</p><p>Second paragraph.</p>`  
>   * *Diagnostic:* The greedy `.*` consumes past the first `</p>` all the way to the final `</p>` in the entire document!
> 
> * **Lazy Pattern:** `<p>.*?</p>`  
>   * $\checkmark$ **Match 1:** `<p>First paragraph.</p>`  
>   * $\checkmark$ **Match 2:** `<p>Second paragraph.</p>`  
>   * *Diagnostic:* The lazy `.*?` halts matching immediately at the earliest closing `</p>`.

---

## 8. Summary Cheat Sheet: Basic Metacharacters & Quantifiers

| Symbol | Name | Operational Function | Example | Matches ($\checkmark$) vs. Rejects ($\times$) |
| :---: | :--- | :--- | :--- | :--- |
| `.` | Dot | Any single character except newline | `c.t` | $\checkmark$ `"cat"`, `"cot"` $\quad\times$ `"coat"` |
| `?` | Question | Zero or one occurrence of previous item | `colou?r` | $\checkmark$ `"color"`, `"colour"` $\quad\times$ `"colouur"` |
| `*` | Kleene Star | Zero or more occurrences of previous item | `go*gle` | $\checkmark$ `"ggle"`, `"gogle"`, `"google"` |
| `+` | Kleene Plus | One or more occurrences of previous item | `go+gle` | $\checkmark$ `"gogle"`, `"google"` $\quad\times$ `"ggle"` |
| `^` | Caret | Line or string start anchor | `^Hello` | $\checkmark$ `"Hello world"` $\quad\times$ `"Say Hello"` |
| `$` | Dollar | Line or string end anchor | `world$` | $\checkmark$ `"Hello world"` $\quad\times$ `"worlds"` |

---

## 9. Modular Regex: Grouping & Numbered Capturing Registers

Parentheses `(...)` fulfill two vital operational functions: **operator scoping** (overriding operator precedence) and **register capturing** (storing matched substrings into indexed memory registers).

* **Precedence Scoping:** Quantifiers apply to the entire grouped subexpression: `(woodchuck)+` matches `"woodchuckwoodchuck"`.
* **Numbered Registers (`\1`, `\2`, ...):** Each pair of capturing parentheses copies its matched substring into an indexed memory register ordered by opening parenthesis position.
* **Substitution Syntax (`s/pattern/replacement/`):** Replaces matched text using captured registers. E.g., `s/([0-9]+)/<\1>/` applied to `"the 35 boxes"` stores `"35"` into register `\1` and rewrites to `"the <35> boxes"`.
* **Pattern Backreferencing:** Registers can be evaluated *within the pattern itself* to enforce identity across occurrences.

> ### 🔍 Standout Demonstration: Backreferencing (Slide Example)
> **Regex Pattern:**  
> `/the (.*)er they (.*), the \1er we \2/`
> 
> * $\checkmark$ **Match Case:** `"the faster they ran, the faster we ran"`  
>   *Execution Trace:* Register `\1` captures `"fast"`; register `\2` captures `"ran"`. Backreference `\1er` expects `"faster"` and `\2` expects `"ran"`. Both match perfectly!
> 
> * $\times$ **Rejection Case:** `"the faster they ran, the faster we ate"`  
>   *Execution Trace:* Register `\2` captured `"ran"`, but the second clause has `"ate"`. Because `"ate"` $\ne$ `\2` (`"ran"`), the regex strictly rejects the string!

---

## 10. Non-Capturing Groups (`(?:...)`) for Modular Design

When parentheses are needed solely to group alternatives without consuming memory registers or polluting register numbering, prepend `?:` immediately after the opening parenthesis.

> ### 🔍 Standout Demonstration: Non-Capturing Groups (Slide Example)
> **Regex Pattern:**  
> `/(?:some|a few) (people|cats) like some \1/`
> 
> * **Register Allocation Analysis:** The first group `(?:some|a few)` is non-capturing (unindexed). Therefore, register `\1` refers exclusively to the second group `(people|cats)`.
> * $\checkmark$ **Match Case:** `"some cats like some cats"` $\longrightarrow$ Register `\1` = `"cats"`, identical in both positions.
> * $\times$ **Rejection Case:** `"some cats like some people"` $\longrightarrow$ Register `\1` = `"cats"`, but second position is `"people"` ($\ne$ `\1`).

---

## 11. Lookahead Assertions: Zero-Width Pointer Inspections

Lookaheads are **zero-width assertions**: they test whether a subpattern matches or does not match immediately ahead in the text stream **without advancing the character pointer** or consuming characters into the match buffer.

| Lookahead Type | Syntax & Formal Logic | Operational Behavior |
| :--- | :--- | :--- |
| **Positive Lookahead** | `(?=pattern)`: True if `pattern` matches immediately ahead. | The engine asserts that `pattern` follows. If true, the pointer remains at its current position; subsequent tokens consume the string. |
| **Negative Lookahead** | `(?!pattern)`: True if and only if `pattern` **fails** to match ahead. | The engine asserts that `pattern` does **not** follow. If it fails to match, the assertion succeeds; pointer does not advance. |

> ### 🔍 Step-by-Step Execution Trace: Disallowing Specific Prefixes (Slide Example)
> **Task:** Match any single word at line start that does **not** begin with `"Volcano"`:  
> **Pattern:** `/^(?!Volcano)[A-Za-z]+/`
> 
> * **Candidate String 1:** `"Vesuvius is an active volcano."`
>   1. Start Anchor `^`: Pointer initialized at index 0 (character `'V'`).
>   2. Lookahead `(?!Volcano)`: Engine inspects ahead for `"Volcano"`. Since `"Vesuvius"` $\ne$ `"Volcano"`, negative lookahead **succeeds**!
>   3. Pointer Position: Remains at index 0 (**zero-width assertion consumed zero characters**).
>   4. Token Consumption `[A-Za-z]+`: Consumes and captures `"Vesuvius"`. $\checkmark$ **MATCH SUCCESSFUL**.
> 
> * **Candidate String 2:** `"Volcanoes are dangerous."`
>   1. Start Anchor `^`: Pointer is at index 0 (character `'V'`).
>   2. Lookahead `(?!Volcano)`: Engine inspects ahead and detects `"Volcano"`. Because `"Volcano"` matches, negative lookahead **fails**!
>   3. Verdict: $\times$ **MATCH REJECTED IMMEDIATELY** at index 0. Zero characters consumed.

### 11.1 Practical Lookahead Applications in NLP Text Pipelines
* **Conjunctive Multi-Condition Validation:** Positive lookaheads allow asserting multiple criteria concurrently regardless of character ordering:  
  `^(?=.*[A-Z])(?=.*\d).{8,}$` $\longrightarrow$ Demands at least one uppercase letter **and** at least one digit in $\ge 8$ characters.
* **Exclusion Boundary Filtering:** Negative lookaheads allow filtering out unwanted file extensions or patterns:  
  `^.*(?!\.txt$)[A-Za-z0-9]+$` $\longrightarrow$ Matches alphanumeric tokens that do **not** conclude with `.txt`.

---

## 12. Solved Slide Exercise: Enclosing First & Second Numbers

> ### 📝 Slide Problem Statement (Slide 20 Task)
> *"What if I wanted to surround any first number in a string with `<` and `>` and the second with `[` and `]`?  
> e.g., `'The 35 boxes and 42 items are nice.'` $\longrightarrow$ `'The <35> boxes and [42] items are nice.'` Think about it."*

### 12.1 Theoretical Pure Regex Substitution Formulation

```
Match Pattern :  (\d+)(\D+)(\d+)
Replacement   :  <\1>\2[\3]
```
*(Applied on the first matched occurrence; or full-string capture: `s/^(.*?)(\d+)(.*?)(\d+)(.*)$/\1<\2>\3[\4]\5/`)*

### 12.2 Register Allocation & Structural Decomposition

| Register | Sub-Pattern | Captured Chunk | Operational Role in Output Reassembly |
| :---: | :--- | :--- | :--- |
| `\1` | `(\d+)` | `"35"` | Captures the first numerical sequence; enclosed in `<...>` during output. |
| `\2` | `(\D+)` | `" boxes and "` | Captures the non-digit span; preserved intact between the numbers. |
| `\3` | `(\d+)` | `"42"` | Captures the second numerical sequence; enclosed in `[...]` during output. |

### 12.3 Critical Engineering Nuance: The Multi-Number Greedy Trap
* **Why Greedy `.*` Fails:** If the separator were written using greedy wildcard `(.*)`, an input with 3+ numbers (e.g., `"10 apples, 20 oranges, 30 pears"`):
  * `(\d+)(.*)(\d+)` causes `.*` to greedily consume through `"20"`, capturing `"10"` in `\1` and `"30"` in `\3`!
* **The Solution:** Using non-digits `(\D+)` or lazy wildcard `(.*?)` strictly bounds register `\2` to the immediate gap between the first and second numbers.

---

## 13. Pattern Engineering in NLP: Precision vs. Recall Trade-Off

Developing regexes in NLP is an iterative empirical process balancing two competing error types:

* **False Negatives (Type II Error):** Missing target strings that should match $\Longrightarrow$ Minimizing false negatives increases **recall** (coverage).
* **False Positives (Type I Error):** Incorrectly matching spurious strings $\Longrightarrow$ Minimizing false positives increases **precision** (accuracy).

> ### 🔍 Iterative Refinement Case Study: Extracting the English Article `"the"`
> 
> 1. **Iteration 1 --- Plain Literal `the`:**  
>    *Target Text:* `"The dog chased the cat."`  
>    * $\times$ **Error Diagnosis (Low Recall):** Fails to match capitalized `"The"` at sentence start $\Longrightarrow$ **False Negative**.
> 
> 2. **Iteration 2 --- Disjunctive Capitalization `[tT]he`:**  
>    *Target Text:* `"The other theology student was there."`  
>    * $\times$ **Error Diagnosis (Low Precision):** Matches `"The"`, but also erroneously matches substrings inside `"other"`, `"Theology"`, and `"there"` $\Longrightarrow$ **False Positives**.
> 
> 3. **Iteration 3 --- Word Boundary Isolation `\b[tT]he\b` (or `\W[tT]he\W`):**  
>    *Target Text:* `"The other theology student said the dog was there."`  
>    * $\checkmark$ **Optimal Solution:** Strictly matches standalone `"The"` and `"the"`, cleanly rejecting `"other"`, `"theology"`, and `"there"`. Maximizes precision and recall simultaneously!

---

## 14. Historical Case Study: ELIZA (Joseph Weizenbaum, 1966)

ELIZA was one of the earliest conversational agents, simulating a Rogerian psychotherapist purely through a cascade of regex substitutions and pronoun reflections, with zero syntactic parsers or semantic logic:

| Cascading Regex Substitution Rule | Simulated Dialogue Transformation |
| :--- | :--- |
| `s/.* I'M (depressed\|sad) .*/I AM SORRY TO HEAR YOU ARE \1/` | Patient: `"I'm depressed much of the time."`<br>ELIZA: `"I AM SORRY TO HEAR YOU ARE DEPRESSED"` |
| `s/.* I AM (depressed\|sad) .*/WHY DO YOU THINK YOU ARE \1/` | Patient: `"I am sad today."`<br>ELIZA: `"WHY DO YOU THINK YOU ARE SAD"` |
| `s/.* all .*/IN WHAT WAY?/` | Patient: `"Men are all alike."`<br>ELIZA: `"IN WHAT WAY?"` |
| `s/.* always .*/CAN YOU THINK OF A SPECIFIC EXAMPLE?/` | Patient: `"They're always bugging us about something."`<br>ELIZA: `"CAN YOU THINK OF A SPECIFIC EXAMPLE?"` |

### 14.1 Core Takeaways
* **Cascading Priority:** Rules evaluate in order; the first matching regex triggers the conversational response.
* **Pronoun Inversion:** Maps first-person declarations into second-person inquiries (`I AM` $\rightarrow$ `YOU ARE`).
* **Linguistic Reality:** Proved that surface-level pattern matching and register reassembly can produce realistic dialogue without genuine semantic understanding.

---
*Summary compiled for Natural Language Processing (ENSIA 2026–2027) based on Lecture 2 materials.*
