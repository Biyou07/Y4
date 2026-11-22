# Natural Language Processing: Text Normalization & Edit Distance (Lecture 2, Part 2)
**Tokenization, BPE Learners/Segmenters, Morphological Processing & Levenshtein Alignment**  
*Course: Natural Language Processing (ENSIA 2026–2027) — Prof. Ahmed Guessoum*

---

## Overview & Scope: Text Normalization & String Distance in NLP

Raw natural language text is unstructured, ambiguous, and morphologically diverse. Before feeding textual data into statistical models or deep neural architectures, corpora must undergo **text normalization**: transforming raw character streams into standardized sequences of linguistic tokens.

```
                      Raw Unstructured Text Corpus
                                   │
                                   ▼
          ┌─────────────────────────────────────────────────┐
          │  Text Normalization & Tokenization Pipeline     │
          │  • Word Tokenization & Clitic Splitting         │
          │  • Subword Token Induction (BPE, WordPiece, LM) │
          │  • Case Folding, Lemmatization vs. Stemming     │
          │  • Sentence Boundary Detection                  │
          └─────────────────────────────────────────────────┘
                                   │
                                   ▼
          ┌─────────────────────────────────────────────────┐
          │  String Comparison & Distance Metrics           │
          │  • Minimum Edit Distance (Levenshtein)          │
          │  • Dynamic Programming Matrix Formulation       │
          │  • Backtrace Pointer Alignment                  │
          └─────────────────────────────────────────────────┘
```

This summary details word and subword tokenization, the structural distinction between token learners and segmenters, Byte-Pair Encoding (BPE), morphological lemmatization vs. stemming, sentence boundary detection, and the exact dynamic programming formulation of Minimum Edit Distance.

---

## 1. Corpus Dimensions: Tokens ($N$) vs. Word Types ($|V|$)

Formal quantitative analysis of corpora requires a strict distinction between running tokens and distinct vocabulary types:

* **Token Count ($N$):** The total number of running word occurrences in a text or corpus.
* **Type Count ($|V|$):** The number of distinct, unique word forms composing the corpus vocabulary $V$.
* **Heaps' Law (Vocabulary Growth):** As corpus size $N$ expands, vocabulary size grows continuously without reaching an asymptotic ceiling:
  $$|V| = k N^\beta \qquad (k > 0, \quad 0 < \beta < 1, \quad \text{typically } \beta \approx 0.45 - 0.7)$$
  Large textual corpora never completely saturate vocabulary growth; new types continuously appear.

> ### 🔍 Standout Example: Token vs. Type Measurement
> **Target Text:** `"They slumber, and they dream, and they awake."`
> * **Running Tokens ($N$):** $N = 8$ word occurrences.
> * **Unique Word Types ($|V|$):** $|V| = 5$ distinct vocabulary types: `{"they", "slumber", "and", "dream", "awake"}` (disregarding punctuation and capitalization).

---

## 2. Tokenization Challenges in Natural Language

Naive whitespace splitting (`text.split()`) fails across multiple linguistic phenomena:

| Linguistic Phenomenon | Structural Challenge | Prominent Example & Tokenization Resolution |
| :--- | :--- | :--- |
| **Embedded Punctuation** | Punctuation symbols embedded inside domain entities cannot be stripped blindly. | `m.p.h.`, `Ph.D.`, `AT&T`, `$45.55`, `01/02/06`, `#nlproc`, `someone@cs.edu` must each be preserved as individual single tokens. |
| **Clitics** | A grammatical element that functions phonologically like a word but adheres syntactically to another. | Contractions: `"we're"` $\longrightarrow$ `we` + `'re` (verb *are*).<br>French: `"j'ai"` $\longrightarrow$ `j'` (*je*) + `ai`; `"l'honneur"` $\longrightarrow$ `l'` (*le*) + `honneur`. |
| **Multiword Expressions (MWE)** | Lexical units composed of multiple whitespace-separated tokens that form a single non-compositional semantic concept. | Named locations and idioms: `"Hassi Messaoud"`, `"rock 'n' roll"`, `"New York"` must frequently be treated as single token units. |
| **Scripts Without Whitespace** | Languages that do not use whitespace delimiters between words (e.g., Chinese, Japanese, Thai). | Chinese *hanzi* characters: Each represents a morpheme (meanings: 2.4 morphemes/word). Requires character-level segmentation or statistical sequence models. |

---

## 3. The Modern Subword Paradigm: Token Learners vs. Segmenters

To resolve the dichotomy between massive sparse word vocabularies (which suffer from Out-Of-Vocabulary / OOV words) and pure character tokens (which produce excessively long sequence representations), modern NLP uses **subword tokenization**.

All modern subword algorithms decouple into two distinct operational stages:

| Subword Component | Operational Pipeline Stage | Algorithmic Responsibility & Behavior |
| :--- | :--- | :--- |
| **1. Token Learner** | **Offline Training Phase**<br>*(Run once on raw training corpus)* | Takes a large raw text corpus, initializes a vocabulary of base characters, and induces a fixed vocabulary of $k$ subwords and words by iteratively optimizing a merge or likelihood criterion. |
| **2. Token Segmenter** | **Online Inference / Runtime**<br>*(Run on every unseen input sentence)* | Takes unseen raw text and segments it into a sequence of tokens strictly derived from the induced vocabulary, applying learned rules deterministically or greedily. |

---

## 4. Comparison of Major Subword Tokenization Algorithms

| Algorithm | Induction / Learner Criterion | Segmentation Strategy at Inference | Representative Models |
| :--- | :--- | :--- | :--- |
| **Byte-Pair Encoding (BPE)**<br>*(Sennrich et al., 2016)* | Iterative merge of the most frequent adjacent symbol pair in the training corpus. | Greedy sequential application of learned merges in their exact historical training order. | GPT-2, GPT-3, GPT-4, RoBERTa, LLaMA |
| **WordPiece**<br>*(Schuster & Nakajima, 2012)* | Merges symbol pairs that maximize the language model likelihood of the training data. | Longest-match-first (greedy search from left to right matching the longest subword in vocabulary). | BERT, DistilBERT, Electra |
| **Unigram LM**<br>*(Kudo, 2018)* | Starts with an over-complete vocabulary and progressively prunes tokens that minimize loss. | Probabilistic Viterbi search finding the segmentation maximizing joint token probability. | T5, ALBERT, SentencePiece |

---

## 5. Byte-Pair Encoding (BPE): Algorithmic Mechanics

Byte-Pair Encoding (BPE) is a data-driven subword tokenization algorithm that builds variable-length tokens from bottom-up character merges.

* **End-of-Word Delimiter (`_` or `</w>`):** BPE operates inside whitespace-separated words. A special boundary marker (e.g., `_`) is appended to the final character of each word to distinguish word-final characters from word-internal characters.
* **Vocabulary Initialization:** The vocabulary $V$ is initialized to the set of all unique individual characters appearing in the training corpus.

> ### 📝 Formal Algorithmic Specification: BPE Learner & Segmenter
> 
> **BPE Token Learner Algorithm (Training Phase):**
> 1. Represent every word in the training corpus as a sequence of space-separated characters plus the end-of-word marker `_`. Count word frequencies.
> 2. **Iterative Merge Loop:** Repeat for $k$ merge iterations:
>    * Count co-occurrence frequencies of all adjacent symbol pairs $(c_i, c_j)$ across the corpus vocabulary.
>    * Identify the most frequent pair:
>      $$(A, B) = \arg\max_{(c_i, c_j)} \text{Count}(c_i, c_j)$$
>    * Add new token $AB$ to vocabulary $V$, and record $(A, B) \rightarrow AB$ in the ordered merge list.
>    * Replace all adjacent occurrences of $A$ and $B$ in the corpus representation with the merged token $AB$.
> 
> **BPE Token Segmenter Algorithm (Inference Phase):**
> Given an unseen test string:
> 1. Tokenize into space-separated characters with trailing `_` on each word.
> 2. Apply each learned merge rule $(A, B) \rightarrow AB$ **greedily in the exact sequential order** in which they were learned during training.
> 3. *Note:* Test data frequencies play **zero role** during inference; only the learned rule priority matters.

### 5.1 Complete Step-by-Step Walkthrough: BPE Learner Trace (Slide Corpus)
* **Raw Corpus:** `5 low, 2 lowest, 6 newer, 3 wider, 2 new`
* **Initial Corpus Representation:**
  `5 l o w _` $\vert$ `2 l o w e s t _` $\vert$ `6 n e w e r _` $\vert$ `3 w i d e r _` $\vert$ `2 n e w _`
* **Initial Vocabulary:** `{"d", "e", "i", "l", "n", "o", "r", "s", "t", "w", "_"}`

| Iteration | Merged Pair | Pair Count | Updated Corpus Tokens & State |
| :---: | :---: | :---: | :--- |
| **1** | `(e, r)` $\rightarrow$ `er` | $6 + 3 = 9$ | `... 6 n e w er _` $\quad$ `3 w i d er _` $\Longrightarrow$ New token `er` added to $V$. |
| **2** | `(er, _)` $\rightarrow$ `er_` | $6 + 3 = 9$ | `... 6 n e w er_` $\quad$ `3 w i d er_` $\Longrightarrow$ New token `er_` added to $V$. |
| **3** | `(n, e)` $\rightarrow$ `ne` | $6 + 2 = 8$ | `... 6 ne w er_` $\quad$ `2 ne w _` $\Longrightarrow$ New token `ne` added to $V$. |
| **4** | `(ne, w)` $\rightarrow$ `new` | $6 + 2 = 8$ | `... 6 new er_` $\quad$ `2 new _` $\Longrightarrow$ New token `new` added to $V$. |
| **5** | `(l, o)` $\rightarrow$ `lo` | $5 + 2 = 7$ | `5 lo w _` $\quad$ `2 lo w e s t _` $\Longrightarrow$ New token `lo` added to $V$. |
| **6** | `(lo, w)` $\rightarrow$ `low` | $5 + 2 = 7$ | `5 low _` $\quad$ `2 low e s t _` $\Longrightarrow$ New token `low` added to $V$. |

**Segmenter Execution on Unseen Test Strings:**
* **Input 1:** `n e w e r _` $\longrightarrow$ Merges apply sequentially: `er` $\rightarrow$ `er_` $\rightarrow$ `ne` $\rightarrow$ `new` $\rightarrow$ $\checkmark$ **Single Token:** `newer_`.
* **Input 2 (Novel Word):** `l o w e r _` $\longrightarrow$ Merges apply: `er_` and `low`. `low` and `er_` were never merged $\rightarrow$ $\checkmark$ **Two Subwords:** `[low, er_]`.

---

## 6. Core Linguistic Properties of BPE Tokens

* **Morpheme Induction Without Supervision:** High-frequency merged subwords naturally correspond to linguistic **morphemes** (the minimal meaning-bearing units of language), such as grammatical suffixes (`-er`, `-est`) and common roots. E.g., *"unlikeliest"* is segmented into three intuitive morphemes: `un-`, `likely`, `-est`.
* **Complete Elimination of OOV Words:** Any rare or out-of-vocabulary word is cleanly broken down into known subwords or individual characters. The model never encounters an unknown token symbol `<UNK>`.

---

## 7. Word Normalization: Case Folding

Word normalization maps diverse surface forms into a unified representation to eliminate spurious lexical sparsity:
* **Case Folding (Lowercasing):** Converting all alphabetic characters to lowercase. Essential in Information Retrieval (IR) and search engines where user queries are predominantly lowercase.
* **When Case Folding is Harmful:** Lowercasing must be avoided in Sentiment Analysis, Machine Translation, Information Extraction, and Named Entity Recognition (NER) where capitalization conveys vital semantic distinctions:
  * **Named Entity vs. Common Pronoun:** *"US"* (United States) vs. *"us"* (pronoun). Lowercasing destroys entity detection.
  * **Proper Noun vs. Verb:** *"Fed"* (Federal Reserve Bank) vs. *"fed"* (past tense of feed).
  * **Acronym vs. Noun:** *"SAIL"* (Stanford AI Lab) vs. *"sail"* (nautical cloth).

---

## 8. Lemmatization & Morphological Parsing

Lemmatization represents each word token as its **lemma**: its shared root and canonical dictionary headword form.

* **Lemma Definition:** The canonical base form shared by inflected variants:
  * *"am, are, is"* $\longrightarrow$ `be`
  * *"car, cars, car's, cars'"* $\longrightarrow$ `car`
  * Spanish *"quiero, quieres"* $\longrightarrow$ `querer`
* **Morphological Parsing:** The structural decomposition of words into morphemes:
  * **Stem:** The central, meaning-bearing lexical core.
  * **Affixes:** Bound morphemes (prefixes, suffixes, infixes) that attach to stems to encode grammatical functions (tense, number, person, case).
* **Contextual Disambiguation:** Full morphological parsers determine the part of speech (POS) before reducing forms: *"saw"* $\rightarrow$ `see` (if verb) vs. `saw` (if noun).

> ### 🔍 Standout Morphological Parsing Demonstrations
> * **English Lemmatization:** `"He is reading detective stories"` $\longrightarrow$ `He be read detective story`.
> * **Morpheme Feature Extraction:** `"cats"` $\longrightarrow$ Stem: `cat` + Affix: `-s` (*Number=Plural*).
> * **Inflected Verb Parsing (Spanish):** `"amaren"` $\longrightarrow$ Stem: `amar` ('to love') + Features: `3PL` + `Future Subjunctive`.
> * **Complex Agglutinative Morphology (Turkish):** *Uygarlastiramadiklarimizdanmissinizcasina* ('as if you are among those whom we could not civilize') decomposes into 10 distinct morphemes:
>   `Uygar` (civilized) + `las` (become) + `tir` (cause) + `ama` (not able) + `dik` (past) + `lar` (plural) + `imiz` (1pl possessive) + `dan` (ablative) + `mis` (past) + `siniz` (2pl) + `casina` (as if).

---

## 9. Stemming & The Porter Stemmer Algorithm

Stemming is a crude, heuristic process that chops off affixes to reduce tokens to a base stem, without dictionary lookups or morphological feature analysis. Stems are **not guaranteed** to be valid dictionary words.

| Dimension | Lemmatization | Stemming (Porter Stemmer) |
| :--- | :--- | :--- |
| **Theoretical Basis** | Full morphological analysis with dictionary headwords. | Heuristic, rule-based suffix chopping. |
| **Output Validity** | Always produces a valid dictionary headword (`be`, `goose`). | Often produces non-words (*"accur"*, *"copi"*, *"singl"*). |
| **Part-of-Speech Sensitivity** | Context-aware (differentiates noun vs. verb forms). | Blind to context and POS categories. |
| **Computational Cost** | Slower; requires large lexical databases (e.g., WordNet). | Extremely fast; simple cascade of string rewrite rules. |

> ### 📝 The Porter Stemmer: Cascaded Rewrite Rules (Porter, 1980)
> The Porter Stemmer applies a cascade of sequential rewrite rules organized into 5 successive phases. The output of each phase forms the direct input to the next phase:
> 
> | Phase / Step | Rewrite Rule Syntax | Prominent Example & Transformation |
> | :--- | :--- | :--- |
> | **Step 1a** | `sses` $\longrightarrow$ `ss`<br>`ies` $\longrightarrow$ `i`<br>`ss` $\longrightarrow$ `ss`<br>`s` $\longrightarrow$ $\emptyset$ | *"caresses"* $\longrightarrow$ `caress`<br>*"ponies"* $\longrightarrow$ `poni`; *"ties"* $\longrightarrow$ `ti`<br>*"caress"* $\longrightarrow$ `caress` (preserved intact)<br>*"cats"* $\longrightarrow$ `cat` |
> | **Step 1b** | `(*v*)ing` $\longrightarrow$ $\emptyset$<br>`(*v*)ed` $\longrightarrow$ $\emptyset$ | If stem contains a vowel: *"motoring"* $\longrightarrow$ `motor`.<br>But *"sing"* remains `sing` (no prior vowel in stem).<br>*"plastered"* $\longrightarrow$ `plaster` |
> | **Step 2 & 3** | `ational` $\longrightarrow$ `ate`<br>`tional` $\longrightarrow$ `tion` | *"relational"* $\longrightarrow$ `relate`<br>*"conditional"* $\longrightarrow$ `condition` |

---

## 10. Stemming Failure Modes: Over-Stemming vs. Under-Stemming

* **Over-Stemming (False Positive Conflation):** Unrelated words are collapsed to the same stem:
  * $\checkmark$ *"organization"* and *"organ"* are both reduced to `organ`, conflating biological and institutional meanings.
* **Under-Stemming (False Negative Separation):** Words that share a morphological root fail to collapse:
  * $\checkmark$ *"European"* $\rightarrow$ `european` while *"Europe"* $\rightarrow$ `europ`.

---

## 11. Sentence Segmentation (Sentence Boundary Detection)

Dividing running text into discrete sentences is complicated by the severe polysemy of punctuation:
* **Punctuation Ambiguity:** While `!` and `?` are relatively unambiguous sentence terminators, the period `.` serves three distinct linguistic roles:
  1. Sentence boundary delimiter
  2. Abbreviation marker (*Dr.*, *Inc.*, *m.p.h.*)
  3. Numerical decimal point (*4.3*, *.02%*)
* **Standard Architecture:** Tokenize first, then classify each period using rule-based abbreviation dictionaries or supervised binary classifiers (decision trees, logistic regression) to assign a boundary probability $P(\text{boundary} \mid \text{period})$.

---

## 12. Minimum Edit Distance: Mathematical Formulation

The **Minimum Edit Distance** between two strings $X$ (length $n$) and $Y$ (length $m$) is the minimum number of editing operations (Insertions, Deletions, Substitutions) required to transform $X$ into $Y$.

* **Core NLP Applications:** Spelling correction, speech recognition Word Error Rate (WER), machine translation evaluation (Translation Edit Rate / TER), biological sequence alignment (DNA/protein nucleotides), and named entity coreference.
* **Cost Models:**
  * **Levenshtein Distance (1966):** $c_{\text{ins}} = 1$, $c_{\text{del}} = 1$, $c_{\text{sub}} = 2$ if $X_i \ne Y_j$ ($0$ if $X_i = Y_j$). (A substitution is 1 deletion + 1 insertion).
  * **Unit Cost (Needleman-Wunsch):** $c_{\text{ins}} = 1$, $c_{\text{del}} = 1$, $c_{\text{sub}} = 1$ if $X_i \ne Y_j$ ($0$ if $X_i = Y_j$).

> ### 📝 Dynamic Programming Recurrence for Minimum Edit Distance
> Let $D(i, j)$ denote the minimum edit distance between prefixes $X[1..i]$ and $Y[1..j]$.
> 
> **Initialization (Base Cases):**
> $$D(i, 0) = i \quad (1 \le i \le n), \qquad D(0, j) = j \quad (1 \le j \le m), \qquad D(0, 0) = 0$$
> 
> **Recurrence Relation:**
> $$D(i, j) = \min \begin{cases}
> D(i-1, j) + 1 & \text{\textbf{Deletion} from } X \quad (\text{pointer: DOWN } \downarrow) \\
> D(i, j-1) + 1 & \text{\textbf{Insertion} into } X \quad (\text{pointer: LEFT } \leftarrow) \\
> D(i-1, j-1) + \begin{cases} 2 & \text{if } X_i \ne Y_j \\ 0 & \text{if } X_i = Y_j \end{cases} & \text{\textbf{Substitution / Match}} \quad (\text{pointer: DIAG } \swarrow)
> </cases}$$
> 
> **Termination:** The top-right entry $D(n, m)$ (in bottom-up coordinate layout) contains the exact minimum edit distance.

---

## 13. Full DP Matrix Walkthrough: `INTENTION` $\longrightarrow$ `EXECUTION`

Transforming source $X = \text{INTENTION}$ ($n=9$) into target $Y = \text{EXECUTION}$ ($m=9$) under Levenshtein costs ($c_{\text{sub}}=2$):

| $D(i,j)$ | **#** | **E** | **X** | **E** | **C** | **U** | **T** | **I** | **O** | **N** |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **N** | 9 | ↓ 8 | ↙←↓ 9 | ↙←↓ 10 | ↙←↓ 11 | ↙←↓ 12 | ↓ 11 | ↓ 10 | ↓ 9 | **↙ 8** 🟩 |
| **O** | 8 | ↓ 7 | ↙←↓ 8 | ↙←↓ 9 | ↙←↓ 10 | ↙←↓ 11 | ↓ 10 | ↓ 9 | **↙ 8** 🟩 | ← 9 |
| **I** | 7 | ↓ 6 | ↙←↓ 7 | ↙←↓ 8 | ↙←↓ 9 | ↙←↓ 10 | ↓ 9 | **↙ 8** 🟩 | ← 9 | ← 10 |
| **T** | 6 | ↓ 5 | ↙←↓ 6 | ↙←↓ 7 | ↙←↓ 8 | ↙←↓ 9 | **↙ 8** 🟩 | ← 9 | ← 10 | ←↓ 11 |
| **N** | 5 | ↓ 4 | ↙←↓ 5 | ↙←↓ 6 | ↙←↓ 7 | **↙←↓ 8** 🟩 | ↙←↓ 9 | ↙←↓ 10 | ↙←↓ 11 | ↙↓ 10 |
| **E** | 4 | ↙ 3 | ← 4 | **↙← 5** 🟩 | **← 6** 🟩 | ← 7 | ←↓ 8 | ↙←↓ 9 | ↙←↓ 10 | ↓ 9 |
| **T** | 3 | ↙←↓ 4 | **↙← 5** 🟩 | ↙←↓ 6 | ↙←↓ 7 | ↙←↓ 8 | ↙ 7 | ←↓ 8 | ↙←↓ 9 | ↓ 8 |
| **N** | 2 | **↙←↓ 3** 🟩 | ↙←↓ 4 | ↙←↓ 5 | ↙←↓ 6 | ↙←↓ 7 | ↙←↓ 8 | ↓ 7 | ↙←↓ 8 | ↙ 7 |
| **I** | **1** 🟩 | ↙←↓ 2 | ↙←↓ 3 | ↙←↓ 4 | ↙←↓ 5 | ↙←↓ 6 | ↙←↓ 7 | ↙ 6 | ← 7 | ← 8 |
| **#** | **0** 🟩 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 |
| | **#** | **E** | **X** | **E** | **C** | **U** | **T** | **I** | **O** | **N** |

* **Backtrace Legend:**
  * **Bold / 🟩 Highlighted Cells:** Optimal backtrace trajectory from top-right $D(9,9)=8$ to bottom-left $D(0,0)=0$.
  * **Pointers:** $\swarrow$ = Substitution/Match ($D(i-1,j-1)$), $\leftarrow$ = Insertion ($D(i,j-1)$), $\downarrow$ = Deletion ($D(i-1,j)$).

> ### 🔍 Backtrace Alignment & Edit Sequence Derivation
> Starting at $D(9,9)=8$ and following backtrace pointers to $D(0,0)=0$ yields the optimal character alignment:
> 
> ```
> Source X:    I    N    T    E    --    N    T    I    O    N
> Target Y:   --    E    X    E     C    U    T    I    O    N
> -------------------------------------------------------------
> Operation:  del  sub  sub match  ins  sub match match match match
> Lev Cost:    1    2    2    0     1    2    0     0     0     0
> ```
> 
> * **Summary Cost:** $\text{Levenshtein Distance} = 1 + 2 + 2 + 0 + 1 + 2 + 0 + 0 + 0 + 0 = \mathbf{8}$.  
>   *(Under unit substitution cost, Distance $= \mathbf{5}$)*.

---

## 14. Computational Complexity & Weighted Edit Distance

### 14.1 Asymptotic Complexity
* **Time Complexity:** $\mathcal{O}(n \times m)$ --- every cell in the $n \times m$ table takes constant $\mathcal{O}(1)$ operations.
* **Space Complexity:** $\mathcal{O}(n \times m)$ to store the table and backtrace pointers ($\mathcal{O}(\min(n, m))$ if only distance is needed).
* **Backtrace Time:** $\mathcal{O}(n + m)$ path length from $(n, m)$ to $(0, 0)$.

### 14.2 Weighted Minimum Edit Distance (Non-Uniform Operation Costs)
In practical NLP, edit operations are not equally probable. In spell correction, adjacent keyboard letters (e.g., mistyping `'e'` for `'r'`) are far more common than distant keys. In biology, specific nucleotide transitions/transversions have distinct mutation rates:

$$D(i, j) = \min \begin{cases}
D(i-1, j) + \text{del}[X_i] \\
D(i, j-1) + \text{ins}[Y_j] \\
D(i-1, j-1) + \text{sub}[X_i, Y_j]
\end{cases}
\qquad
\begin{aligned}
& \text{Base Cases:} \\
& D(i, 0) = D(i-1, 0) + \text{del}[X_i] \\
& D(0, j) = D(0, j-1) + \text{ins}[Y_j]
\end{aligned}$$

Cost values $\text{del}$, $\text{ins}$, and $\text{sub}$ are derived empirically from confusion matrices of typing or phonetic error probabilities.

---
*Summary compiled for Natural Language Processing (ENSIA 2026–2027) based on Lecture 2 materials.*
