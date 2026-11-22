# NLP Lecture 6: Vector Semantics & Embeddings
**Comprehensive Course Summary (ENSIA S7 2026–2027)**  
*Instructor: Prof. Ahmed Guessoum*

---

> ### 📌 Lecture Scope & Foundations
> Traditional symbolic NLP represents vocabulary words as discrete atomic symbols or orthogonal one-hot indicator vectors $\mathbf{e}_w \in \{0, 1\}^{|V|}$, rendering all distinct words mutually orthogonal and equidistant:
> $$\|\mathbf{e}_{\text{cat}} - \mathbf{e}_{\text{dog}}\|_2 = \|\mathbf{e}_{\text{cat}} - \mathbf{e}_{\text{refrigerator}}\|_2 = \sqrt{2}$$
> **Vector Semantics** replaces discrete symbols with continuous geometric representations based on the **Distributional Hypothesis** (Firth, 1957): *"You shall know a word by the company it keeps!"*
> 1. **Sparse Count-Based Representations:** High-dimensional ($|V| \approx 50{,}000$), sparse co-occurrence vectors weighted by Information Retrieval metrics (TF-IDF) or information-theoretic association (Positive Pointwise Mutual Information, PPMI).
> 2. **Dense Learned Embeddings:** Low-dimensional ($d \in [50, 300]$), continuous representations optimized via self-supervised binary classification (Word2Vec Skip-Gram with Negative Sampling, SGNS).
> 3. **Geometric Properties & Operations:** Cosine angle similarity, context window dynamics, analogical reasoning via vector offsets (the Parallelogram method), polysemy limitations, and subspace debiasing.

---

## 1. Vector Space Models: Co-occurrence Matrix Architectures

A **Vector Space Model (VSM)** maps linguistic entities into geometric spaces where semantic distance corresponds to contextual similarity.

```
       [Raw Text Corpus]
               │
      ┌────────┴────────┐
      ▼                 ▼
[Term-Document]   [Term-Context]
  (|V| × |D|)       (|V| × |V|)
      │                 │
      ▼                 ▼
   TF-IDF             PPMI
(Search / Docs)   (Word Meaning)
                        │
                        ▼
                 [Dense Embeddings]
                   Word2Vec SGNS
                     (d ≈ 300)
```

### 1.1 Term-Document Matrix ($|V| \times |D|$)
* **Structure:** Rows index the vocabulary $V$ ($|V|$ terms); columns index the corpus documents $D$ ($|D|$ documents).
* **Document Vector:** Each document $d_j$ is a column vector containing term frequencies:
  $$\mathbf{d}_j = [f_{1j}, f_{2j}, \dots, f_{|V|j}]^T$$
* **Term Vector:** Each term $w_i$ is a row vector recording occurrences across documents:
  $$\mathbf{w}_i = [f_{i1}, f_{i2}, \dots, f_{i|D|}]$$
* **Primary NLP Application:** Document retrieval, search engine indexing, text clustering, and computing document-document topical similarity.

### 1.2 Term-Context / Word-Word Matrix ($|V| \times |V|$)
* **Structure:** A square vocabulary-by-vocabulary matrix tracking co-occurrence frequencies within a sliding context window of $\pm L$ tokens around target word $w_i$.
* **Matrix Entry:** Cell $F_{ij} = \text{count}(w_i, c_j)$ indicates how often candidate context word $c_j$ occurs within window distance $L$ of target word $w_i$.
* **Primary NLP Application:** Word-level semantic similarity, distributional clustering, discovering synonyms, and measuring linguistic relatedness.

---

## 2. Vector Similarity: Dot Product & Cosine Similarity

### 2.1 The Dot Product & The Vector Length Pathology
The Euclidean dot product between two vectors $\mathbf{v}, \mathbf{w} \in \mathbb{R}^d$ is:
$$\mathbf{v} \cdot \mathbf{w} = \sum_{i=1}^d v_i w_i = \|\mathbf{v}\|_2 \|\mathbf{w}\|_2 \cos \theta$$

> [!WARNING]
> **The Vector Length Pathology (Failure of Raw Dot Product):**
> The raw dot product scales linearly with the Euclidean magnitudes $\|\mathbf{v}\|_2$ and $\|\mathbf{w}\|_2$. If a word or document occurs frequently in the corpus, its counts will be massive. Consequently, its raw dot product with completely unrelated terms will be deceptively high solely due to raw occurrence volume, not genuine semantic affinity.

### 2.2 Cosine Similarity Formulation
Cosine similarity cures this pathology by dividing the dot product by the product of their L2 Euclidean norms ($L_2 = \sqrt{\sum v_i^2}$). This normalizes the vectors to unit length ($\hat{\mathbf{v}} = \frac{\mathbf{v}}{\|\mathbf{v}\|_2}$) and measures exclusively the **angle $\theta$** between them:

$$\text{Cosine}(\mathbf{v}, \mathbf{w}) = \frac{\mathbf{v} \cdot \mathbf{w}}{\|\mathbf{v}\|_2 \|\mathbf{w}\|_2} = \frac{\sum_{i=1}^d v_i w_i}{\sqrt{\sum_{i=1}^d v_i^2}\sqrt{\sum_{i=1}^d w_i^2}} = \left(\frac{\mathbf{v}}{\|\mathbf{v}\|_2}\right) \cdot \left(\frac{\mathbf{w}}{\|\mathbf{w}\|_2}\right)$$

* **Range for Non-Negative Counts ($v_i, w_i \ge 0$):**
  * $\text{Cosine} = 1.0 \iff \theta = 0^\circ$: Vectors point in identical directions (collinear / perfectly proportional context profiles).
  * $\text{Cosine} = 0.0 \iff \theta = 90^\circ$: Vectors are orthogonal (share zero context words).

---

## 3. Full Step-by-Step Worked Exam Problem 1: Cosine Similarity on Context Counts

> **Exam Task:** Given co-occurrence counts across 3 context dimensions (`pie`, `data`, `computer`), compute the pairwise cosine similarity between $\mathbf{v}_{\text{cherry}}$ and $\mathbf{v}_{\text{information}}$, and between $\mathbf{v}_{\text{digital}}$ and $\mathbf{v}_{\text{information}}$. Explain the semantic implications.

| Target Word | $c_1 = \text{\texttt{pie}}$ | $c_2 = \text{\texttt{data}}$ | $c_3 = \text{\texttt{computer}}$ | Vector Representation $\mathbf{v}$ |
| :--- | :---: | :---: | :---: | :--- |
| $\mathbf{v}_{\text{cherry}}$ | $442$ | $8$ | $2$ | $[442, 8, 2]^T$ |
| $\mathbf{v}_{\text{digital}}$ | $5$ | $1683$ | $1670$ | $[5, 1683, 1670]^T$ |
| $\mathbf{v}_{\text{information}}$ | $5$ | $3982$ | $3325$ | $[5, 3982, 3325]^T$ |

### Step 1: Compute Vector L2 Euclidean Norms ($\|\mathbf{v}\|_2 = \sqrt{\sum v_i^2}$)
$$\|\mathbf{v}_{\text{cherry}}\|_2 = \sqrt{442^2 + 8^2 + 2^2} = \sqrt{195{,}364 + 64 + 4} = \sqrt{195{,}432} \approx \mathbf{442.08}$$
$$\|\mathbf{v}_{\text{digital}}\|_2 = \sqrt{5^2 + 1683^2 + 1670^2} = \sqrt{25 + 2{,}832{,}489 + 2{,}788{,}900} = \sqrt{5{,}621{,}414} \approx \mathbf{2370.95}$$
$$\|\mathbf{v}_{\text{information}}\|_2 = \sqrt{5^2 + 3982^2 + 3325^2} = \sqrt{25 + 15{,}856{,}324 + 11{,}055{,}625} = \sqrt{26{,}911{,}974} \approx \mathbf{5187.68}$$

### Step 2: Compute Raw Dot Products ($\mathbf{v} \cdot \mathbf{w}$)
$$\mathbf{v}_{\text{cherry}} \cdot \mathbf{v}_{\text{information}} = (442 \times 5) + (8 \times 3982) + (2 \times 3325) = 2210 + 31{,}856 + 6650 = \mathbf{40{,}716}$$
$$\mathbf{v}_{\text{digital}} \cdot \mathbf{v}_{\text{information}} = (5 \times 5) + (1683 \times 3982) + (1670 \times 3325) = 25 + 6{,}701{,}706 + 5{,}552{,}750 = \mathbf{12{,}254{,}481}$$

### Step 3: Compute Normalized Cosine Similarities
$$\text{Cosine}(\mathbf{v}_{\text{cherry}}, \mathbf{v}_{\text{information}}) = \frac{40{,}716}{442.08 \times 5187.68} = \frac{40{,}716}{2{,}293{,}368} \approx \mathbf{0.0177} \approx \mathbf{0.018}$$
$$\text{Cosine}(\mathbf{v}_{\text{digital}}, \mathbf{v}_{\text{information}}) = \frac{12{,}254{,}481}{2370.95 \times 5187.68} = \frac{12{,}254{,}481}{12{,}299{,}720} \approx \mathbf{0.9963} \approx \mathbf{0.996}$$

### Semantic Interpretation & Exam Takeaway
1. $\text{Cosine}(\text{cherry}, \text{information}) = 0.018 \approx 0 \implies$ **Orthogonal / Unrelated:** Despite the non-zero raw dot product ($40{,}716$), the two words share virtually zero semantic affinity. Their co-occurrence mass is concentrated in orthogonal subspaces (`pie` vs. `data`/`computer`).
2. $\text{Cosine}(\text{digital}, \text{information}) = 0.996 \approx 1 \implies$ **Parallel / Synonymous:** Their context profiles have almost identical proportional distributions across the computational dimensions, proving high semantic synonymy.

---

## 4. Vector Weighting Schemes: TF-IDF & PPMI

### 4.1 The Frequency Skew Pathology
Raw co-occurrence counts $f_{wc}$ are heavily distorted by high-frequency grammatical function words (*the, of, and, is, to*). These non-informative words co-occur with nearly all tokens purely by chance. An optimal weighting function must:
1. Dampen extreme term counts within a single context/document.
2. Discount words that co-occur with everything.
3. Amplify terms that carry high **informational specificity**.

### 4.2 TF-IDF Weighting (Information Retrieval & Document Spaces)

```
        Raw Term Count: count(t, d)
                     │
         [Logarithmic Dampening]
                     ▼
  Sub-linear TF: 1 + log10(count(t, d))
                     │
          [Corpus-level Specificity]
                     ▼
        IDF: log10( N / df_t )
                     │
             [Multiplication]
                     ▼
        TF-IDF = tf_{t,d} × idf_t
```

#### A. Sub-linear Term Frequency ($\text{tf}_{t,d}$)
A word appearing 20 times in a document is not 20 times more informative than one appearing once. Sub-linear logarithmic scaling squashes high frequencies:
$$\text{tf}_{t,d} = \begin{cases} 1 + \log_{10}(\text{count}(t, d)) & \text{if } \text{count}(t, d) > 0 \\ 0 & \text{otherwise} \end{cases}$$

#### B. Inverse Document Frequency ($\text{idf}_t$)
Measures term specificity across corpus $D$ ($N = |D|$ total documents; $\text{df}_t$ documents containing term $t$):
$$\text{idf}_t = \log_{10}\left(\frac{N}{\text{df}_t}\right)$$
* If a term appears in every document ($\text{df}_t = N$), $\text{idf}_t = \log_{10}(1) = 0$ (completely muted).
* Rare, highly specific terms receive large positive $\text{idf}_t$ values.

#### C. Compound Score & Document Centroids
$$\text{tf-idf}_{t,d} = \text{tf}_{t,d} \times \text{idf}_t$$
To represent an entire document $d$ as a single vector in semantic space, compute its **Centroid Vector**:
$$\mathbf{d} = \frac{1}{|d|} \sum_{w \in d} \mathbf{w} \qquad \text{or} \qquad \mathbf{d} = \sum_{w \in d} \text{tf-idf}(w, d) \cdot \mathbf{w}$$

---

## 5. Pointwise Mutual Information (PMI & PPMI) for Word-Word Spaces

### 5.1 Mathematical Formulation of PMI
**Pointwise Mutual Information (PMI)** measures whether target word $w$ and context word $c$ co-occur more frequently than expected under statistical independence:
$$\text{PMI}(w, c) = \log_2 \frac{P(w, c)}{P(w)P(c)}$$

Given an empirical co-occurrence count matrix $F \in \mathbb{R}^{|V| \times |C|}$ with total counts $N = \sum_{i}\sum_{j} f_{ij}$:
$$P(w, c) = \frac{f_{wc}}{N}, \qquad P(w) = \frac{\sum_{c'} f_{wc'}}{N} = \frac{f_{w\bullet}}{N}, \qquad P(c) = \frac{\sum_{w'} f_{w'c}}{N} = \frac{f_{\bullet c}}{N}$$
Substituting the joint and marginal probabilities:
$$\text{PMI}(w, c) = \log_2 \left( \frac{\frac{f_{wc}}{N}}{\frac{f_{w\bullet}}{N} \cdot \frac{f_{\bullet c}}{N}} \right) = \log_2 \left( \frac{f_{wc} \cdot N}{f_{w\bullet} \cdot f_{\bullet c}} \right) = \log_2 \left( \frac{f_{wc}}{E_{wc}} \right)$$
where $E_{wc} = \frac{f_{w\bullet} \cdot f_{\bullet c}}{N}$ is the **expected co-occurrence count** under statistical independence.

* $\text{PMI}(w, c) = 0 \iff f_{wc} = E_{wc}$: Words co-occur exactly at chance level.
* $\text{PMI}(w, c) > 0 \iff f_{wc} > E_{wc}$: Positive semantic association.
* $\text{PMI}(w, c) < 0 \iff f_{wc} < E_{wc}$: Mutual avoidance / negative association.

### 5.2 Positive Pointwise Mutual Information (PPMI) Truncation
Negative PMI scores are notoriously unreliable because:
1. Low/zero co-occurrence counts in corpus samples are noisy and sparse.
2. Human semantic intuition reflects association rather than absence.
**Positive PMI (PPMI)** truncates all negative values to zero:
$$\text{PPMI}(w, c) = \max(\text{PMI}(w, c), 0)$$

---

## 6. Full Step-by-Step Worked Exam Problem 2: Computing PPMI from Contingency Counts

> **Exam Task:** Given the $2 \times 2$ co-occurrence count matrix below, compute the expected counts $E_{wc} = \frac{f_{w\bullet} \cdot f_{\bullet c}}{N}$, the PMI scores, and the PPMI matrix.

| Target Word ($w$) | $c_1 = \text{\texttt{computer}}$ | $c_2 = \text{\texttt{pie}}$ | Marginal Row Sum $f_{w\bullet}$ |
| :--- | :---: | :---: | :---: |
| $w_1 = \text{\texttt{data}}$ | $10$ | $2$ | $\mathbf{12}$ |
| $w_2 = \text{\texttt{cherry}}$ | $1$ | $8$ | $\mathbf{9}$ |
| **Marginal Col Sum $f_{\bullet c}$** | $\mathbf{11}$ | $\mathbf{10}$ | **Total Sum $N = 21$** |

### Step 1: Compute Expected Counts under Independence ($E_{wc} = \frac{f_{w\bullet} \cdot f_{\bullet c}}{N}$)
$$E_{\text{data, comp}} = \frac{12 \times 11}{21} = \frac{132}{21} \approx \mathbf{6.29}, \qquad E_{\text{data, pie}} = \frac{12 \times 10}{21} = \frac{120}{21} \approx \mathbf{5.71}$$
$$E_{\text{cherry, comp}} = \frac{9 \times 11}{21} = \frac{99}{21} \approx \mathbf{4.71}, \qquad E_{\text{cherry, pie}} = \frac{9 \times 10}{21} = \frac{90}{21} \approx \mathbf{4.29}$$

### Step 2: Compute $\text{PMI}(w, c) = \log_2 (f_{wc} / E_{wc})$
$$\text{PMI}(\text{data}, \text{comp}) = \log_2(10 / 6.29) = \log_2(1.5898) \approx \mathbf{+0.670} \text{ bits}$$
$$\text{PMI}(\text{data}, \text{pie}) = \log_2(2 / 5.71) = \log_2(0.3503) \approx \mathbf{-1.515} \text{ bits}$$
$$\text{PMI}(\text{cherry}, \text{comp}) = \log_2(1 / 4.71) = \log_2(0.2123) \approx \mathbf{-2.238} \text{ bits}$$
$$\text{PMI}(\text{cherry}, \text{pie}) = \log_2(8 / 4.29) = \log_2(1.8648) \approx \mathbf{+0.901} \text{ bits}$$

### Step 3: Apply PPMI Thresholding ($\text{PPMI} = \max(\text{PMI}, 0)$)
$$\mathbf{PPMI} = \begin{pmatrix} \max(+0.670, 0) & \max(-1.515, 0) \\ \max(-2.238, 0) & \max(+0.901, 0) \end{pmatrix} = \begin{pmatrix} \mathbf{0.670} & \mathbf{0} \\ \mathbf{0} & \mathbf{0.901} \end{pmatrix}$$

---

## 7. Context Distribution Smoothing ($\text{PPMI}_\alpha$ with $\alpha = 0.75$)

### 7.1 The Rare Word Bias Pathology
Standard PMI exhibits severe mathematical pathology: it strongly over-weights pairs containing extremely rare context words. If a rare context word $c_{\text{rare}}$ appears only once in the entire corpus, its marginal probability $P(c_{\text{rare}})$ is infinitesimally small. Since $P(c)$ sits in the denominator of $\frac{P(w, c)}{P(w)P(c)}$, the resulting PMI is artificially massive.

### 7.2 The $\alpha = 0.75$ Smoothing Mechanism
Raise the context marginal counts to the power of $\alpha = 0.75$:
$$P_\alpha(c) = \frac{(\text{count}(c))^{\alpha}}{\sum_{c'} (\text{count}(c'))^{\alpha}} = \frac{(f_{\bullet c})^{0.75}}{\sum_{c'} (f_{\bullet c'})^{0.75}}$$
$$\text{PPMI}_\alpha(w, c) = \max\left( \log_2 \frac{P(w, c)}{P(w) P_\alpha(c)}, 0 \right)$$

* **Why $\alpha = 0.75$ Works:** Raising fractional numbers or small counts to the power of $0.75$ increases their relative mass ($x^{0.75} > x$ for small normalized probabilities). This inflates $P_\alpha(c)$ for rare words, enlarging the denominator and suppressing spuriously inflated PMI scores.

---

## 8. Dense Embeddings & Word2Vec Skip-Gram with Negative Sampling (SGNS)

### 8.1 Sparse vs. Dense Embeddings
* **Sparse Vectors (PPMI, TF-IDF):** High-dimensional ($|V| \ge 50{,}000$), $>98\%$ zeros, treat synonymous contexts as orthogonal axes, and cause parameter explosion in downstream neural networks.
* **Dense Vectors (Word2Vec, GloVe):** Low-dimensional ($d \in [50, 300]$), continuous representations where synonyms cluster together, dramatically improving generalization and computational efficiency.

### 8.2 The Skip-Gram Architecture with Negative Sampling (SGNS)
Proposed by Mikolov et al. (2013). Instead of training an intractable $|V|$-way softmax over the entire vocabulary:
$$\frac{\exp(\mathbf{c} \cdot \mathbf{w})}{\sum_{v \in V} \exp(\mathbf{v} \cdot \mathbf{w})} \quad (\text{intractable denominator for } |V| = 50{,}000+)$$
SGNS converts self-supervised learning into a **binary logistic regression** task:

```
Target Word: w ──┐
                 ├──► Dot Product c·w ──► Sigmoid σ(c·w) ──► P(+ | w, c)
Context Word: c ─┘
```

1. **Binary Task:** Given target $w$ and candidate $c$, predict: *Is $c$ a true context word ($y = 1$) or noise ($y = 0$)?*
2. **Positive Pairs ($+$):** For target word $w$, extract all words $c_{\text{pos}}$ occurring within a sliding context window of $\pm L$ tokens.
3. **Negative Pairs ($-$):** For each positive pair $(w, c_{\text{pos}})$, draw $k$ noise words $c_{\text{neg}_1}, \dots, c_{\text{neg}_k}$ from unigram noise distribution $P_\alpha(w) \propto \text{count}(w)^{0.75}$.

### 8.3 Sigmoid Classifier Probabilities
Target vector $\mathbf{w} \in \mathbb{R}^d$, Context vector $\mathbf{c} \in \mathbb{R}^d$:
$$P(+ \mid w, c) = \sigma(\mathbf{c} \cdot \mathbf{w}) = \frac{1}{1 + e^{-\mathbf{c} \cdot \mathbf{w}}}$$
$$P(- \mid w, c) = 1 - P(+ \mid w, c) = 1 - \sigma(\mathbf{c} \cdot \mathbf{w}) = \sigma(-\mathbf{c} \cdot \mathbf{w}) = \frac{1}{1 + e^{\mathbf{c} \cdot \mathbf{w}}}$$

---

## 9. SGNS Objective Function & Analytical Gradient Derivations

### 9.1 Binary Cross-Entropy Objective Function
For a single target word $w$, one positive context word $c_{\text{pos}}$, and $k$ negative samples $c_{\text{neg}_1}, \dots, c_{\text{neg}_k}$:
$$\mathcal{L}_{\text{Likelihood}} = P(+ \mid w, c_{\text{pos}}) \prod_{i=1}^k P(- \mid w, c_{\text{neg}_i}) = \sigma(\mathbf{c}_{\text{pos}} \cdot \mathbf{w}) \prod_{i=1}^k \sigma(-\mathbf{c}_{\text{neg}_i} \cdot \mathbf{w})$$
Taking the negative log-likelihood yields the **SGNS Binary Cross-Entropy Loss**:
$$\mathcal{L}_{\text{CE}} = - \log \sigma(\mathbf{c}_{\text{pos}} \cdot \mathbf{w}) - \sum_{i=1}^k \log \sigma(-\mathbf{c}_{\text{neg}_i} \cdot \mathbf{w})$$

### 9.2 Analytical Gradient Derivations (Critical Exam Derivations)

> [!NOTE]
> **Foundational Sigmoid Derivative Lemmas:**
> 1. $\frac{d}{dz} \log \sigma(z) = \frac{1}{\sigma(z)} \cdot \sigma(z)[1 - \sigma(z)] = 1 - \sigma(z)$
> 2. $\frac{d}{dz} \log \sigma(-z) = \frac{1}{\sigma(-z)} \cdot [-\sigma(-z)(1 - \sigma(-z))] = -(1 - \sigma(-z)) = -\sigma(z)$

#### 1. Partial Derivative with respect to Positive Context Vector $\mathbf{c}_{\text{pos}}$
$$\frac{\partial \mathcal{L}_{\text{CE}}}{\partial \mathbf{c}_{\text{pos}}} = -\frac{\partial}{\partial \mathbf{c}_{\text{pos}}} \log \sigma(\mathbf{c}_{\text{pos}} \cdot \mathbf{w}) = - [1 - \sigma(\mathbf{c}_{\text{pos}} \cdot \mathbf{w})] \frac{\partial (\mathbf{c}_{\text{pos}} \cdot \mathbf{w})}{\partial \mathbf{c}_{\text{pos}}} = \mathbf{[\sigma(\mathbf{c}_{\text{pos}} \cdot \mathbf{w}) - 1]\mathbf{w}}$$

#### 2. Partial Derivative with respect to Negative Context Vector $\mathbf{c}_{\text{neg}_i}$
$$\frac{\partial \mathcal{L}_{\text{CE}}}{\partial \mathbf{c}_{\text{neg}_i}} = -\frac{\partial}{\partial \mathbf{c}_{\text{neg}_i}} \log \sigma(-\mathbf{c}_{\text{neg}_i} \cdot \mathbf{w}) = - [-\sigma(\mathbf{c}_{\text{neg}_i} \cdot \mathbf{w})] \frac{\partial (\mathbf{c}_{\text{neg}_i} \cdot \mathbf{w})}{\partial \mathbf{c}_{\text{neg}_i}} = \mathbf{[\sigma(\mathbf{c}_{\text{neg}_i} \cdot \mathbf{w})]\mathbf{w}}$$

#### 3. Partial Derivative with respect to Target Word Vector $\mathbf{w}$
$$\frac{\partial \mathcal{L}_{\text{CE}}}{\partial \mathbf{w}} = -\frac{\partial}{\partial \mathbf{w}} \log \sigma(\mathbf{c}_{\text{pos}} \cdot \mathbf{w}) - \sum_{i=1}^k \frac{\partial}{\partial \mathbf{w}} \log \sigma(-\mathbf{c}_{\text{neg}_i} \cdot \mathbf{w})$$
$$\frac{\partial \mathcal{L}_{\text{CE}}}{\partial \mathbf{w}} = \mathbf{[\sigma(\mathbf{c}_{\text{pos}} \cdot \mathbf{w}) - 1]\mathbf{c}_{\text{pos}} + \sum_{i=1}^k [\sigma(\mathbf{c}_{\text{neg}_i} \cdot \mathbf{w})]\mathbf{c}_{\text{neg}_i}}$$

---

## 10. Stochastic Gradient Descent (SGD) Updates & Vector Matrices

### 10.1 Parameter Update Equations (Learning Rate $\eta$)
Applying gradient descent $\theta^{(t+1)} = \theta^{(t)} - \eta \nabla_\theta \mathcal{L}_{\text{CE}}$:
$$\mathbf{c}_{\text{pos}}^{(t+1)} = \mathbf{c}_{\text{pos}}^{(t)} - \eta \, [\sigma(\mathbf{c}_{\text{pos}}^{(t)} \cdot \mathbf{w}^{(t)}) - 1]\,\mathbf{w}^{(t)}$$
$$\mathbf{c}_{\text{neg}_i}^{(t+1)} = \mathbf{c}_{\text{neg}_i}^{(t)} - \eta \, [\sigma(\mathbf{c}_{\text{neg}_i}^{(t)} \cdot \mathbf{w}^{(t)})]\,\mathbf{w}^{(t)} \qquad (\forall i \in \{1, \dots, k\})$$
$$\mathbf{w}^{(t+1)} = \mathbf{w}^{(t)} - \eta \left( [\sigma(\mathbf{c}_{\text{pos}}^{(t)} \cdot \mathbf{w}^{(t)}) - 1]\,\mathbf{c}_{\text{pos}}^{(t)} + \sum_{i=1}^k [\sigma(\mathbf{c}_{\text{neg}_i}^{(t)} \cdot \mathbf{w}^{(t)})]\,\mathbf{c}_{\text{neg}_i}^{(t)} \right)$$

### 10.2 Geometric Force Interpretation
* **Attraction of True Contexts:** For positive context $c_{\text{pos}}$, $[\sigma(\cdot) - 1] < 0$. The update adds $+\eta (1 - \sigma)\mathbf{w}$, pulling $\mathbf{c}_{\text{pos}}$ **toward** target vector $\mathbf{w}$.
* **Repulsion of Noise Samples:** For negative context $c_{\text{neg}}$, $\sigma(\cdot) > 0$. The update subtracts $-\eta \sigma \mathbf{w}$, pushing $\mathbf{c}_{\text{neg}}$ **away** from target vector $\mathbf{w}$.

### 10.3 The Two Embedding Matrices ($\mathbf{W}$ and $\mathbf{C}$)
The Word2Vec network learns two distinct weight matrices:
* Target matrix $\mathbf{W} \in \mathbb{R}^{|V| \times d}$ (row $i$ is target embedding $\mathbf{w}_i$).
* Context matrix $\mathbf{C} \in \mathbb{R}^{|V| \times d}$ (row $j$ is context embedding $\mathbf{c}_j$).
* **At Inference Time:**
  * Option A (Standard): Discard $\mathbf{C}$ entirely and keep $\mathbf{W}$.
  * Option B (Superior): Sum the matrices $\mathbf{e}_w = \mathbf{w} + \mathbf{c}$, which empirically captures richer semantic nuances.

---

## 11. Context Window Dynamics, Vector Analogies, Bias & Architecture Matrix

### 11.1 Context Window Size Dynamics ($L$)
| Window Size | Semantic & Linguistic Character | Concrete Example |
| :--- | :--- | :--- |
| **Small Window** ($L = \pm 1$ or $\pm 2$) | Captures **syntactic** and **grammatical** similarity. Nearest neighbors are interchangeable parts-of-speech and direct **co-hyponyms**. | Nearest neighbors for *dog* are *cat*, *puppy*, *terrier* (substitutable entities). |
| **Large Window** ($L = \pm 5$ to $\pm 10$) | Captures **topical**, **discourse**, and **associational** similarity. Neighbors reflect shared semantic scenarios and domain co-occurrence. | Nearest neighbors for *coffee* are *mug*, *barista*, *breakfast*, *caffeine*, *brew*. |

### 11.2 Analogical Reasoning via Parallelogram Method (Slides 96–99)
Solving proportional word analogies of the form $a : a^* :: b : \hat{b}^*$ (e.g., *man is to king as woman is to queen*):

```
       a* (king) ────────► b* (queen)
          ▲                    ▲
          │  + (a* - a)        │  + (a* - a)
          │                    │
       a (man)   ────────► b (woman)
```

1. **Vector Offset Arithmetic:** The difference vector $\mathbf{a}^* - \mathbf{a}$ isolates a semantic relational displacement vector (e.g., $+[\text{royalty}]$). Adding this vector to $\mathbf{b}$ points directly toward $\hat{\mathbf{b}}^*$:
   $$\hat{\mathbf{b}}^* \approx \mathbf{b} + (\mathbf{a}^* - \mathbf{a})$$
2. **The Parallelogram Optimization Formula (Slide 97):**
   $$\hat{b}^* = \arg\max_{x \in V \setminus \{a, a^*, b\}} \text{Cosine}(\mathbf{x}, \; \mathbf{a}^* - \mathbf{a} + \mathbf{b})$$
3. **Failure Modes & Caveats:**
   * **Input Exclusion:** The input query tokens $\{a, a^*, b\}$ must be explicitly masked out from the search; otherwise, high self-similarity frequently retrieves $a^*$ or $b$.
   * **Asymmetric Relations:** Parallelograms work reliably for inflectional morphology (*apple* $\to$ *apples*) and geographic relations (*France* $\to$ *Paris*), but fail on hierarchical taxonomic relations (*clothing* $\to$ *shirt*).

### 11.3 Static vs. Dynamic/Contextual Embeddings
* **Static Embeddings (Word2Vec, GloVe, FastText):** Assigns exactly one fixed vector per vocabulary type.
  * **Polysemy Blindness:** Conflates distinct senses of a polysemous word into a single vector (e.g., the river *bank* vs. financial *bank*).
* **Dynamic / Contextual Embeddings (ELMo, BERT, GPT):** Token representations are dynamic functions of the full sentence: $\mathbf{h}_i = f(w_i, w_1, \dots, w_n)$. Disambiguates homonyms dynamically.

### 11.4 Societal Bias & Subspace Debiasing
* Word embeddings geometrically absorb and amplify historical, gender, and racial prejudices present in training text:
  $$\mathbf{v}_{\text{doctor}} - \mathbf{v}_{\text{man}} + \mathbf{v}_{\text{woman}} \approx \mathbf{v}_{\text{nurse}}$$
* **Debiasing Methodology (Bolukbasi et al., 2016):**
  1. Identify the gender direction $\mathbf{g}$ by computing the primary principal component (PCA) across definitional pairs ($\mathbf{v}_{\text{she}} - \mathbf{v}_{\text{he}}$, $\mathbf{v}_{\text{woman}} - \mathbf{v}_{\text{man}}$).
  2. Project gender-neutral words $\mathbf{w}$ onto the orthogonal subspace $\mathbf{g}^\perp$ to eliminate spurious gender projections:
     $$\mathbf{w}_{\text{debiased}} = \mathbf{w} - (\mathbf{w} \cdot \mathbf{g})\mathbf{g}$$
  3. Equalize distances to ensure gender-neutral words are strictly equidistant from gendered counterpart pairs.

---

## 12. Comprehensive Semantic Representation Architecture Matrix

| Architecture | Representation Type | Dimension | Optimization / Objective | Primary NLP Application |
| :--- | :--- | :---: | :--- | :--- |
| **Term-Document (TF-IDF)** | Sparse Count-Based | $|V| \approx 50\text{k}$--$1\text{M}$ | Sub-linear TF-IDF: <br> $(1 + \log_{10} \text{tf})\log_{10}(N/\text{df}_t)$ | Information Retrieval, Search Ranking, Document Categorization |
| **Term-Context (PPMI)** | Sparse Contextual | $|V| \approx 50\text{k}$ | PPMI with $\alpha = 0.75$ smoothing: <br> $\max(\log_2 \frac{P(w, c)}{P(w)P_\alpha(c)}, 0)$ | Computational Linguistics, Word Association Modeling, Feature Extraction |
| **Word2Vec (SGNS)** | Dense Learned | $d \in [100, 300]$ | Binary Cross-Entropy on true context vs.\ $k$ negative noise samples | Pretrained Static Word Vectors, Downstream Neural Text Classification |
| **GloVe (Global Vectors)** | Dense Factorization | $d \in [50, 300]$ | Weighted least-squares regression on log-co-occurrence matrix counts | Fast Global Pretraining, Dense Semantic & Syntactic Analogical Reasoning |

---

*Summary compiled and verified for ENSIA Natural Language Processing (S7 2026–2027) according to publication-grade mathematical standards.*
