# NLP Lecture 3: Language Modeling & N-grams
**Comprehensive Course Summary (ENSIA S7 2026–2027)**  
*Instructor: Prof. Ahmed Guessoum*

---

> ### 📌 Lecture Scope & Core Foundations
> A **Language Model (LM)** assigns probabilities to sequences of words $P(W) = P(w_1, w_2, \dots, w_n)$ or predicts the conditional distribution of upcoming words $P(w_n \mid w_1, \dots, w_{n-1})$. Probabilistic LMs form the computational core of automatic speech recognition, machine translation, predictive typing, and natural language generation. This summary details the Chain Rule of probability, the Markov assumption and $N$-gram hierarchies, extrinsic vs. intrinsic evaluation, dataset partitioning (train/dev/test) and data leakage prevention, mathematical formulation of Perplexity as an effective branching factor, zero-probability handling, smoothing techniques (Laplace, Add-$k$, Linear Interpolation with EM derivation from Lab 3, Stupid Backoff), and open vs. closed vocabulary management for Out-Of-Vocabulary (OOV) tokens.

---

## 1. Definition & Core Applications of Language Models

A probabilistic language model computes either:
1. **The joint probability of an entire sentence:**
   $$P(W) = P(w_1, w_2, \dots, w_n)$$
2. **The conditional probability of an upcoming word given historical context:**
   $$P(w_n \mid w_1, w_2, \dots, w_{n-1})$$

### Core NLP Applications
* **Automatic Speech Recognition (ASR):** Disambiguates phonetically identical acoustic sequences (homophones):
  * $\checkmark$ $P(\text{I saw a van}) \gg P(\text{eyes awe of an})$
* **Spelling Correction & Typing Assistance:** Evaluates contextual plausibility among typographic edit candidates:
  * $\checkmark$ $P(\text{about fifteen minutes from}) > P(\text{about fifteen minuets from})$
* **Augmentative and Alternative Communication (AAC):** Accelerates communication for motor-impaired users by dynamically predicting the next word on an eye-gaze or switch-selection interface.
* **Machine Translation (MT) & Summarization:** Evaluates target-language fluency and grammatical word order:
  * $\checkmark$ $P(\text{the green table}) \gg P(\text{the table green})$

---

## 2. The Chain Rule of Probability & The Counting Dilemma

### 2.1 The Chain Rule of Probability
From the foundational definition of conditional probability $P(A, B) = P(A)P(B \mid A)$, any joint distribution over $n$ variables factorizes recursively into a product of conditional probabilities:

$$P(w_1, w_2, \dots, w_n) = P(w_1) P(w_2 \mid w_1) P(w_3 \mid w_1, w_2) \cdots P(w_n \mid w_1, \dots, w_{n-1}) = \prod_{i=1}^n P(w_i \mid w_1, \dots, w_{i-1})$$

#### Worked Sentence Example
$$P(\text{its water is so transparent}) = P(\text{its}) \cdot P(\text{water}\mid\text{its}) \cdot P(\text{is}\mid\text{its water}) \cdot P(\text{so}\mid\text{its water is}) \cdot P(\text{transparent}\mid\text{its water is so})$$

### 2.2 The Empirical Counting Dilemma
Could we compute these conditional terms directly by counting relative frequencies in a raw training corpus?

$$P(w_n \mid w_1, \dots, w_{n-1}) \stackrel{?}{=} \frac{C(w_1, w_2, \dots, w_n)}{C(w_1, w_2, \dots, w_{n-1})}$$

* **The Failure Mode:** Natural language is creative and combinatorially infinite. The space of possible sentences dwarfs any finite text collection. Long histories almost never reoccur verbatim in training corpora, causing $C(w_1, \dots, w_{n-1}) = 0$ (division by zero and catastrophic probability collapse $P(W) = 0$).

---

## 3. The Markov Assumption & The $N$-gram Hierarchy

To make probability estimation computationally tractable, the **Markov Assumption** (Andrei Markov) posits that the probability of an incoming word depends only on the immediately preceding $k$ words, rather than the entire historical sequence:

$$P(w_i \mid w_1, w_2, \dots, w_{i-1}) \approx P(w_i \mid w_{i-k}, \dots, w_{i-1})$$

The parameter $k$ defines the $N$-gram model order ($N = k + 1$):

| Model Name | Order $N$ | Conditioning Context ($k$) | Mathematical Definition & MLE Formula |
| :--- | :---: | :---: | :--- |
| **Unigram** | $N=1$ | None ($k=0$, Bag-of-words independence) | $P(W) \approx \prod_{i=1}^n P(w_i), \quad P_{\text{MLE}}(w_i) = \frac{C(w_i)}{N_{\text{tokens}}}$ |
| **Bigram** | $N=2$ | 1 word: $w_{i-1}$ ($k=1$) | $P(W) \approx \prod_{i=1}^n P(w_i \mid w_{i-1}), \quad P_{\text{MLE}}(w_i \mid w_{i-1}) = \frac{C(w_{i-1}, w_i)}{C(w_{i-1})}$ |
| **Trigram** | $N=3$ | 2 words: $(w_{i-2}, w_{i-1})$ ($k=2$) | $P(w_i \mid w_{<i}) \approx P(w_i \mid w_{i-2}, w_{i-1}) = \frac{C(w_{i-2}, w_{i-1}, w_i)}{C(w_{i-2}, w_{i-1})}$ |
| **General $N$-gram** | $N$ | $N-1$ words: $w_{i-N+1}^{i-1}$ ($k=N-1$) | $P(w_i \mid w_{<i}) \approx P(w_i \mid w_{i-N+1}^{i-1}) = \frac{C(w_{i-N+1}^i)}{C(w_{i-N+1}^{i-1})}$ |

### Sentence Boundary Padding
To define a mathematically consistent probability distribution over variable-length sentences (so that sentences can end naturally), text is augmented with explicit boundary tokens: `<s>` (start of sentence) and `</s>` (end of sentence).
* **Bigram Sentence Scoring Example:**
  $$P(\text{<s> I want food </s>}) = P(\text{I}\mid\text{<s>}) \times P(\text{want}\mid\text{I}) \times P(\text{food}\mid\text{want}) \times P(\text{</s>}\mid\text{food})$$

---

## 4. Limitations of Markov Models & Practical Computation

* **Violation of Long-Distance Syntactic Dependencies:** Real language violates the Markov property across subordinate clauses. A bigram or trigram cannot maintain grammatical agreement across intervening words:
  * $\times$ *"The **books** that I borrowed yesterday from the central library **were** fascinating."*  
    *(A bigram only evaluates $P(\text{were}\mid\text{library})$, failing to enforce plural agreement with "books")*.
* **Context Horizon vs. Parameter Explosion Dilemma:** The parameter space scales exponentially as $\mathcal{O}(|V|^N)$. For a vocabulary $|V| = 100,000$, a 4-gram entails $10^{20}$ possible parameters. The vast majority never appear in training, leading to extreme data sparsity.
* **Underflow Prevention via Log-Space Computation:** Multiplying hundreds of small probabilities $p_i \ll 1$ leads to numerical floating-point underflow. In practice, all computations are performed in log-space:
  $$\log P(W) = \sum_{i=1}^n \log P(w_i \mid w_{i-N+1}^{i-1}), \qquad P(W) = \exp(\log P(W))$$
  Adding logarithms prevents underflow, preserves numerical precision, and accelerates inference.

---

## 5. Model Evaluation: Extrinsic (In-Vivo) vs. Intrinsic (In-Vitro)

| Evaluation Paradigm | Operational Methodology & Characterization | Engineering Trade-offs |
| :--- | :--- | :--- |
| **Extrinsic Evaluation**<br>*(In-Vivo / End-to-End)* | Embed the LM inside an end-user application (e.g., Speech Recognizer, Machine Translation engine). Run the full pipeline and measure task performance (e.g., Word Error Rate (WER) in ASR, BLEU in MT). | **Pros:** Directly measures real-world operational utility.<br>**Cons:** Extremely slow, expensive, and improvements can be confounded by other pipeline components. |
| **Intrinsic Evaluation**<br>*(In-Vitro / Standalone)* | Measure how well the LM predicts held-out, unseen natural text directly, independent of any external system. Evaluates assigned probability via **Perplexity**. | **Pros:** Fast, cheap, reproducible, and provides instantaneous feedback during model training.<br>**Cons:** Lower perplexity does not guarantee higher downstream task metric. |

---

## 6. Dataset Partitioning, Integrity & Data Leakage

Valid evaluation requires strict segregation of textual data into three non-overlapping partitions:
1. **Training Set (typically 80%):** Used to compute raw $N$-gram frequency statistics and train base parameters.
2. **Development Set / Validation Set (typically 10%):** A held-out partition used strictly to tune **hyperparameters** (e.g., smoothing parameters $k$, interpolation weights $\lambda$, backoff penalties $\alpha$) and diagnose error modes without compromising the test set.
3. **Test Set (typically 10%):** Reserved exclusively for a single, final evaluation. Must never be consulted during training or tuning.

* **Data Leakage (Training on the Test Set):** If sentences from the test set contaminate the training data, the model memorizes test $N$-grams, reporting artificially deflated perplexity that fails completely on genuinely novel text.
* **Distributional Consistency:** The training, dev, and test sets must match in domain, genre, register, and dialect (e.g., an LM trained on 19th-century literature will fail when evaluated on contemporary social media text).

---

## 7. Perplexity ($\text{PP}$): Mathematical Formulation

> ### 📐 Mathematical Definition: Perplexity ($\text{PP}$)
> The **Perplexity** ($\text{PP}$) of a language model on a test set $W = (w_1, w_2, \dots, w_N)$ containing $N$ words is the **inverse probability of the test set, normalized by the total number of words**:
> 
> $$\text{PP}(W) = P(w_1, w_2, \dots, w_N)^{-\frac{1}{N}} = \sqrt[N]{\frac{1}{P(w_1, w_2, \dots, w_N)}} = \sqrt[N]{\prod_{i=1}^N \frac{1}{P(w_i \mid w_{i-1})}} = \exp\left( -\frac{1}{N} \sum_{i=1}^N \ln P(w_i \mid w_{i-1}) \right)$$
> 
> **Information-Theoretic Connection:** Perplexity is the base-2 exponentiation of the **cross-entropy** $H(W)$:
> $$H(W) = -\frac{1}{N} \log_2 P(w_1, \dots, w_N) \quad \Longrightarrow \quad \text{PP}(W) = 2^{H(W)}$$
> 
> **Minimization Principle:** Minimizing cross-entropy $\iff$ Maximizing test probability $\iff$ **Minimizing Perplexity**.

---

## 8. Physical Intuition: Perplexity as Weighted Effective Branching Factor

What does a perplexity value of $k$ physically mean? It measures the **effective branching factor** of the language:
* **Intuition:** If an LM must guess the next word from a vocabulary, a perplexity of $B$ means the model is as uncertain as if it were choosing uniformly at random among $B$ equally probable alternatives.
* **Deterministic Language with Equal Branching:** Consider a language alphabet of size $B$ where every word is followed by any of the $B$ words with equal probability $P(w) = \frac{1}{B}$. For a sentence of length $N$:
  $$P(W) = \left(\frac{1}{B}\right)^N \implies \text{PP}(W) = \left[\left(\frac{1}{B}\right)^N\right]^{-\frac{1}{N}} = B$$
  Thus, for a completely uniform distribution, perplexity **exactly equals** the branching factor $B$.

### Concrete Walkthrough: Uniform vs. Biased Models
Consider a miniature vocabulary $L = \{\text{red}, \text{blue}, \text{green}\}$ ($B=3$), and a test set of $N=5$ words: $T = \text{red red red red blue}$.
* **Model A (Uniform Guessing):** $P(\text{red}) = P(\text{blue}) = P(\text{green}) = \frac{1}{3} \implies P_A(T) = (1/3)^5 = \frac{1}{243} \approx 0.004116$.
  $$\text{PP}_A(T) = \left[(1/3)^5\right]^{-\frac{1}{5}} = \mathbf{3.00} \quad \text{(Maximally uncertain across all 3 vocabulary candidates)}$$
* **Model B (Learned Regularities):** $P(\text{red}) = 0.8$, $P(\text{blue}) = 0.1$, $P(\text{green}) = 0.1$.
  $$P_B(T) = 0.8^4 \times 0.1^1 = 0.4096 \times 0.1 = 0.04096 \quad \Longrightarrow \quad \text{PP}_B(T) = (0.04096)^{-\frac{1}{5}} \approx \mathbf{1.89}$$
* **Takeaway:** Model B leverages frequency knowledge to collapse its uncertainty from 3 choices down to an effective branching factor of **1.89**. A lower perplexity indicates higher predictive certainty and superior language modeling.

> ### ⚠️ The Zero-Probability Breakdown: Why Smoothing is Mathematically Mandatory
> If a single test $N$-gram $(w_{i-1}, w_i)$ never occurred in the training corpus, maximum likelihood estimation assigns:
> $$P_{\text{MLE}}(w_i \mid w_{i-1}) = 0 \quad \Longrightarrow \quad P(W) = 0 \quad \Longrightarrow \quad \text{PP}(W) = \lim_{p \to 0^+} \left( \dots \times \frac{1}{0} \dots \right)^{\frac{1}{N}} = \boldsymbol{\infty}$$
> A single missing bigram in a 100,000-word test document destroys the entire evaluation metric. This fatal mathematical pathology makes **smoothing mandatory**.

---

## 9. The Data Sparsity Crisis & The Philosophy of Smoothing

* **Zipfian Sparsity:** In the Berkeley Restaurant corpus ($N=9222$ sentences), out of all possible bigrams between vocabulary words, over **99.7%** have a count of zero.
* **The Smoothing Mandate:** **Smoothing** shaves a fraction of probability mass from frequently observed $N$-grams and redistributes it to unobserved events (zeros), ensuring $P(w_i \mid w_{i-1}) > 0$ for all possible sequences while maintaining a valid probability sum $\sum_w P(w \mid \text{context}) = 1$.

---

## 10. Add-One (Laplace) Smoothing

Laplace smoothing pretends every possible $N$-gram has been observed exactly one additional time:
* **Mathematical Formulation:**
  $$P_{\text{Laplace}}(w_i \mid w_{i-1}) = \frac{C(w_{i-1}, w_i) + 1}{C(w_{i-1}) + |V|}$$
  where $|V|$ is the total vocabulary size.
* **Proof of Valid Distribution:**
  $$\sum_{w_i \in V} P_{\text{Laplace}}(w_i \mid w_{i-1}) = \frac{\sum_{w_i \in V} C(w_{i-1}, w_i) + |V|}{C(w_{i-1}) + |V|} = \frac{C(w_{i-1}) + |V|}{C(w_{i-1}) + |V|} = 1$$
* **Reconstituted (Adjusted) Counts $c^*$:** What count $c^*$ would yield the smoothed probability if divided by raw context count $C(w_{i-1})$?
  $$P_{\text{Laplace}}(w_i \mid w_{i-1}) = \frac{c^*(w_{i-1}, w_i)}{C(w_{i-1})} \quad \Longrightarrow \quad c^*(w_{i-1}, w_i) = [C(w_{i-1}, w_i) + 1] \times \frac{C(w_{i-1})}{C(w_{i-1}) + |V|}$$
* **Discount Ratio ($d$):** The fractional count retained after smoothing: $d_c = \frac{c^*}{c}$.
* **Why Add-1 is a "Blunt Instrument" (Pathology):**  
  Because $|V|$ is typically large (e.g., $10^4$ to $10^5$), the denominator $C(w_{i-1}) + |V|$ is overwhelmingly dominated by $|V|$. Laplace smoothing shifts a **monstrous amount of probability mass** into the zeros:
  * In the Berkeley Restaurant corpus ($|V| = 1446$), the frequent bigram *"want to"* has raw count $C = 608$.
  * Its reconstituted count plummets to $c^* = (608 + 1) \frac{927}{927 + 1446} \approx \mathbf{238}$ ($d = 0.39$). Probability $P(\text{to}\mid\text{want})$ crashes from $0.66 \to 0.26$!

---

## 11. Add-$k$ (Lidstone) Smoothing

To mitigate the excessive mass destruction of Laplace smoothing, Add-$k$ smoothing adds a fractional count $k \in (0, 1)$ (typically $k \in [0.01, 0.5]$):

$$P_{\text{Add-}k}(w_i \mid w_{i-1}) = \frac{C(w_{i-1}, w_i) + k}{C(w_{i-1}) + k|V|}$$

* **Hyperparameter Tuning:** The value of $k$ cannot be tuned on the test set. It is chosen to maximize log-likelihood on the **development set**.
* **Fundamental Inherent Flaw:** Add-$k$ still assigns identical probability $\frac{k}{C(w_{i-1}) + k|V|}$ to every unobserved word. It cannot distinguish between an unseen plausible word (e.g. *"eat a mango"*) and an unseen absurd word (e.g. *"eat a pterodactyl"*), treating both identically because it ignores unigram base rates.

---

## 12. Linear Interpolation & EM Optimization (Lab 3 Ground Truth)

Instead of blindly adding uniform mass, **Linear Interpolation** mixes evidence across higher- and lower-order models:
* **Simple Linear Interpolation:** Combine trigram, bigram, and unigram MLE estimates using weights $\lambda_i$:
  $$P_{\text{interp}}(w_i \mid w_{i-2}, w_{i-1}) = \lambda_1 P_{\text{MLE}}(w_i) + \lambda_2 P_{\text{MLE}}(w_i \mid w_{i-1}) + \lambda_3 P_{\text{MLE}}(w_i \mid w_{i-2}, w_{i-1})$$
  subject to the simplex constraints: $\lambda_1 + \lambda_2 + \lambda_3 = 1$ and $\lambda_j \ge 0$.
* **Context-Conditioned Interpolation:** The mixture weights are conditioned on context frequency: $\lambda_j(w_{i-2:i-1})$. If a trigram context is observed thousands of times, assign high weight to $\lambda_3$; if context is rare, shift weight to unigram $\lambda_1$.

> ### ⚙️ The Expectation-Maximization (EM) Algorithm for Mixture Weights (Lab 3 Exercise 5)
> The mixture weights $\boldsymbol{\lambda} = (\lambda_1, \lambda_2, \lambda_3)$ are learned on a **held-out validation corpus** by maximizing log-likelihood via EM:
> 1. **Initialization:** Fix $N$-gram parameters trained on training set. Initialize mixture weights uniformly: $\lambda_1 = \lambda_2 = \dots = \frac{1}{N_{\text{orders}}}$.
> 2. **Expectation Step (E-step):** For each token $w_i$ in the held-out set, compute the **posterior responsibility** of each $N$-gram order:
>    $$\text{Resp}_{\text{unigram}}(w_i) = \frac{\lambda_1 P(w_i)}{P_{\text{interp}}(w_i \mid \text{context})}, \qquad \text{Resp}_{\text{bigram}}(w_i) = \frac{\lambda_2 P(w_i \mid w_{i-1})}{P_{\text{interp}}(w_i \mid \text{context})}$$
> 3. **Maximization Step (M-step):** Re-estimate optimal $\lambda$ weights by summing responsibilities across all tokens in the held-out corpus:
>    $$\lambda_1^{\text{new}} = \frac{\sum_{w_i} \text{Resp}_{\text{unigram}}(w_i)}{\sum_{w_i} [\text{Resp}_{\text{unigram}}(w_i) + \text{Resp}_{\text{bigram}}(w_i)]}, \qquad \lambda_2^{\text{new}} = \frac{\sum_{w_i} \text{Resp}_{\text{bigram}}(w_i)}{\sum_{w_i} [\text{Resp}_{\text{unigram}}(w_i) + \text{Resp}_{\text{bigram}}(w_i)]}$$
> 4. **Convergence:** Repeat E-step and M-step iteratively until $|\lambda_j^{\text{new}} - \lambda_j| < \epsilon = 10^{-3}$. Guaranteed to improve held-out likelihood.

---

## 13. Backoff Smoothing Architectures: Stupid Backoff & Katz Backoff

While interpolation always combines all orders, **backoff** relies on the highest available $N$-gram and *only* falls back to lower orders when higher-order counts are zero:
* **Katz Backoff (Formal Probability Distribution):** Uses Good-Turing discounting to calculate discounted probability $P^*(w_i \mid w_{i-1})$ for observed bigrams. The reserved probability mass $1 - \sum_{w: c>0} P^*(w \mid w_{i-1})$ is distributed to unseen bigrams in proportion to their lower-order unigram probabilities:
  $$P_{\text{Katz}}(w_i \mid w_{i-1}) = \begin{cases} P^*(w_i \mid w_{i-1}) = \frac{c^*(w_{i-1}, w_i)}{C(w_{i-1})} & \text{if } C(w_{i-1}, w_i) > 0 \\ \alpha(w_{i-1}) P_{\text{Katz}}(w_i) & \text{if } C(w_{i-1}, w_i) = 0 \end{cases}$$
  where normalization constant $\alpha(w_{i-1}) = \frac{1 - \sum_{w: c>0} P^*(w \mid w_{i-1})}{1 - \sum_{w: c>0} P(w)}$ ensures $\sum_w P_{\text{Katz}}(w \mid w_{i-1}) = 1$.

> ### 🚀 Stupid Backoff: Web-Scale Language Modeling (Brants et al., 2007 & Lab 3)
> Designed for gigantic web corpora (e.g., Google $N$-gram release with $10^{12}$ tokens), **Stupid Backoff** drops formal probability normalization in favor of raw computational efficiency:
> 
> $$S(w_i \mid w_{i-k+1}^{i-1}) = \begin{cases} \frac{C(w_{i-k+1}^i)}{C(w_{i-k+1}^{i-1})} & \text{if } C(w_{i-k+1}^i) > 0 \\ \alpha \cdot S(w_i \mid w_{i-k+2}^{i-1}) & \text{otherwise (back off to lower-order)} \end{cases}$$
> 
> * **Base Condition (Unigram):** $S(w_i) = \frac{C(w_i)}{N_{\text{tokens}}}$.
> * **Empirical Discount Factor:** $\alpha = 0.4$.
> * **Theoretical Distinction:** The scores $S$ **do not sum to 1** and are not true probabilities. However, they preserve relative ranking, scale gracefully to billions of parameters, and rival complex models in downstream performance.

---

## 14. Comprehensive Comparative Matrix of Smoothing Methods

| Smoothing Method | Valid Prob? ($\sum P = 1$) | Mathematical Core / Operational Mechanics | Diagnostic Limitations & Use Case |
| :--- | :---: | :--- | :--- |
| **Laplace (Add-1)** | $\checkmark$ Yes | Adds $1$ to all counts: $\frac{C(w_{i-1}, w_i) + 1}{C(w_{i-1}) + \|V\|}$. | **Blunt instrument:** transfers massive mass to zeros. Never used in modern NLP; purely historical. |
| **Add-$k$ (Lidstone)** | $\checkmark$ Yes | Adds $k \in (0, 1)$ to counts: $\frac{C(w_{i-1}, w_i) + k}{C(w_{i-1}) + k\|V\|}$. | Treats all unobserved words uniformly; ignores unigram base rates. Useful only for text classification. |
| **Linear Interpolation** | $\checkmark$ Yes | Weighted sum of orders: $\sum \lambda_j P_j$; $\boldsymbol{\lambda}$ tuned on dev set via EM algorithm. | Highly effective; captures unigram plausibility for unseen $N$-grams. Standard for small/medium corpora. |
| **Katz Backoff** | $\checkmark$ Yes | Good-Turing discounting on observed counts; backs off strictly when count $=0$ with scaling $\alpha$. | Rigorous probability distribution; requires Good-Turing discount schedules. Computationally demanding. |
| **Stupid Backoff** | $\times$ No<br>*(Heuristic score)* | Backs off recursively with constant decay $\alpha = 0.4$: $S = \alpha \cdot S_{\text{lower}}$. | Extremely fast, no normalization overhead. Preferred industry standard for web-scale corpora. |

---

## 15. Unknown Words: Open vs. Closed Vocabularies & The `<UNK>` Protocol

Real-world natural language text constantly introduces unseen words: named entities, neologisms, and domain terminology:
* **Closed Vocabulary Assumption:** Assumes test vocabulary is identical to training ($V_{\text{test}} \subseteq V_{\text{train}}$). Out-of-vocabulary words are assumed impossible. Completely unviable for open-world NLP.
* **Open Vocabulary Task:** Explicitly models the occurrence of unknown words (**Out-Of-Vocabulary / OOV** words) using a designated pseudo-token: `<UNK>`.

> ### 🏷️ The Two-Step `<UNK>` Protocol & Perplexity Comparison Integrity
> Handling OOV tokens requires strict training and inference discipline:
> 1. **Training Phase (Vocabulary Induction):** Fix vocabulary lexicon $L$ (top $K$ types or words with count $C(w) \ge \text{threshold}$). In training corpus normalization, replace all words not in $L$ with `<UNK>`. Train $N$-gram probabilities treating `<UNK>` as an ordinary word (estimating $P(\text{<UNK>}\mid w_{i-1})$).
> 2. **Inference Phase (Test Scoring):** Map any unseen test word $w \notin L$ to `<UNK>` and score using $P(\text{<UNK>}\mid\text{context})$.
> 
> ---
> **Golden Rule of Evaluation Integrity:** Two LMs can be compared via perplexity **if and only if they share the identical vocabulary**. An LM with a smaller vocabulary trivially achieves a lower (better-looking) perplexity because probability mass is distributed across fewer options. Dropping OOV tokens invalidates comparability.

---
*Summary compiled for Natural Language Processing (ENSIA 2026–2027) based on Lecture 3 materials and Lab 3 implementations.*
