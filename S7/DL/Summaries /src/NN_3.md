# Deep Learning: Neural Networks 3 (NN 3)
**Optimization Algorithms, Loss Landscapes, Multi-Class Softmax, and Batch Normalization**  
*Course: Deep Learning (ENSIA 2026–2027) — Prof. Sid-Ahmed Berrani*

---

## 1. Mini-Batch Gradient Descent & Loss Landscapes

Training deep networks on large datasets ($m = 10^6 - 10^8$) is computationally expensive. We accelerate training by dividing the dataset into smaller, manageable chunks called **mini-batches**.

### 1.1 The Three Gradient Descent Regimes
* **Batch Gradient Descent (Batch Size = $m$):** Processes all $m$ training instances before taking a single parameter step.
  * *Pros:* Smooth, monotonic cost decline.
  * *Cons:* Painfully slow per step on large datasets; cannot start learning until the entire dataset is evaluated.
* **Stochastic Gradient Descent (SGD) (Batch Size = 1):** Takes a parameter step after evaluating each individual sample.
  * *Pros:* Immediate, frequent parameter updates.
  * *Cons:* Highly erratic and noisy; never truly converges to the minimum (wanders around); completely loses GPU matrix parallelization speedup.
* **Mini-Batch Gradient Descent ($1 < \text{Batch Size} < m$):** The ideal middle ground:
  * Leverages high-performance GPU tensor parallelization.
  * Makes multiple parameter updates per pass through the dataset.
* **Definition of an Epoch:** One complete pass through the entire training dataset of $m$ examples.

---

### 1.2 Practical Rules for Mini-Batch Sizing
* **Small Datasets ($m < 2000$):** Use standard **Batch Gradient Descent** (batch size $= m$). Memory overhead is minimal and convergence is smooth.
* **Large Datasets ($m \ge 2000$):** Use mini-batch sizes that are **powers of 2**:
  $$\text{Batch Size} \in \{64, \; 128, \; 256, \; 512, \; 1024\}$$
* **Hardware Alignment:** Powers of 2 match CPU/GPU memory architecture, maximizing cache efficiency and SIMD tensor core utilization.
* **Memory Constraint:** Make sure your mini-batch size comfortably fits within GPU RAM along with all intermediate forward activations.

---

### 1.3 Optimization Challenges in High-Dimensional Landscapes
* **The Local Minima Myth:** In high-dimensional optimization ($10^5$ to $10^8$ weights), the probability that all directions simultaneously slope upwards is virtually zero. Almost all zero-gradient critical points are **Saddle Points** (local minimum along some dimensions, local maximum along others).
* **Flat Plateaus:** Saddle points are surrounded by wide regions where gradients are nearly zero ($\nabla J \approx 0$). Gradient descent slows down to a crawl in these regions.
* **Pathological Curvature (Ravines):** The loss surface forms an elongated valley with steep walls and a flat floor. Gradient descent oscillates violently back and forth between the walls rather than making progress along the floor.

---

### 1.4 The Mathematical Tool: Exponentially Weighted Averages (EWA)
Used to smooth out noisy sequences and track trends:
$$V_t = \beta V_{t-1} + (1 - \beta) \theta_t \qquad (V_0 = 0)$$

* **Averaging Window:** $V_t$ represents an average over approximately the past $\mathbf{\frac{1}{1 - \beta}}$ steps:
  * If $\beta = 0.90 \implies$ average over the past $\approx 10$ steps.
  * If $\beta = 0.98 \implies$ average over the past $\approx 50$ steps.
  * If $\beta = 0.50 \implies$ average over the past $\approx 2$ steps.

---

## 2. Advanced Optimization Algorithms: Momentum, RMSProp, and Adam

Standard Gradient Descent oscillates violently along steep directions and moves agonizingly slowly along shallow directions. Modern optimizers use gradient history to solve this.

### 2.1 Gradient Descent with Momentum (Adds Inertia)
Computes an exponentially weighted average of past gradients and uses this "velocity" $v$ to update parameters. Acts like a heavy ball rolling down a ravine:

$$\begin{aligned}
v_{dw} &= \beta v_{dw} + (1 - \beta) dw, \qquad v_{db} = \beta v_{db} + (1 - \beta) db \\[1.5pt]
w &:= w - \alpha v_{dw}, \qquad\qquad\quad\; b := b - \alpha v_{db} \qquad\qquad (\text{Default } \beta = 0.9)
\end{aligned}$$

* **Cancels Oscillations:** Vertical oscillations cancel each other out (positive and negative components sum to zero), while horizontal progress compounds and accelerates.
* **Escapes Flat Plateaus & Vanishing Gradients:** When the current gradient is near zero ($dw \approx 0$), velocity persists ($v \approx \beta v > 0$), allowing the optimizer to coast through plateaus.

---

### 2.2 RMSProp (Root Mean Square Propagation — Geoffrey Hinton)
Tracks the exponentially weighted average of **squared gradients** ($s$), and divides updates by $\sqrt{s}$:

$$\begin{aligned}
s_{dw} &= \beta_2 s_{dw} + (1 - \beta_2) dw^2, \qquad s_{db} = \beta_2 s_{db} + (1 - \beta_2) db^2 \\[1.5pt]
w &:= w - \alpha \frac{dw}{\sqrt{s_{dw}} + \epsilon}, \qquad\qquad b := b - \alpha \frac{db}{\sqrt{s_{db}} + \epsilon} \qquad (\text{Default } \beta_2 = 0.999, \; \epsilon = 10^{-8})
\end{aligned}$$

* **Self-Tuning Coordinate Scaling:**
  * In steep, oscillating directions ($w_2$): gradients are large $\implies s_{dw}$ is large $\implies$ divides by a large number $\implies$ **dampens oscillations**.
  * In shallow, slow directions ($w_1$): gradients are tiny $\implies s_{dw}$ is small $\implies$ divides by a small number $\implies$ **accelerates progress**.

---

### 2.3 Adam: Adaptive Moment Estimation (Kingma & Ba 2015)
Combines **Momentum** (1st moment, direction) with **RMSProp** (2nd moment, coordinate scaling), and adds **Bias Correction** to fix early steps (since $v_0 = s_0 = 0$):

1. **Compute Moments:**
   $$v_{dw} = \beta_1 v_{dw} + (1 - \beta_1) dw, \qquad s_{dw} = \beta_2 s_{dw} + (1 - \beta_2) dw^2$$
2. **Apply Bias Correction (Crucial for Early Steps):**
   $$v_{dw}^{\text{corrected}} = \frac{v_{dw}}{1 - \beta_1^t}, \qquad s_{dw}^{\text{corrected}} = \frac{s_{dw}}{1 - \beta_2^t}$$
3. **Update Parameters:**
   $$w := w - \alpha \frac{v_{dw}^{\text{corrected}}}{\sqrt{s_{dw}^{\text{corrected}}} + \epsilon}$$

* **Hyperparameter Defaults:** $\beta_1 = 0.9$ (momentum), $\beta_2 = 0.999$ (RMSProp), $\epsilon = 10^{-8}$ (numerical stability). Learning rate $\alpha$ is tuned.

---

### 2.4 Summary Comparison of Optimizers

| Optimizer | Parameter Update Rule | Key Hyperparameters | Primary Advantage |
| :--- | :--- | :--- | :--- |
| **SGD** | $w := w - \alpha dw$ | $\alpha$ | Baseline; suffers from oscillations in ravines. |
| **Momentum** | $v := \beta v + (1-\beta)dw; \ w := w - \alpha v$ | $\alpha, \; \beta = 0.9$ | Smooths oscillations; coasts through flat plateaus. |
| **RMSProp** | $s := \beta_2 s + (1-\beta_2)dw^2; \ w := w - \alpha \frac{dw}{\sqrt{s}+\epsilon}$ | $\alpha, \; \beta_2 = 0.999, \; \epsilon = 10^{-8}$ | Adaptive learning rate per parameter coordinate. |
| **Adam** | Combines $v^{\text{corr}}$ and $\sqrt{s^{\text{corr}}}$ | $\alpha, \; \beta_1 = 0.9, \; \beta_2 = 0.999, \; \epsilon = 10^{-8}$ | **Industry standard**; fast, self-tuning, and robust. |

---

## 3. Learning Rate Schedules & Multi-Class Softmax Classification

### 3.1 Learning Rate Decay
A constant learning rate $\alpha$ is suboptimal:
* **Early in Training:** The model is far from the minimum $\implies$ large $\alpha$ allows rapid traversal of parameter space.
* **Late in Training:** Near the minimum, a fixed $\alpha$ causes the optimizer to bounce around the basin without converging. Decaying $\alpha$ allows tight, fine-tuned convergence.

#### Common Schedules (Epoch $t+1$)
Where $t+1$ is the number of the current epoch, $\alpha_t$ is the previous epoch's learning rate, and $k$ is a hyperparameter:
1. **Default (Inverse Decay):** $\alpha_{t+1} = \dfrac{1}{1 + k \cdot t} \cdot \alpha_t$ (smooth, gradual decay).
2. **Step Decay:** Drops the learning rate by a fixed factor every few epochs (e.g., typically cut by half every 10 epochs).
3. **Discrete Staircase:** $\alpha_{t+1} = \dfrac{k}{\sqrt{t}} \cdot \alpha_t$ (inversely proportional to $\sqrt{t}$).
4. **Exponential Decay:** $\alpha_{t+1} = \alpha_t \cdot e^{-k \cdot t}$ (faster, sharper drop-off).

---

### 3.2 Multi-Class Classification with Softmax ($C > 2$ Classes)
When classifying inputs into $C$ mutually exclusive classes (e.g., Dog, Cat, Bird, Other):
1. **Linear Logits:** The output layer has $C$ neurons:
   $$z^{[L]} = W^{[L]} a^{[L-1]} + b^{[L]} \in \mathbb{R}^C$$
2. **Exponentiation:** $t_i = e^{z_i^{[L]}}$ (ensures all terms are strictly positive).
3. **Softmax Normalization:**
   $$a_i^{[L]} = \hat{y}_i = \frac{e^{z_i^{[L]}}}{\sum_{j=1}^C e^{z_j^{[L]}}} \qquad \text{for } i = 1, 2, \dots, C$$

* **Key Properties:**
  * Every predicted probability is strictly bounded: $0 < \hat{y}_i < 1$.
  * The sum of all probabilities is **guaranteed to be 1**: $\sum_{i=1}^C \hat{y}_i = 1$. It forms a valid probability distribution!
  * If $C = 2$, Softmax is mathematically identical to the standard Sigmoid function.

---

### 3.3 Categorical Cross-Entropy Loss
For one-hot encoded ground truth vector $y \in \{0, 1\}^C$ and prediction vector $\hat{y} \in (0, 1)^C$:
$$\mathcal{L}(\hat{y}, y) = - \sum_{i=1}^C y_i \log(\hat{y}_i)$$

For a sample whose true class is $k$ ($y_k = 1$ and $y_{j \neq k} = 0$):
$$\mathcal{L}(\hat{y}, y) = - \log(\hat{y}_k)$$

* If the model predicts $\hat{y}_k = 1$ (confident & correct): $\mathcal{L} = -\log(1) = 0$ (Zero penalty).
* If the model predicts $\hat{y}_k = 0.5$: $\mathcal{L} = -\log(0.5) \approx 0.693$.
* If the model predicts $\hat{y}_k \to 0$ (completely wrong): $\mathcal{L} = -\log(0) \to +\infty$ (Infinite penalty!).

---

## 4. Batch Normalization (Subtle Overview) & Hyperparameters Reference

### 4.1 What is Batch Normalization?
Just as we normalize input features $x$ (zero mean, unit variance) to eliminate elongated cost contours, **Batch Normalization (Ioffe & Szegedy 2015)** normalizes the linear logits $z^{[l]}$ inside hidden layers across each mini-batch before applying the activation function $g(z)$.

### 4.2 The 4-Step Mini-Batch Normalization Algorithm
For a mini-batch of size $m$ with linear values $z^{(1)}, z^{(2)}, \dots, z^{(m)}$:
1. **Compute Mini-Batch Mean:** $\mu = \frac{1}{m} \sum_{i=1}^m z^{(i)}$
2. **Compute Mini-Batch Variance:** $\sigma^2 = \frac{1}{m} \sum_{i=1}^m (z^{(i)} - \mu)^2$
3. **Standardize (Zero Mean, Unit Variance):**
   $$z_{\text{norm}}^{(i)} = \frac{z^{(i)} - \mu}{\sqrt{\sigma^2 + \epsilon}} \qquad (\epsilon \approx 10^{-8} \text{ prevents division by zero})$$
4. **Scale and Shift (Learnable Parameters $\gamma$ and $\beta$):**
   $$\tilde{z}^{(i)} = \gamma \cdot z_{\text{norm}}^{(i)} + \beta \qquad \Longrightarrow \qquad a^{(i)} = g\big(\tilde{z}^{(i)}\big)$$

#### Why Learnable $\gamma$ and $\beta$?
If a hidden layer strictly had zero mean and unit variance, activations like Tanh would be permanently locked in their linear regime! Learnable parameters $\gamma$ and $\beta$ allow the network to **choose the optimal variance and mean for each layer** (if the network learns $\gamma = \sqrt{\sigma^2+\epsilon}$ and $\beta = \mu$, it can completely undo the normalization if needed).

### 4.3 Key Takeaways & Test-Time Behavior
* **Where applied:** Applied directly to $z^{[l]}$ **before** the activation function $g(\cdot)$.
* **Reduces Internal Covariate Shift:** Keeps the distribution of hidden inputs stable even as earlier layers update weights, allowing much **higher learning rates** $\alpha$ and accelerating training.
* **At Test Time:** Examples are evaluated one by one (no mini-batch). The model uses a running **Exponential Moving Average** of $\mu$ and $\sigma^2$ accumulated across mini-batches during training.

---

### 4.4 Master Deep Learning Hyperparameters Checklist

| Hyperparameter | Typical Default / Range | Practical Guidance |
| :--- | :--- | :--- |
| **Learning Rate $\alpha$** | $0.001, \; 0.01, \; 0.1$ | **Most important hyperparameter**; tune first using logarithmic scale. |
| **Momentum Factor $\beta_1$** | $0.9$ | Averages over last $\approx 10$ gradients; rarely needs tuning. |
| **RMSProp Factor $\beta_2$** | $0.999$ | Averages over last $\approx 1000$ squared gradients; almost never changed. |
| **Adam Epsilon $\epsilon$** | $10^{-8}$ | Prevents numerical division by zero; leave at default. |
| **Mini-Batch Size** | $64, \; 128, \; 256, \; 512$ | Powers of 2 matching hardware; tune based on GPU memory. |
| **Learning Rate Decay $k$** | Scheduled ($0.5$ every $K$ ep) | Decays $\alpha$ in late epochs to allow fine-tuned convergence. |
| **Architecture ($L, n^{[l]}$)** | Problem dependent | Increase depth/width for high bias; regularize for high variance. |
| **Regularization ($\lambda, kp$)** | $\lambda \approx 10^{-4}-10^{-2}, \; kp=0.5-0.8$ | Increase $\lambda$ or lower $kp$ strictly when facing overfitting. |
