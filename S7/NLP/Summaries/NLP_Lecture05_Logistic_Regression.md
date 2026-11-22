# NLP Lecture 5: Logistic Regression & Maximum Entropy in NLP
**Comprehensive Differential Course Summary (ENSIA S7 2026–2027)**  
*Instructor: Prof. Ahmed Guessoum*

---

> ### 📌 Differential Lecture Scope & Foundations
> While fundamental binary logistic regression, the sigmoid curve, and basic cross-entropy loss were thoroughly derived in the **Deep Learning** course, this summary focuses strictly on the **distinct foundations and modifications specific to Natural Language Processing**:
> 1. **Generative vs. Discriminative Classifiers:** Naïve Bayes ($P(d, c) = P(c)P(d \mid c)$) vs. Logistic Regression ($P(c \mid d)$), the Cat vs. Dog collar analogy, and freedom from conditional feature independence assumptions.
> 2. **NLP-Specific Feature Engineering:** Extracting handcrafted linguistic features from raw text (lexicon counts, negation indicators, punctuation cues, subjectivity pronouns, sub-linear logarithmic length scaling), sub-word period disambiguation, and TF-IDF term weighting from Lab 5.
> 3. **Complete Step-by-Step Worked Exam Problem 1:** Movie review sentiment classification forward pass with explicit 6D features $[3, 2, 1, 3, 0, 4.19]$, weights, dot product $z = 0.833$, sigmoid output $\hat{y} = 0.70$, and cross-entropy loss analysis when correct vs. wrong.
> 4. **NLP Optimization & Full Worked Exam Problem 2:** Why Stochastic Gradient Descent (SGD) and mini-batches dominate web-scale text classification; full step-by-step numerical parameter update with learning rate $\eta = 0.1$ and semantic gradient direction analysis.
> 5. **High-Dimensional Text Regularization:** Overfitting driven by massive vocabulary sizes ($|V| \ge 50{,}000$) and higher-order $n$-gram explosion; L2 Ridge (weight shrinkage) vs. L1 Lasso (sparsity and automatic feature selection).
> 6. **Multinomial Logistic Regression (Softmax / MaxEnt):** Multi-class text classification ($K > 2$), class-specific weight vectors $\mathbf{w}_k$, softmax normalization, and multiclass cross-entropy loss.
> 7. **The Model Identifiability Problem & Reference Class Constraint:** Mathematical proof of parameter redundancy under shift vector addition $\mathbf{w}_k + \mathbf{a}$; fixing the "floating" ambiguity by anchoring a reference class $\mathbf{w}_K = \mathbf{0}$; and the resulting non-redundant probability formulas.
> 8. **Comprehensive Naïve Bayes vs. Logistic Regression Comparison:** Complete 6-dimension comparative matrix.

---

## 1. Generative vs. Discriminative Classifiers in NLP

Supervised text classification partitions algorithms into two fundamentally distinct probabilistic modeling paradigms:

### 1.1 Generative Classifiers (e.g., Naïve Bayes)
* **Target Distribution:** Models the **joint probability** $P(d, c) = P(c) \, P(d \mid c)$.
* **Operational Mechanism:** It models how natural language text is generated for each class $c$. By estimating class priors $P(c)$ and class-conditional word likelihoods $P(w \mid c)$, it builds a complete statistical picture of class text.
* **Inference:** Applies Bayes' Rule:
  $$P(c \mid d) = \frac{P(d \mid c) \, P(c)}{P(d)} \propto P(c) \prod_{i=1}^n P(w_i \mid c)$$
* **Linguistic Analogy:** To distinguish cat photos from dog photos, a generative classifier learns what cat whiskers, ears, and eyes look like, and what dog whiskers, ears, and eyes look like. Given an unseen image, it evaluates which species model generated the observed features.

### 1.2 Discriminative Classifiers (e.g., Logistic Regression / MaxEnt)
* **Target Distribution:** Models the **posterior probability** $P(c \mid d)$ directly.
* **Operational Mechanism:** It completely ignores the generative question of how language is produced. Instead, it searches directly for the optimal mathematical **decision boundary** that partitions classes in the input feature space.
* **Linguistic Analogy:** If all dog photos in the training set happen to wear collars, a discriminative classifier notices the collar, ignores whiskers entirely, and uses the collar to separate dogs from cats.

### 1.3 The Core NLP Advantage: Freedom from Independence Assumptions
* **The Naïve Bayes Limitation:** Naïve Bayes strictly assumes that all input features are conditionally independent given the class. If two correlated features occur in a document (e.g., the tokens *"San"* and *"Francisco"*, or a word token and its morphological root), Naïve Bayes multiplies their probabilities, effectively **double-counting** the evidence and producing severely distorted, overconfident probabilities.
* **The Logistic Regression Strength:** Logistic Regression has **no independence assumptions**. Features can freely overlap, strongly correlate, or measure linguistic phenomena at multiple granularities simultaneously (word, stem, syntactic tag, capitalization, prefix). During training, the optimization algorithm automatically coordinates and calibrates their weights jointly.

---

## 2. NLP Feature Engineering: Transforming Text into Vectors

Unlike computer vision where raw pixel intensities provide natural numeric inputs, text documents must be mapped into numeric feature vectors $\mathbf{x} = [x_1, x_2, \dots, x_n]^T \in \mathbb{R}^n$.

### 2.1 Handcrafted Linguistic Features for Sentiment Analysis
In classical NLP, documents are represented by informative handcrafted feature extractors:
* $x_1 = \text{count}(w \in \text{PositiveLexicon})$: Total occurrences of words in an external sentiment dictionary (e.g., VADER, General Inquirer, LIWC).
* $x_2 = \text{count}(w \in \text{NegativeLexicon})$: Total occurrences of negative polarity words.
* $x_3 = \mathbb{I}(\text{"no"} \in d) \in \{0, 1\}$: Binary negation flag indicating the presence of explicit negation markers (*"no"*, *"not"*, *"never"*).
* $x_4 = \text{count}(\text{"!"})$: Punctuation intensity cue indicating strong emotional charge or subjective emphasis.
* $x_5 = \text{count}(\text{1st/2nd person pronouns})$: Subjectivity marker (informal reviews frequently use *I, me, my, you*).
* $x_6 = \ln(\text{document length in words})$: Sub-linear logarithmic scaling prevents long documents from dominating linear dot products purely through word volume.

### 2.2 Sub-Word & Contextual Feature Engineering: The Period Disambiguation Task
Deciding whether a period `.` marks an End-of-Sentence (**EOS**) or an abbreviation (**Not-EOS**):
* $x_1 = 1 \text{ if } \text{Case}(w_i) = \text{Lower}$ (current token lower-cased $\implies$ large positive weight for EOS).
* $x_2 = 1 \text{ if } w_i \in \text{AcronymDict}$ (e.g., *U.S.A.* $\implies$ large negative weight for EOS).
* $x_3 = 1 \text{ if } w_i = \text{"St."} \land \text{Case}(w_{i-1}) = \text{Cap}$ (e.g., *Main St.* $\implies$ negative weight for EOS).

---

## 3. TF-IDF Feature Representation & Damping (Lab 5)

In large-scale bag-of-words text classification, raw token counts cause ubiquitous words (*the, is, and*) to dominate feature weights. **TF-IDF** dampens frequency:

### 3.1 Term Frequency (TF)
$$\text{TF}(w, d) = \frac{\text{count}(w, d)}{\sum_{w' \in d} \text{count}(w', d)}$$
Measures how concentrated word $w$ is within document $d$.

### 3.2 Inverse Document Frequency (IDF)
$$\text{IDF}(w) = \log\left(\frac{N}{\text{DF}(w)}\right)$$
Or the smoothed formulation:
$$\text{IDF}_{\text{smooth}}(w) = \log\left(\frac{1 + N}{1 + \text{DF}(w)}\right) + 1$$
Where $N$ is the total number of documents in the corpus, and $\text{DF}(w)$ is the number of documents containing word $w$.

### 3.3 Compound TF-IDF Score
$$\text{TF-IDF}(w, d) = \text{TF}(w, d) \times \text{IDF}(w)$$
A word receives a high TF-IDF score only if it occurs frequently within document $d$ but rarely across the broader corpus.

---

## 4. Binary Logistic Regression in NLP: Formulation & Log-Odds

For binary classification ($y \in \{0, 1\}$, e.g., positive vs. negative sentiment), the model parameterizes conditional probabilities via the **sigmoid** function:

$$P(y = 1 \mid x) = \sigma(z) = \frac{1}{1 + e^{-z}} = \frac{1}{1 + e^{-(\mathbf{w}^T \mathbf{x} + b)}}$$
$$P(y = 0 \mid x) = 1 - P(y = 1 \mid x) = \frac{e^{-z}}{1 + e^{-z}} = \frac{1}{1 + e^z}$$

### 4.1 The Log-Odds (Logit) Formulation
The linear score $z$ equals the natural logarithm of the odds ratio:

$$\ln\left( \frac{P(y = 1 \mid x)}{1 - P(y = 1 \mid x)} \right) = \ln\left( \frac{\sigma(z)}{1 - \sigma(z)} \right) = z = \mathbf{w}^T \mathbf{x} + b = \sum_{j=1}^n w_j x_j + b$$

### 4.2 Decision Boundary
The classifier predicts $\hat{y} = 1$ if $P(y = 1 \mid x) \ge 0.5$, which corresponds exactly to:
$$\mathbf{w}^T \mathbf{x} + b \ge 0$$

### 4.3 Binary Cross-Entropy Loss for a Single Document
$$\mathcal{L}_{\text{CE}}(\hat{y}, y) = -\big[ y \ln \hat{y} + (1 - y) \ln(1 - \hat{y}) \big] = \begin{cases} -\ln \hat{y} & \text{if } y = 1 \\ -\ln(1 - \hat{y}) & \text{if } y = 0 \end{cases}$$

---

## 5. Complete Step-by-Step Worked Exam Problem: Sentiment Forward Pass & Loss

This problem traces the movie review sentiment classification example from the lecture slides (Slides 23–28 & 37–40).

### Document Text ($d$)
> *"It's hokey. There are virtually no surprises, and the writing is second-rate. So why was it so enjoyable? For one thing, the cast is great. Another nice touch is the music. I was overcome with the urge to get off the couch and start dancing. It sucked me in, and it'll do the same to you."*

---

### Step 1: Extracted Feature Vector $\mathbf{x} \in \mathbb{R}^6$
* $x_1 = 3$ (count of positive words: *"great"*, *"enjoyable"*, *"nice"*).
* $x_2 = 2$ (count of negative words: *"hokey"*, *"second-rate"*).
* $x_3 = 1$ (negation indicator: presence of the token *"no"*).
* $x_4 = 3$ (punctuation count: 3 exclamation marks in expanded review text).
* $x_5 = 0$ (count of specific pronominal subjectivity cues).
* $x_6 = \ln(66) \approx 4.19$ (logarithmic total word length of the review: 66 words).

$$\mathbf{x} = [3,\, 2,\, 1,\, 3,\, 0,\, 4.19]^T$$

---

### Step 2: Learned Parameter Weights & Bias
$$\mathbf{w} = [2.5,\, -5.0,\, -1.2,\, 0.5,\, 2.0,\, 0.7]^T, \qquad b = 0.1$$

---

### Step 3: Linear Score ($z$) Dot Product
$$\begin{aligned}
z = \mathbf{w}^T \mathbf{x} + b &= (2.5 \times 3) + (-5.0 \times 2) + (-1.2 \times 1) + (0.5 \times 3) + (2.0 \times 0) + (0.7 \times 4.19) + 0.1 \\
&= 7.5 - 10.0 - 1.2 + 1.5 + 0.0 + 2.933 + 0.1 \\
&= \mathbf{0.833}
\end{aligned}$$

---

### Step 4: Sigmoid Activation & Class Posterior Probabilities
$$P(+ \mid x) = \sigma(0.833) = \frac{1}{1 + e^{-0.833}} = \frac{1}{1 + 0.4347} = \mathbf{0.70}$$
$$P(- \mid x) = 1 - 0.70 = \mathbf{0.30}$$

**Classification Decision:** Since $P(+ \mid x) = 0.70 \ge 0.50$ (or $z = 0.833 > 0$), the model predicts **Positive (+)**.

---

### Step 5: Cross-Entropy Loss Evaluation (Model Behavior Analysis)
* **Case A (Ground truth is $y = 1$ --- Model is Correct):**
  $$\mathcal{L}_{\text{CE}} = -\ln P(+ \mid x) = -\ln(0.70) \approx \mathbf{0.36}$$
  *(Small penalty; model is rewarded for confident, correct prediction).*
* **Case B (Ground truth is $y = 0$ --- Model is Wrong):**
  $$\mathcal{L}_{\text{CE}} = -\ln P(- \mid x) = -\ln(0.30) \approx \mathbf{1.20}$$
  *(Severe penalty; $\mathbf{3.33\times}$ larger loss punishing incorrect prediction).*

---

## 6. Model Interpretability & Feature Attribution in Text NLP

A major advantage of Logistic Regression over deep neural networks is **direct interpretability**:
* Each weight $w_j$ represents the increase in log-odds of the positive class per unit increase in feature $x_j$, holding all other features fixed.
* $w_j > 0$ pushes the document towards the positive class (e.g., $w_{\text{"awesome"}} = +10$, $w_{\text{"great"}} = +2.5$).
* $w_j < 0$ pushes the document towards the negative class (e.g., $w_{\text{"abysmal"}} = -10$, $w_{\text{"mediocre"}} = -2.0$).
* Magnitudes reflect linguistic diagnostic power: $|w_j|$ quantifies how strongly that word or feature shifts the prediction.

---

## 7. Optimization for NLP: Batch vs. Mini-Batch vs. SGD

In NLP, corpora routinely contain hundreds of thousands or millions of documents. Optimization strategies balance convergence stability and speed:
* **Batch Gradient Descent:** Computes gradients over the entire training set $m$. Highly smooth convergence, but computationally prohibitive when $m \ge 10^6$ text documents (requires a complete dataset pass per parameter step).
* **Stochastic Gradient Descent (SGD):** Updates weights after observing a **single document** $(x^{(i)}, y^{(i)})$. Fast online updates, handles streaming text, and noisy trajectory helps escape shallow local minima and flat plateaus.
* **Mini-Batch Gradient Descent:** Groups $B$ examples (e.g., $B \in \{512, 1024\}$). Combines SGD's speed with GPU SIMD vectorization.

---

## 8. Complete Step-by-Step Worked Exam Problem: SGD Parameter Update

This problem traces the exact numerical SGD step from the lecture slides (Slides 56–58).

### Setup
Perform **one step** of Stochastic Gradient Descent on a single training document with true class $y = 1$ (Positive).
* Input features: $x_1 = 3$ (count of positive words), $x_2 = 2$ (count of negative words).
* Initial parameters ($\theta^{(0)}$): $w_1^{(0)} = 0, \quad w_2^{(0)} = 0, \quad b^{(0)} = 0$.
* Learning rate hyperparameter: $\eta = 0.1$.

---

### Step 1: Forward Prediction & Error
$$z = w_1 x_1 + w_2 x_2 + b = (0)(3) + (0)(2) + 0 = 0 \implies \hat{y} = \sigma(0) = \mathbf{0.5}$$
$$\text{Error Term: } (\hat{y} - y) = 0.5 - 1.0 = \mathbf{-0.5}$$

---

### Step 2: Loss Gradient Vector ($\nabla_\theta \mathcal{L}$)
The partial derivatives of binary cross-entropy loss are:
$$\frac{\partial \mathcal{L}}{\partial w_j} = (\hat{y} - y) x_j, \qquad \frac{\partial \mathcal{L}}{\partial b} = (\hat{y} - y)$$

Evaluating gradients for our training instance:
$$\frac{\partial \mathcal{L}}{\partial w_1} = (-0.5) \times 3 = \mathbf{-1.5}$$
$$\frac{\partial \mathcal{L}}{\partial w_2} = (-0.5) \times 2 = \mathbf{-1.0}$$
$$\frac{\partial \mathcal{L}}{\partial b} = \mathbf{-0.5}$$
$$\implies \nabla_\theta \mathcal{L} = \big[ -1.5,\; -1.0,\; -0.5 \big]^T$$

---

### Step 3: Steepest Descent Parameter Updates ($\theta^{(1)} = \theta^{(0)} - \eta \nabla_\theta \mathcal{L}$)
$$\begin{aligned}
w_1^{(1)} &= w_1^{(0)} - \eta \frac{\partial \mathcal{L}}{\partial w_1} = 0 - (0.1)(-1.5) = 0 + 0.15 = \mathbf{+0.15} \\
w_2^{(1)} &= w_2^{(0)} - \eta \frac{\partial \mathcal{L}}{\partial w_2} = 0 - (0.1)(-1.0) = 0 + 0.10 = \mathbf{+0.10} \\
b^{(1)}   &= b^{(0)} - \eta \frac{\partial \mathcal{L}}{\partial b} = 0 - (0.1)(-0.5) = 0 + 0.05 = \mathbf{+0.05}
\end{aligned}$$

---

### Critical Exam Takeaway: Why Did Negative Feature Weight $w_2$ Increase?
$w_2$ increased from $0 \to +0.10$ because this single document was labeled **positive** despite containing negative words ($x_2 = 2$). The gradient descent update credits all active features in positive documents. However, across the full corpus, negative documents ($y = 0 \implies \hat{y} - y > 0$) will encounter negative gradients, driving $w_2$ into negative territory.

---

## 9. Regularization in High-Dimensional Text NLP: L1 vs. L2

In NLP, vocabulary spaces are massive ($|V| \ge 50{,}000$; bigrams and trigrams reach millions of features). An unregularized model easily overfits by assigning huge weights to rare idiosyncratic words that happened to appear in one class (achieving 100% train accuracy but failing on test data).

### Regularized Objective
$$J(\theta) = \mathcal{L}_{\text{CE}}(\theta) + \alpha R(\theta)$$

### 9.1 L2 Regularization (Ridge Regression)
Penalizes the Euclidean norm (sum of squared weights):
$$R_{\text{L2}}(\mathbf{w}) = \|\mathbf{w}\|_2^2 = \sum_{j=1}^n w_j^2, \qquad \nabla R_{\text{L2}} = 2\mathbf{w}$$
* Easy to optimize due to smooth, continuous derivative.
* Acts as **weight decay**: shrinks all weights towards zero, preferring many small weights across the vocabulary.

### 9.2 L1 Regularization (Lasso Regression)
Penalizes the Manhattan norm (sum of absolute weights):
$$R_{\text{L1}}(\mathbf{w}) = \|\mathbf{w}\|_1 = \sum_{j=1}^n |w_j|, \qquad \frac{\partial R_{\text{L1}}}{\partial w_j} = \text{sign}(w_j)$$
* Derivative is non-differentiable at $w_j = 0$.
* Drives insignificant weights to **exactly zero**, producing **sparse weight vectors**.
* **Major NLP Advantage:** Serves as built-in **feature selection**, discarding thousands of irrelevant vocabulary words.

---

## 10. Multinomial Logistic Regression (Softmax Regression / MaxEnt)

When text classification involves $K > 2$ classes (e.g., sentiment $\{+, -, 0\}$, topic classification, POS tagging), binary LR generalizes to **Multinomial Logistic Regression**.

### 10.1 Class Weight Vectors
The model maintains a separate weight vector $\mathbf{w}_k \in \mathbb{R}^n$ and bias $b_k \in \mathbb{R}$ for each class $k \in \{1, \dots, K\}$.

### 10.2 The Softmax Activation Function
Normalizes unconstrained real-valued scores $z_k = \mathbf{w}_k^T \mathbf{x} + b_k$ into a valid probability distribution:

$$P(y = k \mid x) = \frac{\exp(\mathbf{w}_k^T \mathbf{x} + b_k)}{\sum_{j=1}^K \exp(\mathbf{w}_j^T \mathbf{x} + b_j)}, \qquad \text{where } \sum_{k=1}^K P(y = k \mid x) = 1, \quad P(y = k \mid x) \in (0, 1)$$

### 10.3 Categorical Cross-Entropy Loss
For one-hot ground truth vector $\mathbf{y}$ where $y_k = 1$ for the true class $c$ and $0$ otherwise:

$$\mathcal{L}_{\text{Multi}}(\hat{\mathbf{y}}, \mathbf{y}) = -\sum_{k=1}^K y_k \ln \hat{y}_k = -\ln P(y = c \mid x)$$

### 10.4 Softmax Gradient
$$\frac{\partial \mathcal{L}}{\partial \mathbf{w}_k} = (\hat{y}_k - y_k) \mathbf{x}$$
Remarkably identical in form to binary logistic regression!

---

## 11. The Model Identifiability Problem & Reference Class Constraint

### 11.1 Mathematical Definition of Model Identifiability (Slides 79–83)
A statistical model parameterized by $\theta$ is **identifiable** if distinct parameter values strictly generate distinct probability distributions:

$$P(y \mid x;\, \theta_1) = P(y \mid x;\, \theta_2) \implies \theta_1 = \theta_2$$

If a model is **non-identifiable**, multiple different parameter sets yield the exact same output probabilities.

---

### 11.2 The Parameter Redundancy Proof (Why Standard Softmax is Non-Identifiable)
Suppose we add an arbitrary constant vector $\mathbf{a} \in \mathbb{R}^n$ to all class weight vectors: $\mathbf{w}_k' = \mathbf{w}_k + \mathbf{a}$ for all $k \in \{1, \dots, K\}$.

$$\begin{aligned}
P(y = k \mid x;\, \mathbf{w}') &= \frac{\exp\big((\mathbf{w}_k + \mathbf{a})^T \mathbf{x}\big)}{\sum_{j=1}^K \exp\big((\mathbf{w}_j + \mathbf{a})^T \mathbf{x}\big)} = \frac{\exp(\mathbf{w}_k^T \mathbf{x}) \cdot \exp(\mathbf{a}^T \mathbf{x})}{\sum_{j=1}^K \big[ \exp(\mathbf{w}_j^T \mathbf{x}) \cdot \exp(\mathbf{a}^T \mathbf{x}) \big]} \\
&= \frac{\exp(\mathbf{w}_k^T \mathbf{x}) \cdot \exp(\mathbf{a}^T \mathbf{x})}{\left[\sum_{j=1}^K \exp(\mathbf{w}_j^T \mathbf{x})\right] \cdot \exp(\mathbf{a}^T \mathbf{x})} = \frac{\exp(\mathbf{w}_k^T \mathbf{x})}{\sum_{j=1}^K \exp(\mathbf{w}_j^T \mathbf{x})} = P(y = k \mid x;\, \mathbf{w})
\end{aligned}$$

The shift factor $\exp(\mathbf{a}^T \mathbf{x})$ cancels completely from numerator and denominator!

* **The Problem:** The unconstrained system is "floating". Infinitely many parameter configurations produce identical predictions, making it impossible to determine a unique optimal weight vector $\theta^*$ during optimization.

---

### 11.3 Fixing Identifiability via the Reference Class Constraint
To remove the degree-of-freedom redundancy, we pin one class as the **reference class** (baseline category, typically class $K$) and fix its parameters to zero:

$$\mathbf{w}_{\text{ref}} = \mathbf{w}_K = \mathbf{0}, \qquad b_K = 0$$

### 11.4 Resulting Non-Redundant Identifiable Probabilities
* **For non-reference classes $c \in \{1, \dots, K-1\}$:**
  $$P(y = c \mid x) = \frac{\exp(\mathbf{w}_c^T \mathbf{x} + b_c)}{1 + \sum_{j=1}^{K-1} \exp(\mathbf{w}_j^T \mathbf{x} + b_j)}$$
* **For the reference class $K$:**
  $$P(y = K \mid x) = \frac{1}{1 + \sum_{j=1}^{K-1} \exp(\mathbf{w}_j^T \mathbf{x} + b_j)}$$

### 11.5 Direct Link to Binary Logistic Regression
For $K = 2$, setting $\mathbf{w}_2 = \mathbf{0}$ yields:
$$P(y = 1 \mid x) = \frac{e^{\mathbf{w}_1^T \mathbf{x}}}{1 + e^{\mathbf{w}_1^T \mathbf{x}}} = \sigma(\mathbf{w}_1^T \mathbf{x}), \qquad P(y = 2 \mid x) = \frac{1}{1 + e^{\mathbf{w}_1^T \mathbf{x}}} = 1 - \sigma(\mathbf{w}_1^T \mathbf{x})$$
Binary Logistic Regression is simply multinomial logistic regression with one reference class!

---

## 12. Comprehensive Comparison: Naïve Bayes vs. Logistic Regression

| Dimension | Naïve Bayes (Generative) | Logistic Regression (Discriminative) |
| :--- | :--- | :--- |
| **Modeling Target** | Joint distribution $P(d, c) = P(c)P(d \mid c)$ | Posterior distribution $P(c \mid d)$ directly |
| **Independence Assumption** | Strict conditional independence: $P(d\mid c) = \prod P(w_i\mid c)$ | **None**. Features can correlate, overlap, and interact |
| **Correlated Features** | Overcounts evidence, yielding extreme/distorted probabilities | Calibrates distributed weights across correlated features |
| **Optimization / Training** | Closed-form counting (one-pass MLE); ultra-fast | Iterative gradient descent (SGD/Mini-batch); slower |
| **Data Regime Performance** | Converges quickly to asymptotic error on **small datasets** | Achieves **lower asymptotic error** on **large datasets** |
| **Interpretability** | Word likelihood ratio $\frac{P(w \mid c)}{P(w \mid c')}$ | Linear feature weights $w_j$ directly indicate feature log-odds |
