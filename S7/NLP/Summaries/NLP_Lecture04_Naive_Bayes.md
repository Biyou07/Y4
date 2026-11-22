# NLP Lecture 4: Naïve Bayes, Text Classification & Sentiment Analysis
**Comprehensive Course Summary (ENSIA S7 2026–2027)**  
*Instructor: Prof. Ahmed Guessoum*

---

> ### 📌 Lecture Scope & Core Foundations
> Text classification assigns predefined categorical labels $c \in \mathcal{C}$ to unstructured natural language documents $d \in \mathcal{D}$. This summary covers the mathematical foundations of the **Multinomial Naïve Bayes** classifier, the Maximum A Posteriori (MAP) decision rule, log-space linear reformulations, parameter estimation via Maximum Likelihood Estimation (MLE) with Laplace smoothing, the Out-of-Vocabulary (OOV) discard rule, and a fully worked movie review exam trace. It further details sentiment-specific engineering: **Binary Multinomial Naïve Bayes**, **negation marking** (`NOT_` prefixing from Lab 4), sentiment lexicons, and the theoretical duality between Naïve Bayes and class-conditional unigram language models. Finally, it presents rigorous evaluation methodology: the $2 \times 2$ confusion matrix, accuracy pathologies under severe class imbalance, precision, recall, mathematical derivation and proof of the $F_1$ harmonic mean, and macro- vs. micro-averaging.

---

## 1. Text Categorization: Task Definition & Formal Setup

### 1.1 Mathematical Definition
* **Input:** A document $d \in \mathcal{D}$ represented as an ordered sequence of tokens $(w_1, w_2, \dots, w_n)$.
* **Fixed Output Space:** A discrete, predefined inventory of $K$ classes:
  $$\mathcal{C} = \{c_1, c_2, \dots, c_K\}$$
* **Objective:** Learn a mapping function $f: \mathcal{D} \to \mathcal{C}$ that assigns the most probable class $\hat{c}$ to document $d$.

### 1.2 Core NLP Classification Tasks
* **Sentiment Analysis:** Classifying subjective orientation $\mathcal{C} = \{\text{Positive}, \text{Negative}, \text{Neutral}\}$ in movie reviews, product feedback, or social media.
* **Spam Detection:** Binary filtering $\mathcal{C} = \{\text{Spam}, \text{Ham}\}$ based on linguistic markers and message payloads.
* **Topic Classification:** Routing articles or support tickets into predefined domains $\mathcal{C} = \{\text{Finance}, \text{Sports}, \text{Politics}, \text{Tech}\}$.
* **Authorship Attribution & Forensic Linguistics:** Determining author identity or gender based on stylistic unigram and function word distributions.
* **Language Identification (LID):** Classifying the natural language of incoming text across hundreds of linguistic classes.

---

## 2. Bayesian Foundations & The MAP Decision Rule

By Bayes' Rule, the posterior probability of class $c$ given document $d$ is:

$$P(c \mid d) = \frac{P(d \mid c) \, P(c)}{P(d)}$$

Where:
* $P(c)$ is the **Prior Probability** of class $c$ (the baseline prevalence of class $c$ before observing evidence).
* $P(d \mid c)$ is the **Likelihood** of observing document $d$ given that the true class is $c$.
* $P(d)$ is the **Marginal Probability of Evidence**:
  $$P(d) = \sum_{c' \in \mathcal{C}} P(d \mid c') \, P(c')$$
* $P(c \mid d)$ is the **Posterior Probability** of class $c$ given document $d$.

### The Maximum A Posteriori (MAP) Decision Rule
Under 0-1 loss (minimizing misclassification rate), the optimal decision rule chooses the class with maximal posterior probability:

$$\hat{c}_{\text{MAP}} = \arg\max_{c \in \mathcal{C}} P(c \mid d) = \arg\max_{c \in \mathcal{C}} \frac{P(d \mid c) \, P(c)}{P(d)}$$

Because the marginal probability $P(d)$ is independent of $c$ and strictly constant across all candidate classes for a given document, it acts purely as a normalizing scalar. We discard $P(d)$ during inference:

$$\hat{c}_{\text{MAP}} = \arg\max_{c \in \mathcal{C}} P(d \mid c) \, P(c)$$

---

## 3. The Two Core Independence Assumptions of Naïve Bayes

Document $d$ is a joint sequence of $n$ words $(w_1, w_2, \dots, w_n)$. Modeling the full likelihood $P(w_1, w_2, \dots, w_n \mid c)$ directly requires estimating $|V|^n$ parameters, which is mathematically intractable and leads to catastrophic data sparsity.

Naïve Bayes makes **two simplifying independence assumptions**:

### Assumption 1: Bag-of-Words (Position Invariance)
* Word order, syntax, and sentence structure are completely ignored.
* Only token frequencies matter.
* A document is treated as an unordered multiset (bag) of words:
  $$\text{Likelihood depends solely on identity and counts, not sequential positions.}$$

### Assumption 2: Conditional Feature Independence
* Given the document class $c$, the occurrence of word $w_i$ is statistically independent of all other words $w_j$ ($i \neq j$):
  $$P(w_1, w_2, \dots, w_n \mid c) = \prod_{i=1}^n P(w_i \mid c)$$

### The Complete Naïve Bayes Classifier
Combining the MAP rule with both assumptions yields the operational classification formula:

$$\hat{c}_{\text{NB}} = \arg\max_{c \in \mathcal{C}} P(c) \prod_{i=1}^n P(w_i \mid c)$$

> **Why Naïve?** In real human language, words are strongly correlated (e.g., observing *"San"* exponentially increases the likelihood of *"Francisco"*; *"prime"* strongly predicts *"minister"* or *"number"*). Naïve Bayes violates true linguistic reality, yet works exceptionally well in practice because classification only requires picking the maximum argmax, not calibrating exact probabilities.

---

## 4. Multinomial Naïve Bayes in Log Space: Linear Classifier Equivalence

Multiplying hundreds of small fractional probabilities $P(w_i \mid c) \ll 1$ leads to catastrophic floating-point arithmetic underflow on modern computers.

Because the natural logarithm $\ln(x)$ is a strictly monotonically increasing function ($x_1 > x_2 \iff \ln x_1 > \ln x_2$), taking logarithms preserves the exact argmax order while converting products into numerical additions:

$$\hat{c}_{\text{NB}} = \arg\max_{c \in \mathcal{C}} \left[ \log P(c) + \sum_{i=1}^n \log P(w_i \mid c) \right]$$

### Equivalence to a Linear Classifier
Grouping by unique vocabulary types $w_k \in V$ rather than running tokens:

$$\log P(c \mid d) \propto \log P(c) + \sum_{k=1}^{|V|} f_k \log P(w_k \mid c)$$

Where:
* $f_k$ is the frequency count of word $w_k$ in document $d$ (the input feature vector $\mathbf{x}$).
* $\log P(w_k \mid c)$ acts as the weight parameter $w_{k,c}$.
* $\log P(c)$ acts as the bias term $b_c$.

This directly matches the generalized linear classification model:

$$\hat{c} = \arg\max_{c \in \mathcal{C}} \left( \mathbf{w}_c^T \mathbf{x} + b_c \right)$$

---

## 5. Maximum Likelihood Parameter Estimation (MLE)

Parameters are estimated directly from training corpus frequencies.

### Prior Probability Estimation
The prior probability of class $c$ is the relative fraction of training documents belonging to class $c$:

$$\hat{P}(c) = \frac{N_c}{N_{\text{total}}}$$

Where $N_c$ is the number of documents with label $c$, and $N_{\text{total}} = \sum_{c' \in \mathcal{C}} N_{c'}$ is the total training document count.

### Class Mega-Document Construction
For each class $c$, concatenate all training documents labeled with $c$ into a single composite text: the **class mega-document** $\text{Text}_c$.

### Raw MLE Word Likelihood Estimation
$$\hat{P}_{\text{MLE}}(w_i \mid c) = \frac{\text{count}(w_i, c)}{\sum_{w \in V} \text{count}(w, c)} = \frac{\text{count}(w_i, c)}{N_c}$$

Where:
* $\text{count}(w_i, c)$ is the raw frequency of word $w_i$ in $\text{Text}_c$.
* $N_c = \sum_{w \in V} \text{count}(w, c)$ is the total token length of $\text{Text}_c$.
* $V$ is the union vocabulary across **all** classes.

---

## 6. The Zero-Probability Crisis & Laplace Smoothing

### 6.1 The Zero-Frequency Failure Mode
If a test document contains a word $w$ that never appeared in class $c$ during training, raw MLE assigns $\hat{P}_{\text{MLE}}(w \mid c) = 0$. In product form:

$$P(c) \times \hat{P}(w_1 \mid c) \times \dots \times 0 \times \dots \times \hat{P}(w_n \mid c) = 0$$

A single zero term completely annihilates all evidence provided by all other words in the document, regardless of how strongly they point to class $c$.

### 6.2 Laplace (Add-1) Smoothing
Laplace smoothing adds a pseudo-count of 1 to every word in the shared vocabulary $V$:

$$\hat{P}_{\text{Laplace}}(w_i \mid c) = \frac{\text{count}(w_i, c) + 1}{\sum_{w \in V} (\text{count}(w, c) + 1)} = \frac{\text{count}(w_i, c) + 1}{N_c + |V|}$$

Where $|V|$ is the total number of unique word types across the entire training corpus.

> **Normalization Proof:** Summing over all $w \in V$:
> $$\sum_{w \in V} \hat{P}_{\text{Laplace}}(w \mid c) = \frac{\sum_{w \in V} \text{count}(w, c) + \sum_{w \in V} 1}{N_c + |V|} = \frac{N_c + |V|}{N_c + |V|} = 1$$

### Generalized Add-$\alpha$ (Lidstone Smoothing)
For fractional smoothing parameters $0 < \alpha \le 1$:

$$\hat{P}_{\alpha}(w_i \mid c) = \frac{\text{count}(w_i, c) + \alpha}{N_c + \alpha |V|}$$

### 6.3 Out-of-Vocabulary (OOV) Discard Protocol
What happens if a test document contains a word $w \notin V$ that was never seen anywhere in the training corpus?

* **Crucial Rule:** In Naïve Bayes classification, test words not in the training vocabulary $V$ are **completely ignored and dropped** from both the numerator and denominator calculations.
* **Theoretical Justification:** An unknown token $w \notin V$ has zero occurrences in all classes. Assigning it Laplace smoothed probability would yield $\frac{1}{N_c + |V|}$ for all classes, adding no discriminatory power while penalizing classes with larger total word counts.

---

## 7. Complete Step-by-Step Worked Exam Problem

This problem traces the movie review sentiment classification example from the lecture slides.

### Training Corpus ($N_{\text{total}} = 5$ documents)
| Class | Doc ID | Document Content |
| :---: | :---: | :--- |
| **$-$** | $d_1$ | `just plain boring` |
| **$-$** | $d_2$ | `entirely predictable and lacks energy` |
| **$-$** | $d_3$ | `no surprises and very few laughs` |
| **$+$** | $d_4$ | `very powerful` |
| **$+$** | $d_5$ | `the most fun film of the summer` |

**Test Document ($d_{\text{test}}$):** `predictable with no fun`

---

### Step 1: Compute Class Prior Probabilities
Total documents $N_{\text{total}} = 5$. Negative docs $N_- = 3$, Positive docs $N_+ = 2$:

$$\hat{P}(-) = \frac{3}{5} = 0.60, \qquad \hat{P}(+) = \frac{2}{5} = 0.40$$

---

### Step 2: Extract Class Mega-Documents & Global Vocabulary
* **Negative Mega-Document ($\text{Text}_-$):**  
  `just, plain, boring, entirely, predictable, and, lacks, energy, no, surprises, and, very, few, laughs`  
  $$\implies N_- = 14 \text{ tokens}$$
* **Positive Mega-Document ($\text{Text}_+$):**  
  `very, powerful, the, most, fun, film, of, the, summer`  
  $$\implies N_+ = 9 \text{ tokens}$$
* **Global Vocabulary $V$ (Union of all unique words):**  
  $\{ \text{and, boring, entirely, energy, few, film, fun, just, lacks, laughs, most, no, of, plain, powerful, predictable, summer, surprises, the, very} \}$  
  $$\implies |V| = 20 \text{ unique types}$$

---

### Step 3: Normalize Test Document (Apply OOV Discard Rule)
* Test words: `predictable`, `with`, `no`, `fun`.
* Checking membership in $V$:
  * `predictable` $\in V$ ($\checkmark$)
  * `with` $\notin V$ ($\times \implies$ **Drop `with`**)
  * `no` $\in V$ ($\checkmark$)
  * `fun` $\in V$ ($\checkmark$)
* Evaluated test token set: `[predictable, no, fun]` ($n = 3$).

---

### Step 4: Compute Laplace-Smoothed Likelihoods
Denominators ($N_c + |V|$):
* For Negative class ($-$): $14 + 20 = 34$
* For Positive class ($+$): $9 + 20 = 29$

#### Word Likelihoods for Class ($-$)
* $\hat{P}(\text{predictable} \mid -) = \frac{\text{count}(\text{predictable}, -) + 1}{14 + 20} = \frac{1 + 1}{34} = \frac{2}{34}$
* $\hat{P}(\text{no} \mid -) = \frac{\text{count}(\text{no}, -) + 1}{14 + 20} = \frac{1 + 1}{34} = \frac{2}{34}$
* $\hat{P}(\text{fun} \mid -) = \frac{\text{count}(\text{fun}, -) + 1}{14 + 20} = \frac{0 + 1}{34} = \frac{1}{34}$

#### Word Likelihoods for Class ($+$)
* $\hat{P}(\text{predictable} \mid +) = \frac{\text{count}(\text{predictable}, +) + 1}{9 + 20} = \frac{0 + 1}{29} = \frac{1}{29}$
* $\hat{P}(\text{no} \mid +) = \frac{\text{count}(\text{no}, +) + 1}{9 + 20} = \frac{0 + 1}{29} = \frac{1}{29}$
* $\hat{P}(\text{fun} \mid +) = \frac{\text{count}(\text{fun}, +) + 1}{9 + 20} = \frac{1 + 1}{29} = \frac{2}{29}$

---

### Step 5: Score Both Classes via Posterior Product
#### Negative Score:
$$P(-) \prod_{i=1}^3 P(w_i \mid -) = \frac{3}{5} \times \left( \frac{2}{34} \times \frac{2}{34} \times \frac{1}{34} \right) = \frac{3}{5} \times \frac{4}{39{,}304} = \frac{12}{196{,}520} \approx \mathbf{6.1 \times 10^{-5}}$$

#### Positive Score:
$$P(+) \prod_{i=1}^3 P(w_i \mid +) = \frac{2}{5} \times \left( \frac{1}{29} \times \frac{1}{29} \times \frac{2}{29} \right) = \frac{2}{5} \times \frac{2}{24{,}389} = \frac{4}{121{,}945} \approx \mathbf{3.2 \times 10^{-5}}$$

### Final Classification Decision
$$\mathbf{6.1 \times 10^{-5}} > \mathbf{3.2 \times 10^{-5}} \implies \hat{c} = \mathbf{Negative\ (-)}$$

---

## 8. Binary Multinomial Naïve Bayes (Binarized NB for Sentiment)

In topic classification, repeated occurrences of a word provide cumulative evidence (an article mentioning *"tax"* 10 times is twice as topical). In **sentiment analysis**, term frequency distorts predictions: a reviewer writing *"terrible"* 5 times is not 5 times more negative than one writing it once; repeated words artificially dominate the likelihood product.

### The Within-Document Binarization Rule
Word counts are clipped to 1 **within each individual document**:
1. For each document $d_j$, remove all duplicate word tokens (retain exactly one instance of each unique word type).
2. Concatenate the binarized documents to form the class mega-document.
3. **Crucial Distinction:** In the class mega-document, word counts can still exceed 1! The count $\text{count}(w, c)$ now represents the number of individual documents in class $c$ containing word $w$.

### Worked Binarization Example
| Document | Raw Document Content | Binarized Document Content |
| :---: | :--- | :--- |
| Doc 1 ($-$) | `bad bad bad awful movie` | `bad awful movie` |
| Doc 2 ($-$) | `awful plot bad acting` | `awful plot bad acting` |

* **Class Mega-Document Counts:**
  * Raw Count of `bad`: $3 + 1 = 4$
  * Binarized Count of `bad`: $1 + 1 = 2$ (appeared in 2 documents)
  * Likelihood calculation uses binarized counts with standard Laplace smoothing:
    $$\hat{P}_{\text{binary}}(w \mid c) = \frac{\text{count}_{\text{binarized}}(w, c) + 1}{N_{c,\text{binarized}} + |V|}$$

---

## 9. Negation Handling in Sentiment Analysis (Lab 4 Implementation)

A major flaw of the standard Bag-of-Words model is the complete inversion of polarity caused by negation:
* *"I didn't like this movie, it was not good"* $\longrightarrow$ Naïve Bayes sees positive tokens `like` and `good`, incorrectly classifying the sentence as positive!

### The Das et al. (2001) / Potts (2011) Prefix Transformation
1. Identify a negation trigger word:
   $$\text{Triggers} \in \{\text{not},\ \text{n't},\ \text{no},\ \text{never},\ \text{cannot},\ \text{hardly},\ \text{barely}\}$$
2. Append a `NOT_` prefix to every subsequent word until the next punctuation mark:
   $$\text{Punctuation Delimiters} \in \{\text{'.'}, \text{','}, \text{'!'}, \text{'?'}, \text{';'}\}$$

### Concrete Transformation Example
* **Raw Input:** `"I did not like this movie, it was good."`
* **Transformed Tokens:** `["I", "did", "not", "NOT_like", "NOT_this", "NOT_movie", ",", "it", "was", "good", "."]`
* **Effect:** `NOT_like` becomes an entirely distinct vocabulary feature from `like`. The model learns that `NOT_like` has a high likelihood in the negative class, while `good` retains its positive orientation.

---

## 10. Sentiment Lexicons & Polarity Features

When training data is scarce or completely unavailable (cold start), rule-based and lexicon-based models classify sentiment using expert-curated polarity dictionaries.

### Prominent Sentiment Lexicons
* **LIWC (Linguistic Inquiry and Word Count):** Psychologically validated categories (positive emotion, negative emotion, cognitive processes).
* **General Inquirer (GI):** Comprehensive lexical resource categorizing words into positive/negative valence markers.
* **VADER (Valence Aware Dictionary and sEntiment Reasoner):** Rule-based model incorporating intensity modifiers (capitalization, exclamation marks, degree adverbs like *"extremely"* vs. *"slightly"*).

### Prior Polarity vs. Contextual Polarity
* **Prior Polarity:** Out-of-context baseline orientation (e.g., *"terrific"* is positive, *"horrible"* is negative).
* **Contextual Polarity:** Orientation dictated by syntax, domain, and pragmatics:
  * *"This vacuum really sucks."* $\implies$ Literal physical performance ($\checkmark$ Positive)
  * *"This movie really sucks."* $\implies$ Figurative evaluation ($\times$ Negative)
  * *"The vaccine unpredictable adverse event."* $\implies$ Negative medical risk

---

## 11. Generative Modeling & Language Model Equivalence

Naïve Bayes is a **Generative Classifier**:
* It models the joint distribution $P(d, c) = P(c) \, P(d \mid c)$ by learning how each class generates textual data.
* In contrast, discriminative classifiers (such as Logistic Regression or SVMs) model the posterior boundary $P(c \mid d)$ directly.

### Equivalence to Class Unigram Language Models
The class-conditional likelihood $\prod_{i=1}^n P(w_i \mid c)$ is mathematically identical to a **unigram language model** trained exclusively on documents of class $c$:
$$\text{Naïve Bayes} \equiv |\mathcal{C}| \text{ distinct Unigram Language Models competing under prior weights } P(c)$$

---

## 12. The $2 \times 2$ Contingency Table (Confusion Matrix)

Evaluating a binary classifier against ground truth human annotations (Gold Standard labels):

| Classification Contingency Matrix | **Gold Positive ($c = +1$)** | **Gold Negative ($c = -1$)** |
| :--- | :---: | :---: |
| **System Predicted Positive** | **True Positive (TP)** | **False Positive (FP)** (Type I Error) |
| **System Predicted Negative** | **False Negative (FN)** (Type II Error) | **True Negative (TN)** |

---

## 13. Mathematical Definitions: Accuracy, Precision, Recall & $F_1$

### 13.1 Accuracy
$$\text{Accuracy} = \frac{TP + TN}{TP + FP + FN + TN}$$

#### The Accuracy Pathology in Imbalanced Datasets
Suppose an email corpus contains 990 ham emails and 10 spam emails ($99\%$ negative class). A trivial "dummy" classifier that predicts "Ham" for every email achieves:

$$\text{Accuracy} = \frac{0 + 990}{0 + 0 + 10 + 990} = \frac{990}{1000} = \mathbf{99.0\%}$$

Despite an impressive $99\%$ accuracy, the classifier detected **zero spam emails** ($0\%$ spam recall)! Accuracy is dangerously misleading under class imbalance.

---

### 13.2 Precision ($P$)
The fraction of retrieved/predicted positive instances that are actually positive (measure of **exactness**):

$$P = \frac{TP}{TP + FP}$$

* High Precision $\implies$ Low False Positive rate (when the system flags an email as spam, it is almost certainly spam).

---

### 13.3 Recall ($R$)
The fraction of actual gold positive instances correctly identified by the system (measure of **completeness / sensitivity**):

$$R = \frac{TP}{TP + FN}$$

* High Recall $\implies$ Low False Negative rate (the system catches almost all spam, letting very few slip through).

---

### 13.4 The $F_1$-Measure: Harmonic Mean Derivation & Proof

The $F_1$-measure balances Precision and Recall into a single holistic metric via their **Harmonic Mean**:

$$F_1 = \frac{2}{\frac{1}{P} + \frac{1}{R}} = \frac{2PR}{P + R} = \frac{2 \cdot TP}{2 \cdot TP + FP + FN}$$

#### Mathematical Proof: Why Harmonic Mean Beats Arithmetic Mean
Consider an imbalanced test set with 1,000 documents (10 positive, 990 negative). A degenerate model predicts "Positive" for all 1,000 documents:
* $TP = 10, \quad FP = 990, \quad FN = 0, \quad TN = 0$
* $R = \frac{10}{10 + 0} = 1.00 \quad (100\%)$
* $P = \frac{10}{10 + 990} = \frac{10}{1000} = 0.01 \quad (1\%)$

Evaluating both means:
1. **Arithmetic Mean:**
   $$\frac{P + R}{2} = \frac{0.01 + 1.00}{2} = \mathbf{0.505 \quad (50.5\%)}$$
   Misleadingly awards a passing $50\%$ score to a completely broken, degenerate classifier!
2. **Harmonic Mean ($F_1$):**
   $$F_1 = \frac{2 \times 1.0 \times 0.01}{1.0 + 0.01} = \frac{0.02}{1.01} \approx \mathbf{0.0198 \quad (1.98\%)}$$
   Correctly penalizes the extreme imbalance and reflects near-zero practical utility.

> **Takeaway:** The harmonic mean is mathematically dominated by the smaller term:
> $$\lim_{P \to 0} F_1(P, R) = 0 \quad (\text{even if } R = 1.0)$$

---

## 14. Multi-Class Aggregation: Macro-Averaging vs. Micro-Averaging

When evaluating across $|\mathcal{C}| > 2$ classes, performance across individual classes is aggregated using two distinct regimes:

| Aggregation Method | Mathematical Definition & Formula | Operational Behavior & Class Sensitivity |
| :--- | :--- | :--- |
| **Macro-Averaging** | Computes the metric for each class $c_j$ independently, then takes their unweighted arithmetic mean:<br>$$\text{Macro-}F_1 = \frac{1}{|\mathcal{C}|} \sum_{j=1}^{|\mathcal{C}|} F_1(c_j)$$ | **Unweighted per class:** Treats every class equally regardless of frequency. Highly sensitive to performance on rare classes (a class with 5 examples carries the same weight as a class with 50,000 examples). |
| **Micro-Averaging** | Pools all individual counts $(TP_j, FP_j, FN_j)$ globally across all classes, then computes the metric:<br>$$\text{Micro-}F_1 = \frac{2 \sum TP_j}{2 \sum TP_j + \sum FP_j + \sum FN_j}$$ | **Frequency-weighted per instance:** Every test instance contributes equally. Dominated by large, frequent classes; masks poor performance on rare minority classes. |

---

## 15. Summary Comparison of Text Classification Architectures

| Model Architecture | Input Representation | Core Engineering Mechanism | Optimal NLP Use Case |
| :--- | :--- | :--- | :--- |
| **Multinomial Naïve Bayes** | Raw term frequencies $f_k$ | Likelihood normalized by total token count $N_c + \|V\|$. | Topic categorization, language identification, author attribution. |
| **Binary Multinomial Naïve Bayes** | Clipped frequencies $x_k \in \{0, 1\}$ | Within-doc binarization; eliminates frequency distortion. | Sentiment analysis, subjective review rating. |
| **Negation-Augmented Naïve Bayes** | Transformed tokens with `NOT_` prefix | Prefixes words between negation markers and punctuation delimiters. | Reversing polarity in sentiment and stance detection. |
| **Lexicon-Based Models (VADER/LIWC)** | Pre-compiled sentiment dictionaries | Counts pre-annotated positive and negative polarity cues. | Cold start with zero labeled training data, real-time social streams. |

---

## 16. Key Exam Formulas Quick Reference

1. **MAP Rule:** $\hat{c} = \arg\max_{c \in \mathcal{C}} P(c) \prod_{i=1}^n P(w_i \mid c)$
2. **Log-Space Form:** $\hat{c} = \arg\max_{c \in \mathcal{C}} \left[ \log P(c) + \sum_{i=1}^n \log P(w_i \mid c) \right]$
3. **Prior Probability:** $\hat{P}(c) = \frac{N_c}{N_{\text{total}}}$
4. **Laplace Likelihood:** $\hat{P}(w_i \mid c) = \frac{\text{count}(w_i, c) + 1}{N_c + |V|}$
5. **Add-$\alpha$ Likelihood:** $\hat{P}(w_i \mid c) = \frac{\text{count}(w_i, c) + \alpha}{N_c + \alpha |V|}$
6. **OOV Rule:** If $w \notin V$, **drop** $w$ entirely from test evaluation.
7. **Accuracy:** $\frac{TP + TN}{TP + FP + FN + TN}$
8. **Precision:** $\frac{TP}{TP + FP}$
9. **Recall:** $\frac{TP}{TP + FN}$
10. **$F_1$-Measure:** $\frac{2PR}{P+R} = \frac{2TP}{2TP + FP + FN}$
11. **Macro-$F_1$:** $\frac{1}{|\mathcal{C}|} \sum_{j=1}^{|\mathcal{C}|} F_1(c_j)$
12. **Micro-$F_1$:** $\frac{2 \sum TP_j}{2 \sum TP_j + \sum FP_j + \sum FN_j}$
