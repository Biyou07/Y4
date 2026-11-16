# Deep Learning: Neural Networks 2 (NN 2)
**Regularization Techniques, Gradient Dynamics, and Weight Initialization Theory**  
*Course: Deep Learning (ENSIA 2026–2027) — Prof. Sid-Ahmed Berrani*

---

## 1. Dropout Regularization

Dropout is a simple but extremely effective technique to stop neural networks from overfitting.

### 1.1 Core Idea
* At each training step, we randomly turn off (drop) each hidden neuron with probability $1 - kp$, where $kp \in (0, 1]$ is the **keep probability** (typically $0.5$).
* **Dynamic Sub-networks:** At every training iteration, the network trains a smaller, randomly sampled "thinned" sub-network.

---

### 1.2 Implementation: Inverted Dropout (3 Simple Steps)
For each layer $l$ during training:

```
Step 1: Sample Binary Mask       d^[l] ~ Bernoulli(kp)
                                      |
Step 2: Zero Out Neurons         a^[l] := a^[l] * d^[l]
                                      |
Step 3: Scale Up (Inverted)      a^[l] := a^[l] / kp
                                      |
Step 4: Next Layer Forward       z^[l+1] = W^[l+1] a^[l] + b^[l+1]
```

1. **Sample Mask:** Draw a random boolean matrix where each element is 1 with probability $kp$:
   $$d^{[l]} = (\text{np.random.rand}(*a^{[l]}\text{.shape}) < kp)$$
2. **Zero Out Neurons:** Multiply activations element-wise:
   $$a^{[l]} := a^{[l]} * d^{[l]}$$
3. **Scale Up (Inverted Step):** Divide by the keep probability $kp$:
   $$a^{[l]} := \frac{a^{[l]}}{kp}$$

#### Why Divide by $kp$? (Expected Value Preservation)
Because dropout zeroes out a fraction $(1 - kp)$ of the neurons, the total signal sum entering the next layer would be reduced by $(1 - kp)$ without scaling. Dividing by $kp$ restores the original expected value:
$$\mathbb{E}[a^{[l]}_{\text{dropout}}] = kp \cdot a^{[l]} + (1 - kp) \cdot 0 = kp \cdot a^{[l]} \quad\Longrightarrow\quad \mathbb{E}\left[\frac{a^{[l]} * d^{[l]}}{kp}\right] = a^{[l]}$$

> **What to do at Test Time? Absolutely Nothing!**  
> Because activations were already scaled up during training, at test time we evaluate the **full unmasked network** with standard activations ($a^{[l]} = g(z^{[l]})$). No dropout and no scaling are needed at test time.

---

### 1.3 Why Does Dropout Work? (Two Simple Intuitions)
1. **Ensemble of Smaller Networks:** At each training step, we train a different random sub-network. At test time, using the full network is like averaging the predictions of $2^N$ different models together.
2. **Spreading the Weights (No Single Feature is Essential):** A neuron cannot rely heavily on any single input feature because that input could be dropped at any time. Therefore, the neuron is forced to spread its weights across all inputs rather than putting high confidence on just one. This has a shrinking effect on weights, very similar to $L_2$ regularization!

---

### 1.4 Practical Rules for Dropout
* **Layer-by-Layer Tuning:** You can set a different $kp$ for each layer. For wide layers with many parameters, use aggressive dropout (e.g., $kp = 0.5$). For small layers, use $kp = 0.8$ or $1.0$ (no dropout).
* **Input Layer:** Rarely used on the input layer ($kp = 1.0$ or at most $0.8$).
* **When to Use:** Use dropout **only to fix Overfitting (High Variance)**. Never use it for High Bias. It is especially popular in Computer Vision.

---

## 2. Data Augmentation & Early Stopping

### 2.1 Data Augmentation
* **Motivation:** More training data is the best cure for overfitting. When collecting real data is too difficult or expensive, we artificially generate new examples from existing data.
* **Common Transformations in Computer Vision:**
  1. *Horizontal / Vertical Flips:* A flipped cat is still a cat.
  2. *Random Rotations:* Rotate slightly ($\pm 10^\circ - 30^\circ$) to recognize tilted objects.
  3. *Random Brightness & Contrast:* Simulates different lighting and sensors.
  4. *Random Zoom & Crop:* Teaches the model to recognize objects whether near or far.
* **Why it regularizes:** It forces the network to learn invariant features rather than memorizing specific pixel coordinates.
* **Implementation:** Handled on-the-fly during training using `ImageDataGenerator` in Keras or modern data preprocessing layers (`RandomFlip`, `RandomRotation`).

---

### 2.2 Early Stopping
During training, training loss keeps going down. But validation (dev) loss goes down, reaches a minimum, and then starts climbing back up as the model overfits:
1. **Underfitting Phase:** Training and dev loss both decrease.
2. **Best Stopping Point:** Dev loss reaches its global minimum (optimal generalization).
3. **Overfitting Phase:** Training loss continues down, but dev loss increases because the network memorizes noise.

#### Why Early Stopping Acts Like $L_2$ Regularization
* Weights start initialized near zero ($\|W\| \approx 0$).
* With each gradient update, weights grow larger to fit complex patterns.
* By stopping training early, we **prevent weights from becoming large**. Stopping after $T$ iterations is mathematically very similar to applying an $L_2$ penalty with $\lambda \approx 1 / (\alpha T)$.

#### The Orthogonalization Trade-off
* **The Principle:** Each knob should address only one task:
  * *Task 1:* Minimize cost $J$ on the training set (optimizers, train longer).
  * *Task 2:* Prevent overfitting on the dev set (regularization, more data).
* **Early Stopping Violates Orthogonalization:** Stopping early stops you from minimizing training loss (hurts Task 1) in order to keep dev loss low (helps Task 2).
* **Advantage:** You only need to run training **once**, whereas $L_2$ requires testing many values of $\lambda$.

---

## 3. Vanishing and Exploding Gradients in Deep Networks

### 3.1 Simple Example: Exponential Compounding with Depth
Imagine an $L$-layer deep network with $b = 0$, linear activations $g(z) = z$, and weight matrices scaled by a constant factor $p$:
$$W^{[l]} = p \cdot I \quad\Longrightarrow\quad \hat{y} = (p \cdot I)^L x = p^L x$$

For a deep network with $L = 50$ layers:
* **If $p > 1$ (e.g., $p = 1.5$):**  
  $p^L = (1.5)^{50} \approx 6.37 \times 10^8 \implies$ **Exploding Gradients** (overflow, `NaN`, divergence).
* **If $p < 1$ (e.g., $p = 0.5$):**  
  $p^L = (0.5)^{50} \approx 8.88 \times 10^{-16} \implies$ **Vanishing Gradients** (signals and gradients disappear; early layers stop learning).

---

### 3.2 The Symmetry Problem: Why We Cannot Initialize Weights to Zero
In Logistic Regression, initializing $w = 0, b = 0$ works because there is only 1 output unit.  
In a Neural Network, **zero initialization causes complete failure**:

#### Why Zero Initialization Fails
If $W = 0, b = 0$:
1. **Identical Activations:** All hidden neurons compute $z_1 = z_2 = 0 \implies a_1 = a_2 = g(0)$.
2. **Identical Gradients:** Downstream neurons send back the exact same gradients: $\frac{\partial J}{\partial W_{1, j}} = \frac{\partial J}{\partial W_{2, j}}$.
3. **Identical Updates:** After gradient descent, $W_{1, j}$ and $W_{2, j}$ remain completely equal forever.

> **Takeaway:** All hidden neurons compute the exact same feature! The entire layer acts as if it has only **one single neuron**.  
> **Solution:** Weights in neural networks **must be initialized randomly** to break symmetry.

---

### 3.3 Small Random Initialization (`np.random.randn(...) * 0.01`)
* **Why small?** For Sigmoid and Tanh, keeping weights small keeps $z$ near 0 where the derivative is steepest ($g'(0) = 1$ for tanh), avoiding flat saturation zones.
* **Why 0.01 fails in deep networks:** Multiplying by $0.01$ across 20 or 50 layers causes signals to vanish. We need weight scales that adjust automatically to the number of incoming inputs!

---

## 4. Weight Initialization Theory: Deducing Xavier & He

To prevent vanishing and exploding gradients, our fundamental rule is:  
**Preserve the signal variance from layer to layer, i.e., $\mathbf{\text{Var}(z) = \text{Var}(x)}$!**

---

### 4.1 The Fundamental Variance Equation
Consider a single neuron computing $z = \sum_{i=1}^{n} w_i x_i$ (where $n = n^{[l-1]}$ is the number of inputs, and $b = 0$).  
Assuming weights $w_i$ and inputs $x_i$ are independent with mean zero:

$$\text{Var}(w_i x_i) = \text{Var}(w_i) \cdot \text{Var}(x_i) = \text{Var}(w) \cdot \text{Var}(x)$$

Since $z$ is the sum of $n$ independent identical components:
$$\text{Var}(z) = \sum_{i=1}^n \text{Var}(w_i x_i) = n \cdot \text{Var}(w) \cdot \text{Var}(x)$$

---

### 4.2 Deducing Xavier Initialization (for Tanh / Sigmoid)

For linear activations or Tanh near zero ($\tanh(z) \approx z$), the activation function does not change the variance:
$$\text{Var}(a) \approx \text{Var}(z)$$

We enforce our golden rule: the variance of the output $z$ must equal the variance of the input $x$:
$$\text{Var}(z) \stackrel{!}{=} \text{Var}(x)$$

Substitute our variance equation:
$$n \cdot \text{Var}(w) \cdot \text{Var}(x) = \text{Var}(x)$$

Divide both sides by $\text{Var}(x)$:
$$n \cdot \text{Var}(w) = 1 \quad\Longrightarrow\quad \mathbf{\text{Var}(w) = \frac{1}{n}}$$

Taking the square root gives the required standard deviation:
$$\mathbf{\sigma_w = \sqrt{\frac{1}{n^{[l-1]}}}}$$

```python
# Xavier (Glorot) Initialization for Tanh / Sigmoid
W = np.random.randn(n_l, n_in) * np.sqrt(1.0 / n_in)
```

*(Normalized Xavier variant also averages fan-out: $\text{Var}(w) = \frac{2}{n_{\text{in}} + n_{\text{out}}}$).*

---

### 4.3 Deducing He (Kaiming) Initialization (for ReLU)

What happens when we pass $z$ through a **ReLU** activation ($a = \max(0, z)$)?
* ReLU sets all negative values ($z < 0$) to zero.
* This zeroes out half the distribution ($\approx 50\%$ of the signal), **cutting the variance in half**:
  $$\text{Var}(a) = \frac{1}{2} \text{Var}(z)$$
* When this activation becomes the input $x$ to the next layer:
  $$\text{Var}(z_{\text{next}}) = n \cdot \text{Var}(w) \cdot \text{Var}(a) = n \cdot \text{Var}(w) \cdot \left(\frac{1}{2} \text{Var}(z)\right) = \frac{n}{2} \cdot \text{Var}(w) \cdot \text{Var}(z)$$

To preserve the variance across layers ($\text{Var}(z_{\text{next}}) \stackrel{!}{=} \text{Var}(z)$):
$$\frac{n}{2} \cdot \text{Var}(w) = 1 \quad\Longrightarrow\quad \mathbf{\text{Var}(w) = \frac{2}{n}}$$

Taking the square root gives the required standard deviation:
$$\mathbf{\sigma_w = \sqrt{\frac{2}{n^{[l-1]}}}}$$

```python
# He (Kaiming) Initialization for ReLU / Leaky ReLU
W = np.random.randn(n_l, n_in) * np.sqrt(2.0 / n_in)
```

> **Simple Takeaway:** Because ReLU zeroes out the negative half of the inputs (killing half the variance), we must **double the weight variance** ($2/n$) to keep the signal variance stable!

---

### 4.4 Bias Initialization
Biases $b^{[l]}$ do not have $n$ inputs summing into them, so they do not amplify variance. Initializing biases to zero ($b = 0$) is standard and optimal, because symmetry is already broken by the random weights $W$.

---

### 4.5 Master Summary: Weight Initialization Reference Table

| Activation Function | Initialization Name | Variance Rule $\text{Var}(W)$ | Standard Deviation $\sigma_w$ | NumPy Implementation Code |
| :--- | :--- | :---: | :---: | :--- |
| **Tanh / Sigmoid** | Xavier (Glorot) | $\dfrac{1}{n^{[l-1]}}$ | $\sqrt{\dfrac{1}{n^{[l-1]}}}$ | `W = np.random.randn(n_l, n_in) * np.sqrt(1/n_in)` |
| **Tanh / Sigmoid (Alt)** | Normalized Xavier | $\dfrac{2}{n^{[l-1]} + n^{[l]}}$ | $\sqrt{\dfrac{2}{n_{\text{in}} + n_{\text{out}}}}$ | `W = np.random.randn(n_l, n_in) * np.sqrt(2/(n_in + n_l))` |
| **ReLU / Leaky ReLU** | He (Kaiming) | $\dfrac{2}{n^{[l-1]}}$ | $\sqrt{\dfrac{2}{n^{[l-1]}}}$ | `W = np.random.randn(n_l, n_in) * np.sqrt(2/n_in)` |
| **Biases ($b^{[l]}$)** | Zeros | $0$ | $0$ | `b = np.zeros((n_l, 1))` *(Symmetry broken by $W$)* |
