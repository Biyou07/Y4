# Lecture 6: Deep Learning — Neural Networks 1 (NN 1)

**Course:** Deep Learning (S.-A. Berrani, ENSIA 2026–2027)  
**Topic:** Feedforward Neural Network Convention, Activation Functions, Hyperparameters, Data Splitting, Feature Normalization, Bias & Variance, and Regularization ($L_1$ vs. $L_2$).

---

## 1. Feedforward Neural Network Convention & Matrix Representation

A multilayer **Feedforward Neural Network (FF-NN)** maps an input feature vector $x \in \mathbb{R}^{n_x}$ through $L-1$ hidden layers to compute an output prediction $\hat{y} = a^{[L]}$.

```
[Input Layer l=0]       [Hidden Layer l=1]       [Hidden Layer l=2]       ...       [Hidden Layer l=L-1]       [Output Layer l=L]
      x₁ ───────( W[1], b[1] )──────> a₁[1] ───( W[2], b[2] )───> a₁[2] ───────...───────> a₁[L-1] ───( W[L], b[L] )───> [ ŷ = a[L] ]
      x₂ ────────────────────────────> a₂[1] ────────────────────> a₂[2] ───────...───────> a₂[L-1] ────────────────────┘
       ⋮                               ⋮                           ⋮                        ⋮
      x_n ───────────────────────────> a_n1[1] ──────────────────> a_n2[2] ────...───────> a_n(L-1)[L-1]
   x = a[0]                       a[1]                     a[2]                          a[L-1]                      ŷ = a[L]
```

### 1.1 Layer Indexing and Notations
* **$L$**: Total number of layers in the network (convention: input layer is layer $0$; hidden layers are $l = 1, \dots, L-1$; output layer is layer $L$).
* **$n^{[l]}$**: Number of neurons (units) in layer $l$.
  * $n^{[0]} = n_x$ (number of input features).
  * $n^{[L]}$ (number of output neurons; $n^{[L]} = 1$ for binary classification).
* **$a^{[l]}$**: Activation vector produced by layer $l$.
  * Input layer: $a^{[0]} = x \in \mathbb{R}^{n_x}$.
  * Hidden layers: $a^{[l]} = g^{[l]}(z^{[l]}) \in \mathbb{R}^{n^{[l]} \times 1}$.
  * Output layer: $a^{[L]} = \hat{y} \in \mathbb{R}^{n^{[L]} \times 1}$.
* **$W^{[l]}$**: Weight matrix connecting layer $l-1$ to layer $l$.
* **$b^{[l]}$**: Bias vector for layer $l$.

---

### 1.2 Mathematical Dimensions & Shapes

#### Single Training Instance:
* Input vector: $x = a^{[0]} \in \mathbb{R}^{n^{[0]} \times 1} \quad (n^{[0]} = n_x)$.
* Linear logit: $z^{[l]} \in \mathbb{R}^{n^{[l]} \times 1}$.
* Activation vector: $a^{[l]} \in \mathbb{R}^{n^{[l]} \times 1}$.
* **Weight matrix:** $W^{[l]} \in \mathbb{R}^{n^{[l]} \times n^{[l-1]}}$.
* **Bias vector:** $b^{[l]} \in \mathbb{R}^{n^{[l]} \times 1}$.

#### Vectorized Batch of $m$ Training Examples:
Stacking $m$ sample vectors as columns creates design matrices:
* $X = A^{[0]} = \begin{bmatrix} \vert & \vert & & \vert \\ x^{(1)} & x^{(2)} & \cdots & x^{(m)} \\ \vert & \vert & & \vert \end{bmatrix} \in \mathbb{R}^{n_x \times m}$
* $Z^{[l]} = W^{[l]} A^{[l-1]} + b^{[l]} \in \mathbb{R}^{n^{[l]} \times m}$ (where $b^{[l]}$ is broadcasted across all $m$ columns).
* $A^{[l]} = g^{[l]}\big(Z^{[l]}\big) \in \mathbb{R}^{n^{[l]} \times m}$.
* Output: $A^{[L]} = \hat{Y} \in \mathbb{R}^{n^{[L]} \times m}$.

---

### 1.3 Internal Ordering of the Weight Matrix $W^{[l]}$

In standard deep learning convention (Prof. Berrani / Andrew Ng framework), the weight matrix connecting layer $l-1$ ($n^{[l-1]}$ neurons) to layer $l$ ($n^{[l]}$ neurons) has shape:
$$\text{Shape}\big(W^{[l]}\big) = \big(n^{[l]}, \; n^{[l-1]}\big)$$

$$W^{[l]} = \begin{bmatrix} \text{---} & (w_1^{[l]})^T & \text{---} \\ \text{---} & (w_2^{[l]})^T & \text{---} \\ & \vdots & \\ \text{---} & (w_{n^{[l]}}^{[l]})^T & \text{---} \end{bmatrix} = \begin{bmatrix} w_{1, 1}^{[l]} & w_{1, 2}^{[l]} & \cdots & w_{1, n^{[l-1]}}^{[l]} \\ w_{2, 1}^{[l]} & w_{2, 2}^{[l]} & \cdots & w_{2, n^{[l-1]}}^{[l]} \\ \vdots & \vdots & \ddots & \vdots \\ w_{n^{[l]}, 1}^{[l]} & w_{n^{[l]}, 2}^{[l]} & \cdots & w_{n^{[l]}, n^{[l-1]}}^{[l]} \end{bmatrix}$$

#### Row Vectors vs. Column Vectors Breakdown:
1. **Row Vectors ($i$-th Row of $W^{[l]}$):**  
   The $i$-th row vector $(w_i^{[l]})^T \in \mathbb{R}^{1 \times n^{[l-1]}}$ represents the weights coming from **all different incoming inputs** $j \in \{1, 2, \dots, n^{[l-1]}\}$ into that **same destination output neuron $i$** in layer $l$:
   $$z_i^{[l]} = \sum_{j=1}^{n^{[l-1]}} W_{i, j}^{[l]} \, a_j^{[l-1]} + b_i^{[l]} = (w_i^{[l]})^T a^{[l-1]} + b_i^{[l]}$$
2. **Column Vectors ($j$-th Column of $W^{[l]}$):**  
   The $j$-th column vector $[W^{[l]}]_{:, j} \in \mathbb{R}^{n^{[l]} \times 1}$ represents the weights emanating from the **same single input unit $j$** in layer $l-1$ fanning out into **all different output destination neurons** $i \in \{1, 2, \dots, n^{[l]}\}$ of layer $l$:
   $$[W^{[l]}]_{:, j} = \begin{bmatrix} w_{1, j}^{[l]} \\ w_{2, j}^{[l]} \\ \vdots \\ w_{n^{[l]}, j}^{[l]} \end{bmatrix}$$
3. **Note on Transposed Conventions:** In alternative software libraries (e.g., PyTorch linear layers using $x A^T + b$ or transposed row vectors), weights are stored as $(n^{[l-1]} \times n^{[l]})$, swapping the row/column interpretations. In standard course notation, $W^{[l]}$ is strictly $(n^{[l]} \times n^{[l-1]})$.

---

## 2. Activation Functions & The Necessity of Non-Linearity

Activation functions transform linear logits $z^{[l]}$ into non-linear activations $a^{[l]}$, enabling neural networks to learn arbitrary, complex decision surfaces.

| Activation Function | Formula $g(z)$ | Output Range | Derivative $g'(z)$ | Key Properties & When to Use |
| :--- | :--- | :---: | :--- | :--- |
| **Sigmoid** | $g(z) = \dfrac{1}{1 + e^{-z}}$ | $(0, 1)$ | $g(z)(1 - g(z))$ | Output layer for binary classification; severe vanishing gradient for $\|z\| > 4$. |
| **Tanh** | $g(z) = \dfrac{e^z - e^{-z}}{e^z + e^{-z}}$ | $(-1, 1)$ | $1 - g(z)^2$ | **Zero-centered** ($\mu \approx 0$); speeds hidden layer learning; saturates for $\|z\| > 3$. |
| **ReLU** | $g(z) = \max(0, z)$ | $[0, +\infty)$ | $\begin{cases} 1 & z > 0 \\ 0 & z < 0 \end{cases}$ | **De facto standard for hidden layers**; non-saturating for $z > 0$, fast; dying ReLU risk. |
| **Leaky ReLU** | $g(z) = \max(0.01z, z)$ | $(-\infty, +\infty)$ | $\begin{cases} 1 & z > 0 \\ 0.01 & z < 0 \end{cases}$ | Prevents dead neurons by ensuring a small gradient ($0.01$) when $z \le 0$. |

---

### 2.1 Why Do We Need Non-Linearity?
* **Real-world complexity:** Physical systems, image pixels, and speech patterns contain non-linear, intricately folded manifolds that cannot be separated by hyperplanes.
* **Varying Slope:** A linear function has a single constant slope everywhere. A non-linear function has a **continuously changing slope**, allowing the network to be selectively sensitive to specific local input regions while insensitive to others.

---

### 2.2 Formal Proof: An $L$-Layer Linear Neural Network is Pointless

> **Theorem:** If all activation functions are linear, i.e., $g^{[l]}(z) = z$ for all $l \in \{1, \dots, L\}$, then an arbitrary $L$-layer deep neural network collapses into a simple linear affine function of its inputs.

#### Step-by-Step Derivation:
* **Layer 1:**
  $$a^{[1]} = z^{[1]} = W^{[1]} x + b^{[1]}$$
* **Layer 2:**
  $$a^{[2]} = z^{[2]} = W^{[2]} a^{[1]} + b^{[2]} = W^{[2]} \big(W^{[1]} x + b^{[1]}\big) + b^{[2]}$$
  $$a^{[2]} = \underbrace{\big(W^{[2]} W^{[1]}\big)}_{W'} x + \underbrace{\big(W^{[2]} b^{[1]} + b^{[2]}\big)}_{b'} = W' x + b'$$
* **Layer 3:**
  $$a^{[3]} = z^{[3]} = W^{[3]} a^{[2]} + b^{[3]} = W^{[3]} (W' x + b') + b^{[3]} = W'' x + b''$$
* **General $L$-Layer Induction:**
  $$a^{[L]} = \widetilde{W} x + \tilde{b} \qquad \text{where } \widetilde{W} = \prod_{l=L}^1 W^{[l]} \in \mathbb{R}^{n^{[L]} \times n_x}$$

**Conclusion:** The composition of multiple linear transformations is itself strictly linear. Regardless of whether the network has 2 layers or 100 layers, or millions of hidden neurons, a purely linear network cannot compute anything that cannot already be computed by basic **linear regression** (or 1-layer logistic regression if the final activation is sigmoid). All intermediate hidden layers are completely redundant.

---

## 3. Parameters vs. Hyperparameters

* **Trainable Parameters:** Internal variables adjusted automatically by the optimization algorithm (gradient descent / backpropagation):
  $$\mathcal{P} = \{W^{[1]}, b^{[1]}, W^{[2]}, b^{[2]}, \dots, W^{[L]}, b^{[L]}\}$$
* **Hyperparameters:** Configuration knobs chosen and tuned by the machine learning engineer to control the learning process:
  1. Learning rate $\alpha$
  2. Number of hidden layers $L$
  3. Number of hidden neurons in each layer $n^{[l]}$
  4. Number of training iterations / epochs
  5. Choice of activation functions $g^{[l]}$
  6. Regularization parameter $\lambda$
  7. Mini-batch size, momentum, optimizer algorithm.

### The Empirical Iterative Process
Deep learning model design is fundamentally an experimental, cyclical search:
$$\boxed{\text{\bfseries Idea}} \;\longrightarrow\; \boxed{\text{\bfseries Code / Architecture}} \;\longrightarrow\; \boxed{\text{\bfseries Experiment}} \;\longrightarrow\; \boxed{\text{\bfseries Tune Hyperparameters}}$$

---

## 4. Dataset Splitting Strategy & Cross-Validation

### 4.1 Train, Dev (Validation), and Test Sets
1. **Training Set:** Used directly by backpropagation to compute gradients and optimize parameters $(W, b)$.
2. **Development (Dev / Validation) Set:** Used to evaluate candidate architectures, tune hyperparameters ($\alpha, \lambda, L, n^{[l]}$), and diagnose bias/variance.
3. **Test Set:** Evaluated **strictly once** at the very end to provide an unbiased estimate of the final model's real-world generalization performance.

---

### 4.2 Maximizing the Training Set in Modern Deep Learning
* **Classical ML Regime ($m \le 10{,}000$):** Data was scarce. Common rule-of-thumb splits were:
  * $70\% / 30\%$ (Train / Test)
  * $60\% / 20\% / 20\%$ (Train / Dev / Test)
* **Modern Big Data / Deep Learning Regime ($m \ge 1{,}000{,}000$):** Deep neural networks have millions of parameters and are **data-hungry**. Therefore, our primary objective is to **maximize the training set**.
* **Sufficiency of Absolute Sample Size:** Dev and Test sets only need to be large enough in *absolute sample count* to provide statistically reliable error estimates (e.g., $10{,}000$ samples are more than enough to detect a subtle difference between $1.1\%$ and $1.2\%$ error).
* **Representative Modern Split for $1{,}000{,}000$ examples:**
  $$\mathbf{98\% \text{ Train}} \ (980{,}000 \text{ samples}) \quad\Big|\quad \mathbf{1\% \text{ Dev}} \ (10{,}000 \text{ samples}) \quad\Big|\quad \mathbf{1\% \text{ Test}} \ (10{,}000 \text{ samples})$$

#### Critical Requirement: Identical Distribution
> **Rule:** The Dev and Test sets **must come from the exact same data distribution** as the target application and training set. If validation data is drawn from a different distribution than deployment data, error metrics become uninformative.

---

### 4.3 Cross-Validation Procedure
* **When to Use:** When total available data is small ($m < 10{,}000$), setting aside a separate dev set sacrifices precious training examples.
* **$k$-Fold Cross-Validation Mechanics:**
  1. Partition available training data randomly into $k$ equal-sized folds (e.g., $k=5$ or $k=10$).
  2. In round $i \in \{1, \dots, k\}$, train on the remaining $k-1$ folds and validate on fold $i$.
  3. Average the validation performance across all $k$ rounds.
* **Deep Learning Context:** For large datasets ($m \ge 10^5$), standard single Dev/Test splits are universally preferred because training a deep network $k$ separate times is computationally prohibitive.

---

## 5. Input Feature Normalization

Feature normalization scales raw input features into a zero-centered, unit-variance coordinate system through two sequential steps:

### 5.1 Two-Step Normalization Procedure
1. **Step 1: Zero-Mean Centering:** Compute empirical coordinate-wise mean vector $\mu \in \mathbb{R}^{n_x}$ and center:
   $$\mu = \frac{1}{m} \sum_{i=1}^m x^{(i)} \qquad \Longrightarrow \qquad x := x - \mu$$
2. **Step 2: Variance Normalization:** Compute empirical variance vector $\sigma^2 \in \mathbb{R}^{n_x}$ and scale:
   $$\sigma^2 = \frac{1}{m} \sum_{i=1}^m \big(x^{(i)}\big)^2 \qquad \Longrightarrow \qquad x := \frac{x}{\sigma} \qquad (\text{with } \sigma = \sqrt{\sigma^2 + \epsilon})$$

---

### 5.2 Why Do We Normalize? (Geometric & Optimization Explanation)
* **Unnormalized Feature Space:** If input features span vastly different numerical ranges (e.g., $x_1 \in [0, 1]$ and $x_2 \in [1000, 100000]$), weight parameters $w_1$ and $w_2$ experience drastically different sensitivities. The cost function $J(w, b)$ forms an **elongated, highly eccentric elliptical valley** (an ill-conditioned Hessian matrix with high condition number $\kappa = \lambda_{\max}/\lambda_{\min}$).
* **Oscillatory Zig-zag Path:** In an elongated cost surface, gradient descent oscillates violently back and forth across the steep ravine while making agonizingly slow progress along the flat valley towards the minimum. To prevent divergence, the learning rate $\alpha$ must be set extremely small.
* **Normalized Feature Space:** After zero-mean and unit-variance normalization, cost contours become **spherical (isotropic)**. The gradient vector points directly toward the global optimum, eliminating oscillations and permitting a much larger learning rate $\alpha$, dramatically accelerating convergence.
* **Critical Rule to Prevent Data Leakage:**
  > Normalization parameters $(\mu, \sigma)$ computed on the **Train set** must be stored and reused to normalize Dev and Test sets. You must **never** compute new mean or variance statistics on dev or test sets!

---

## 6. Bias and Variance: Mathematical Formulation & Diagnostics

### 6.1 Formal Mathematical Definitions (Error Decomposition)
For an estimation problem with target $y = f(x) + \epsilon$ where $\mathbb{E}[\epsilon] = 0$ and $\text{Var}(\epsilon) = \sigma_\epsilon^2$, the expected generalization error decomposes cleanly into:

$$\mathbb{E}_{\mathcal{D}}\big[(y - \hat{f}(x))^2\big] = \underbrace{\Big(\mathbb{E}_{\mathcal{D}}[\hat{f}(x)] - f(x)\Big)^2}_{\textbf{Bias}^2} + \underbrace{\mathbb{E}_{\mathcal{D}}\Big[\big(\hat{f}(x) - \mathbb{E}_{\mathcal{D}}[\hat{f}(x)]\big)^2\Big]}_{\textbf{Variance}} + \underbrace{\sigma_\epsilon^2}_{\textbf{Irreducible Error}}$$

* **Bias:** $\text{Bias}[\hat{f}(x)] = \mathbb{E}[\hat{f}(x)] - f(x)$  
  Measures how much the **average of all predictions** across different partitions / training subsets of the data $\mathcal{D}$ differs from the **actual ground truth** $f(x)$. It captures systematic error stemming from overly simplistic model assumptions.  
  $\implies$ **High Bias $\iff$ Underfitting** (the model family lacks the expressive capacity to fit the true underlying pattern).
* **Variance:** $\text{Var}[\hat{f}(x)] = \mathbb{E}\left[\left(\hat{f}(x) - \mathbb{E}[\hat{f}(x)]\right)^2\right]$  
  Measures the **variance (dispersion)** between all the different individual predictions across different data partitions around their average prediction $\mathbb{E}[\hat{f}(x)]$. It captures the model's sensitivity to random sample noise and fluctuations in the training data.  
  $\implies$ **High Variance $\iff$ Overfitting** (the model memorizes noise and quirks of a specific sample, failing to generalize).
* **Irreducible Error ($\sigma_\epsilon^2$):** Lower bound on error caused by inherent noise in the data generating process (Bayes Optimal Error).

---

### 6.2 Diagnostic Scenarios & Human-Level Baseline

Generalization diagnosis compares **Train Set Error** against **Dev Set Error** relative to the **Human-Level Error (Bayes Baseline)**:

| Metric / Scenario | Case A | Case B | Case C | Case D |
| :--- | :---: | :---: | :---: | :---: |
| **Train Set Error** | $0.5\%$ | $18\%$ | $18\%$ | $2\%$ |
| **Dev Set Error** | $10\%$ | $19\%$ | $35\%$ | $3\%$ |
| **Diagnosis (Human Error $\approx 0\%$):** | **High Variance** (Overfitting) | **High Bias** (Underfitting) | **High Bias & High Variance** | **Low Bias & Low Variance** (Good fit) |
| **Diagnosis (Human Error $\approx 16\%$):** | **High Variance** | **Low Bias & Low Variance** | **High Bias** ($30\%$ vs $32\%$) | **Low Bias & Low Variance** |

* **Avoidable Bias:** Gap between Human-level / Bayes error and Train error.
* **Variance (Generalization Gap):** Gap between Train error and Dev error.

---

### 6.3 Systematic Diagnostic Workflow: What To Do

```
                       [ 1. High Bias? ]
                     (Train error high?)
                           /       \
                    YES   /         \   NO
                         v           v
           [ Remedies for Bias: ]  [ 2. High Variance? ]
           - Bigger model          (Dev error >> Train?)
             (more layers/units)         /       \
           - Train longer         YES   /         \   NO
           - Better optimizer          v           v
           - New NN architecture   [ Remedies for Var: ]   [ DONE / OK ]
                 |                 - More training data    (Deploy Model)
                 |                 - Regularization (L2)
                 v                 - New NN architecture
          (Loop back to 1)               |
                                         v
                                  (Loop back to 1)
```

#### Step 1: Diagnose and Resolve High Bias
* **Remedies:** Train a bigger model (increase depth $L$, increase width $n^{[l]}$), train longer (more epochs), use advanced optimizers (Adam, RMSProp), or modify neural architecture.
* **Loop:** Re-evaluate training error until bias is low.

#### Step 2: Diagnose and Resolve High Variance
* **Remedies:** Gather more training data, apply **Regularization** ($L_2$, Dropout, data augmentation), or refine architecture.
* **Loop:** Re-evaluate validation error until dev error approaches training error.

#### The Modern Deep Learning Superpower
In classical machine learning, reducing bias almost always increased variance (the rigid bias-variance tradeoff). In Deep Learning:
* Making the neural network bigger reduces bias **without increasing variance** (provided proper regularization is applied).
* Adding more data or regularization reduces variance **without increasing bias**.
Practitioners can systematically drive **both** bias and variance down to achieve optimal performance!

---

## 7. Regularization: Solutions to Avoid Overfitting ($L_1$ vs. $L_2$)

> **Definition:** Regularization is the process of adding information or a complexity penalty to the optimization objective in order to solve ill-posed problems, prevent overfitting, and ensure robust generalization on unseen data.

$$\min_{w, b} \mathcal{J}(w, b) = \underbrace{\text{Loss}(\text{Data} \mid \text{Model})}_{\text{Fit Objective}} + \lambda \cdot \underbrace{\text{Complexity}(w)}_{\text{Penalty Term}}$$

### 7.1 Why Do Weights Explode During Overfitting?
When a high-capacity model (e.g., an 8th-degree polynomial) overfits, it forces its curve through every noisy data point. This produces wild, high-frequency oscillations that require **gigantic positive and negative parameter weights** ($w_j \approx \pm 500$) to cancel each other out.  
Regularization penalizes large weight magnitudes, keeping weights small ($w_j \approx 0.1$) and forcing the learned function to remain smooth.

---

### 7.2 Side-by-Side Mathematical Development: $L_2$ vs. $L_1$

| Property / Step | $L_2$ Regularization (Ridge / Weight Decay) | $L_1$ Regularization (Lasso / Sparsity) |
| :--- | :--- | :--- |
| **Complexity Penalty $\Omega(w)$** | $\Omega_{L2}(w) = \dfrac{\lambda}{2m} \|w\|_2^2 = \dfrac{\lambda}{2m} \displaystyle\sum_{j=1}^{n_x} w_j^2$ | $\Omega_{L1}(w) = \dfrac{\lambda}{m} \|w\|_1 = \dfrac{\lambda}{m} \displaystyle\sum_{j=1}^{n_x} \|w_j\|$ |
| **Total Cost Function $J(w, b)$** | $J(w, b) = \dfrac{1}{m}\displaystyle\sum_{i=1}^m \mathcal{L}\big(\hat{y}^{(i)}, y^{(i)}\big) + \dfrac{\lambda}{2m} \|w\|_2^2$ | $J(w, b) = \dfrac{1}{m}\displaystyle\sum_{i=1}^m \mathcal{L}\big(\hat{y}^{(i)}, y^{(i)}\big) + \dfrac{\lambda}{m} \|w\|_1$ |
| **Gradient / Subgradient $\dfrac{\partial J}{\partial w}$** | $\dfrac{\partial J}{\partial w} = \dfrac{\partial J_{\text{orig}}}{\partial w} + \dfrac{\lambda}{m} w$ | $\dfrac{\partial J}{\partial w} = \dfrac{\partial J_{\text{orig}}}{\partial w} + \dfrac{\lambda}{m} \text{sign}(w) \quad (w_j \neq 0)$ |
| **Update Expansion Step 1** | $w := w - \alpha \left(\dfrac{\partial J_{\text{orig}}}{\partial w} + \dfrac{\lambda}{m} w\right)$ | $w := w - \alpha \left(\dfrac{\partial J_{\text{orig}}}{\partial w} + \dfrac{\lambda}{m} \text{sign}(w)\right)$ |
| **Update Expansion Step 2** | $w := w - \alpha \dfrac{\lambda}{m} w - \alpha \dfrac{\partial J_{\text{orig}}}{\partial w}$ | $w := w - \alpha \dfrac{\partial J_{\text{orig}}}{\partial w} - \alpha \dfrac{\lambda}{m} \text{sign}(w)$ |
| **Final Update Formula** | $$w := \underbrace{\left(1 - \alpha \frac{\lambda}{m}\right)}_{< 1} w - \alpha \frac{\partial J_{\text{orig}}}{\partial w}$$ | $$w := w - \alpha \frac{\partial J_{\text{orig}}}{\partial w} - \underbrace{\alpha \frac{\lambda}{m} \text{sign}(w)}_{\text{constant shift towards } 0}$$ |
| **Geometric Behavior** | Spherical norm ball: weights shrunk uniformly, smoothly decayed toward zero, rarely exactly 0. | Sharp diamond norm ball: touches error contours at corners on coordinate axes $\implies$ **drives weights strictly to 0**. |
| **Key Practical Effect** | **Weight Decay:** Smooth, stable regularization preserving all features with reduced influence. | **Sparse Weights:** Performs automatic embedded **feature selection**, setting irrelevant weights to zero. |

---

### 7.3 Tuning the Hyperparameter $\lambda$
* **$\lambda$ too high:** The complexity penalty dominates; weights shrink severely ($w \to 0$); the model becomes too simple and **underfits** (high bias).
* **$\lambda$ too low ($\lambda \to 0$):** The complexity penalty is ignored; the network retains unconstrained capacity and **overfits** (high variance).
* **Target balance:** Fine-tune $\lambda$ on the **Dev set** to achieve maximum generalization accuracy.

---

### 7.4 Intuition: Why Regularization Reduces Overfitting via Tanh
Consider hidden layers using the hyperbolic tangent activation function $g(z) = \tanh(z)$:

$$\text{Increase } \lambda \quad\Longrightarrow\quad \text{Shrinks weight magnitudes: } w \approx 0 \quad\Longrightarrow\quad z = w^T x + b \approx 0$$

* Near $z = 0$, the hyperbolic tangent function is **approximately linear**:
  $$\tanh(z) \approx z \qquad \text{with derivative } g'(0) = 1$$
* When all hidden units operate in their approximately linear regime, the entire multilayer network behaves like a **simple linear model** (as proven in Section 2).
* Therefore, by increasing $\lambda$, we continuously restrict the non-linear flexibility of the network, preventing high-frequency oscillatory fits and effectively eliminating overfitting.

---
*Summary compiled for ENSIA Deep Learning Course 2026–2027 based on Lecture 6 (Neural Networks 1) by Prof. S.-A. Berrani.*
