# Wireless Communications & Networking Systems (WCNS)
## Midterm Examination (2025/2026) — Complete Official Solutions & Explanations

**Institution:** ENSIA (The National School of Artificial Intelligence)  
**Academic Year:** Fourth Year — Semester 7 (2025/2026)  
**Total Points:** 20.0 pts  
**Duration:** 90 minutes  

---

## Part 1: Course Questions — Multiple Choice (8.0 pts)
*Grading Rule: Correct answer = +0.5 pt | Wrong answer = -0.25 pt | No answer = 0 pt*

| Q# | Question Summary | Correct Option | Detailed Justification & Course Reference |
|---|---|---|---|
| **1** | Modulation is necessary to: | **Carry a signal on a high-frequency radio carrier.** | Baseband signals cannot be radiated efficiently into free space because required antenna size is proportional to wavelength ($L \approx \lambda/4 = c / (4f)$). At audio/baseband frequencies, antennas would be kilometers long. Modulation shifts the baseband spectrum to high-frequency RF carrier bands, enabling practical antenna sizes and frequency-division channel sharing (*CH03, Slide 5-9*). |
| **2** | The advantage of modulating digital data into a digital signal is: | **The simplicity and low cost of the equipment.** | Direct baseband digital encoding (e.g., NRZ, Manchester) uses digital logic gates and line drivers, which are substantially simpler, less power-hungry, and cheaper than digital-to-analog modulators/oscillators (*CH05, Slide 5-3*). |
| **3** | ASK modulation is rarely used on its own because it is: | **Very sensitive to variations in signal power.** | Amplitude-Shift Keying represents data through amplitude levels. Wireless propagation channels suffer from fading, shadowing, and path loss variations. Sudden gain changes or amplitude fluctuations directly distort the decision threshold, causing frequent errors (*CH05, Slide 5-11*). |
| **4** | In TDMA, users share the channel by being assigned: | **Different time slots.** | In Time Division Multiple Access, the full channel bandwidth is allocated to users sequentially in disjoint, non-overlapping time slots (*CH04, Slide 4-15*). |
| **5** | Sky-wave propagation allows for long-distance communication because: | **The signal is reflected by the ionosphere.** | Sky-wave signals (typically in the HF band, 3–30 MHz) refract and reflect off the ionized gas layers in the upper atmosphere (ionosphere) back to Earth, allowing multi-hop global transmission beyond the horizon (*CH04, Slide 4-18*). |
| **6** | ISM frequency bands are important because they: | **Can be used without a license for devices like Wi-Fi.** | Industrial, Scientific, and Medical (ISM) frequency bands (e.g., 2.4 GHz, 5 GHz) are unlicensed spectrum allocations, allowing consumer devices such as Wi-Fi, Bluetooth, and ZigBee to transmit without costly spectrum licensing, subject only to power/spread-spectrum constraints (*CH04, Slide 4-13*). |
| **7** | When a Wi-Fi signal passes through a wall, the primary propagation mechanism is: | **Transmission.** | Passing *through* a solid material medium involves transmission through the barrier with attenuation and boundary refraction (*CH04, Slide 4-21*). |
| **8** | The noise present in all electronic devices that cannot be eliminated is: | **Thermal noise.** | Thermal (Johnson-Nyquist) noise arises from the thermal agitation of charge carriers inside all conductors and electronic components. It is a fundamental thermodynamic property with power density $N_0 = kT$ that cannot be eliminated (*CH04, Slide 4-31*). |
| **9** | If multiple copies of a signal arrive at the receiver at slightly different times, it is called: | **Multipath propagation.** | Waves bounce off buildings, terrain, and obstacles along different geometric paths of unequal lengths, causing delayed and attenuated copies of the signal to arrive at the receiver (*CH04, Slide 4-37*). |
| **10** | A channel that changes very slowly compared to the duration of a bit is said to be experiencing: | **Slow fading.** | When the coherence time of the channel $T_c$ is much larger than the bit duration $T_b$ ($T_c \gg T_b$), the channel transfer function remains essentially constant over one or multiple bit intervals (*CH04, Slide 4-42*). |
| **11** | MIMO technology uses multiple antennas to: | **Improve reception and/or data rate.** | Multiple Input Multiple Output (MIMO) leverages spatial diversity (combining redundant paths to combat fading and improve signal reception/reliability) and spatial multiplexing (transmitting independent data streams simultaneously on the same frequency to multiply throughput) (*CH04, Slide 4-54*). |
| **12** | The advantage of QPSK modulation over BPSK is that it: | **Allows a higher bit rate for the same bandwidth.** | QPSK encodes 2 bits per symbol ($M = 4$, $L = \log_2 M = 2$) while BPSK encodes 1 bit per symbol ($M = 2$, $L = 1$). For an identical channel bandwidth, QPSK doubles the spectral efficiency and transmitted bit rate (*CH05, Slide 5-21*). |
| **13** | The technique that spreads the signal over a wide bandwidth to make it more robust is: | **Spread Spectrum.** | Spread Spectrum (e.g., DSSS, FHSS) intentionally broadens the transmission bandwidth well beyond the minimum information bandwidth, providing high immunity against narrowband jamming, interference, and multipath fading (*CH04, Slide 4-47*). |
| **14** | Intersymbol Interference (ISI) is primarily caused by: | **Different delays from multiple paths (multipath).** | Multipath delay spread disperses symbol pulses in time. Delayed replicas of earlier symbols arrive during the time window of subsequent symbols, overlapping and interfering with detection (*CH04, Slide 4-39*). |
| **15** | A Forward Error Correction (FEC) code allows the system to: | **Detect and correct some errors without retransmission.** | FEC introduces structured mathematical redundancy into the transmitted bitstream, allowing the receiver to autonomously identify and correct bit errors without needing a feedback reverse link to request retransmission (*CH04, Slide 4-47*). |
| **16** | Signal path loss increases with: | **Increasing distance and increasing frequency.** | According to the Friis transmission / Free Space Path Loss model, $L = \left(\frac{4\pi d}{\lambda}\right)^2 = \left(\frac{4\pi f d}{c}\right)^2$. Path loss is directly proportional to both $d^2$ (distance squared) and $f^2$ (frequency squared) (*CH04, Slide 4-24*). |

---

## Part 2: Course Questions — Short Answers (4.0 pts)

### Question 1 (0.5 pts)
**Prompt:** *Using your understanding of Shannon's formula, if we increase the bandwidth, what happens to the maximum capacity of the channel? And if we improve the SNR?*

**Solution:**
According to Shannon’s capacity formula:
$$C = B \log_2(1 + \text{SNR})$$
* **Increasing Bandwidth ($B$):** The maximum channel capacity $C$ **increases** (linearly with $B$, assuming constant SNR).
* **Improving SNR ($\frac{P_s}{P_n}$):** The maximum channel capacity $C$ **increases** (logarithmically with SNR).

---

### Question 2 (0.5 pts)
**Prompt:** *To achieve higher throughput, more complex modulation (more bits per symbol) can be used. What is the main disadvantage of this approach?*

**Solution:**
The main disadvantage is **drastically increased sensitivity to noise and interference (requiring a significantly higher SNR to achieve an acceptable Bit Error Rate)**.  
*Physical cause:* Packing more bits into each symbol places constellation points closer together (reducing the minimum Euclidean distance $d_{\min}$ between adjacent symbols), making the signal far more vulnerable to noise misclassification. It also increases hardware/DSP transceiver complexity.

---

### Question 3 (1.0 pt)
**Scenario:** *A technician installs a Wi-Fi link between two buildings.*

#### a- The signal is weak. Give two reasons related to distance and the environment that could explain this. [0.5 pts]
1. **Distance Factor:** **Free Space Path Loss (attenuation over distance)**. Signal power decreases with the square of the distance ($P_r \propto 1/d^2$), leading to high geometric energy spreading over long distances.
2. **Environmental Factor:** **Obstacles and Shadowing / Fresnel Zone Obstruction**. Physical barriers between the two buildings (e.g., walls, foliage/trees, neighboring structures) cause absorption, scattering, and diffraction loss. Obstructing the 1st Fresnel zone causes destructive multipath interference.

#### b- He replaces standard antennas with more directional antennas (with higher gain). What is the expected effect on the strength of the received signal? [0.5 pts]
* **Expected Effect:** The strength of the received signal (received power $P_r$) will **increase significantly**.  
* **Explanation:** Directional antennas focus the radiated electromagnetic energy into a narrow beam towards the receiver rather than dispersing it isotropically in all directions. According to the Friis transmission formula ($P_r = P_t G_t G_r \left(\frac{\lambda}{4\pi d}\right)^2$), increasing transmitter and receiver antenna gains ($G_t, G_r$) directly scales up received power and improves link SNR.

---

### Question 4 (1.0 pt)
**Scenario:** *In an urban environment, a user in a car notices that their mobile signal varies very quickly and may even cut out at times.*

#### a- Identify the physical phenomenon causing this problem. [0.5 pts]
* **Phenomenon:** **Small-scale multipath fading (Rayleigh fading with Doppler spread)**.  
The signal bounces off surrounding buildings, creating multiple delayed paths that interfere constructively and destructively at the mobile receiver.

#### b- Is this fading “fast” or “slow”? Is it “frequency selective” or “flat”? Briefly (max 2 lines) justify your answer in relation to the scenario (car = movement, city = buildings). [0.5 pts]
* **Fast fading:** The motion of the car induces a high Doppler spread and small coherence time ($T_c < T_{\text{symbol}}$), making the channel change rapidly during message transmission.
* **Frequency selective fading:** The dense buildings create multiple distant reflection paths with large delay spread ($\tau$), making the coherence bandwidth ($B_c \approx 1/\tau$) smaller than the signal bandwidth ($B_s$), causing frequency-dependent nulls.

---

### Question 5 (0.5 pts)
**Prompt:** *Briefly explain (in two lines maximum) why 16-QAM is more sensitive to noise than QPSK.*

**Solution:**
For the same transmitted average signal power, 16-QAM packs 16 constellation points into the space where QPSK packs only 4. Consequently, the **minimum Euclidean distance ($d_{\min}$) between adjacent points is much smaller**, allowing small noise fluctuations to push symbols over decision boundaries and cause bit errors.

---

### Question 6 (0.5 pts)
**Prompt:** *Draw the constellation diagram for QPSK modulation. Label each point with the corresponding bits.*

**Solution:**
In QPSK, the carrier phase takes four orthogonal states separated by $90^\circ$ ($\pi/2$), typically mapped using Gray coding so that adjacent symbols differ by only a single bit:

```
               Quadrature Q(t)
                      ^
                      |
        01            |            11
         *            |             *
     (135°, 3π/4)     |         (45°, π/4)
                      |
  --------------------+--------------------> In-Phase I(t)
                      |
         *            |             *
        00            |            10
    (225°, -3π/4)     |        (315°, -π/4)
                      |
```

* **Quadrant I ($I = +1, Q = +1$, phase $+45^\circ$):** Symbol `11`
* **Quadrant II ($I = -1, Q = +1$, phase $+135^\circ$):** Symbol `01`
* **Quadrant III ($I = -1, Q = -1$, phase $-135^\circ$ or $225^\circ$):** Symbol `00`
* **Quadrant IV ($I = +1, Q = -1$, phase $-45^\circ$ or $315^\circ$):** Symbol `10`

---

## Exercise 1 (4.0 pts)

**Given Parameters:**
* Periodic square wave frequency: $f = 0.3\text{ kHz} = 300\text{ Hz}$
* Sampling frequency: $f_s = 10\text{ kHz} = 10,000\text{ Hz}$
* Total observation duration: $50\text{ ms}$

### 1- Time Period

#### Determine the period $T$ of the signal (0.5 pts):
$$T = \frac{1}{f} = \frac{1}{300\text{ Hz}} = \frac{1}{300}\text{ s} = \frac{10}{3}\text{ ms} \approx 3.333\text{ ms} \quad (0.00333\text{ s})$$

#### Determine how many complete periods of the signal are contained in an observation window of $10\text{ ms}$ (0.5 pts):
$$N = \frac{T_{\text{window}}}{T} = \frac{10\text{ ms}}{\frac{10}{3}\text{ ms}} = 10 \times \frac{3}{10} = \mathbf{3\text{ complete periods}}$$

---

### 2- Signal Spectrum

#### Determine the frequencies of the first three harmonics (0.5 pts):
The Fourier series of a zero-mean periodic square wave contains only **odd integer multiples** of the fundamental frequency ($f_k = k \cdot f_0$ for odd $k$):
$$x(t) = \frac{4A}{\pi} \left[ \sin(2\pi f_0 t) + \frac{1}{3}\sin(2\pi(3f_0)t) + \frac{1}{5}\sin(2\pi(5f_0)t) + \frac{1}{7}\sin(2\pi(7f_0)t) + \dots \right]$$

* **Harmonic 1 (Fundamental component):** $f_1 = f_0 = \mathbf{300\text{ Hz}}\ (0.3\text{ kHz})$
* **Harmonic 2 (3rd order harmonic):** $f_3 = 3f_0 = 3 \times 300\text{ Hz} = \mathbf{900\text{ Hz}}\ (0.9\text{ kHz})$
* **Harmonic 3 (5th order harmonic):** $f_5 = 5f_0 = 5 \times 300\text{ Hz} = \mathbf{1500\text{ Hz}}\ (1.5\text{ kHz})$

*(Note: If interpreted as the first three harmonics existing strictly above the fundamental, they are $3f_0 = 900\text{ Hz}$, $5f_0 = 1500\text{ Hz}$, and $7f_0 = 2100\text{ Hz}$).*

#### Explain why a square wave requires more bandwidth than a sinusoidal signal of the same fundamental frequency (0.5 pts):
A pure sinusoidal signal concentrates all its energy at a single discrete frequency ($f_0$), having an ideal bandwidth of zero (or minimal). In contrast, a square wave possesses instantaneous step transitions (discontinuities in the time domain). By Fourier analysis, constructing these sharp vertical edges requires an **infinite summation of odd sinusoidal harmonics** ($3f_0, 5f_0, 7f_0, \dots$). Preserving the steep edges without severe pulse rounding/distortion requires transmitting a large number of these high-frequency harmonics, demanding significantly wider (theoretically infinite) channel bandwidth.

---

### 3- Low-Pass Filtering (Moving Average)

The impulse response of an $M$-point moving average filter is:
$$h[n] = \begin{cases} \frac{1}{M}, & 0 \le n < M \\ 0, & \text{otherwise} \end{cases}$$
Its frequency response is:
$$H(f) = \frac{1}{M} \frac{\sin\left(\omega \frac{M}{2}\right)}{\sin\left(\frac{\omega}{2}\right)} e^{-j\omega(M-1)/2}, \quad \text{where } \omega = 2\pi \frac{f}{f_s}$$

#### For $M = 21$, determine the frequency of the first zero of the frequency response $H(f)$ (1.0 pt):
The zeros of $H(f)$ occur when the numerator equals zero while the denominator is non-zero:
$$\sin\left(\omega \frac{M}{2}\right) = 0 \implies \omega \frac{M}{2} = k\pi \quad (k = 1, 2, \dots)$$
The first zero corresponds to $k = 1$:
$$\left(2\pi \frac{f_{\text{null}}}{f_s}\right) \frac{M}{2} = \pi \implies f_{\text{null}} = \frac{f_s}{M}$$
For $M = 21$ and $f_s = 10\text{ kHz} = 10,000\text{ Hz}$:
$$f_{\text{null}} = \frac{10,000\text{ Hz}}{21} = \mathbf{476.19\text{ Hz}} \quad (\approx 0.476\text{ kHz})$$

#### Determine the minimum odd value of $M$, according to the criterion of the first null frequency, allowing the filter to pass the fundamental frequency as well as the first harmonic, while attenuating higher harmonics (1.0 pt):
We want the filter to:
1. **Pass:** Fundamental frequency $f_0 = 300\text{ Hz}$ and first harmonic component $f_{\text{harm1}} = 3f_0 = 900\text{ Hz}$. This requires $900\text{ Hz}$ to fall inside the main passband lobe before the first zero:
   $$f_{\text{null}} > 900\text{ Hz} \iff \frac{f_s}{M} > 900 \implies M < \frac{10,000}{900} = \frac{100}{9} \approx 11.11$$
2. **Attenuate Higher Harmonics:** The next harmonic is $5f_0 = 1500\text{ Hz}$. To ensure it is attenuated in the stopband, the first null should occur at or before $1500\text{ Hz}$:
   $$f_{\text{null}} \le 1500\text{ Hz} \iff \frac{f_s}{M} \le 1500 \implies M \ge \frac{10,000}{1500} = \frac{20}{3} \approx 6.67$$

Combining both criteria:
$$6.67 \le M < 11.11$$
The allowable odd integer values for $M$ are:
$$M \in \{7, 9, 11\}$$

* **Design Solution Based on Hint 2:**  
  Hint 2 states: *"place this zero just after the first harmonic that we want to preserve ($900\text{ Hz}$), so that the higher harmonics are attenuated."*  
  Placing the zero immediately above $900\text{ Hz}$ yields the odd value **$M = 11$** ($f_{\text{null}} = \frac{10,000}{11} \approx \mathbf{909.09\text{ Hz}}$).  
* **Design Solution Based on Minimum Odd Value:**  
  The lowest odd integer that places the first null below $1500\text{ Hz}$ while keeping $900\text{ Hz}$ in the passband is **$M = 7$** ($f_{\text{null}} = \frac{10,000}{7} \approx \mathbf{1428.57\text{ Hz}}$).

---

## Exercise 2 (4.0 pts)

**Given Parameters:**
* Transmitted 20-bit binary sequence:  
  `B = [1, 0, 1, 1, 0, 0, 1, 0, 1, 0, 1, 1, 0, 0, 0, 1, 0, 1, 1, 0]`
* Bit rate: $R_b = 100\text{ bits/s} \implies T_b = \frac{1}{R_b} = 10\text{ ms}$
* Carrier frequency: $f_c = 200\text{ Hz} \implies T_c = \frac{1}{f_c} = 5\text{ ms}$
* Observation window: $80\text{ ms} \implies \frac{80\text{ ms}}{10\text{ ms}} = \mathbf{8\text{ bits}}$
* First 8 bits: `[1, 0, 1, 1, 0, 0, 1, 0]`

---

### 1- Line Coding over 80 ms Time Window

```
Time [ms]:     0        10        20        30        40        50        60        70        80
Bit:           |  Bit 1  |  Bit 0  |  Bit 1  |  Bit 1  |  Bit 0  |  Bit 0  |  Bit 1  |  Bit 0  |
--------------------------------------------------------------------------------------------------
Unipolar NRZ:  +---------+         +---------+---------+                   +---------+
(+1V / 0V)     |         |         |                   |                   |         |
               0         +---------+                   +---------+---------+         +---------0
--------------------------------------------------------------------------------------------------
Bipolar NRZ:   +---------+         +---------+---------+                   +---------+
(+1V / -1V)    |         |         |                   |                   |         |
               0---------+---------+-------------------+---------+---------+---------+---------0
                         |         |                   |         |                   |         |
                         +---------+                   +---------+                   +---------+
```

* **Unipolar NRZ:** Bit 1 is mapped to $+1\text{ V}$ (high), Bit 0 is mapped to $0\text{ V}$ (ground).
* **Bipolar NRZ (Polar NRZ-L):** Bit 1 is mapped to $+1\text{ V}$, Bit 0 is mapped to $-1\text{ V}$.

---

### 2- Modulated Waveforms (ASK & BPSK) over 80 ms Time Window

#### Calculation of Carrier Cycles per Bit:
$$\text{Cycles per bit} = f_c \times T_b = 200\text{ Hz} \times 0.01\text{ s} = \mathbf{2\text{ full sinusoidal cycles per bit}}$$

#### Descriptions for Drawing:
* **ASK (OOK) on 200 Hz Carrier:**
  * **Bit 1 ($[0,10], [20,40], [60,70]\text{ ms}$):** Carrier is **ON** $\rightarrow$ Draw **2 full sinusoidal cycles** of amplitude $A$.
  * **Bit 0 ($[10,20], [40,60], [70,80]\text{ ms}$):** Carrier is **OFF** $\rightarrow$ Constant zero voltage ($0\text{ V}$, flat line).
* **BPSK on 200 Hz Carrier:**
  * **Bit 1:** Phase $0^\circ$ (standard sine wave $A\sin(2\pi f_c t)$) $\rightarrow$ Draw **2 full cycles** starting with a positive slope.
  * **Bit 0:** Phase $180^\circ$ (inverted sine wave $-A\sin(2\pi f_c t)$) $\rightarrow$ Draw **2 full cycles** inverted (starting with a negative slope).
  * **Phase Reversals:** At boundaries between differing bits ($1 \to 0$ or $0 \to 1$), there is an instantaneous sharp $180^\circ$ phase inversion.

---

### 3- Signal-to-Noise Ratio (SNR) in Decibels

Given linear power ratio $\frac{P_s}{P_n} = 6$:
$$\text{SNR}_{\text{dB}} = 10 \log_{10}\left(\frac{P_s}{P_n}\right) = 10 \log_{10}(6)$$
Using $\log_{10}(6) = \log_{10}(2) + \log_{10}(3) \approx 0.30103 + 0.47712 = 0.77815$:
$$\text{SNR}_{\text{dB}} = 10 \times 0.77815 = \mathbf{7.78\text{ dB}} \quad (\approx 7.8\text{ dB})$$

---

### Performance Evaluation Under Noise

**Experimental Observation:**  
Over 20 transmitted bits:
* ASK (OOK): 4 bit errors observed.
* BPSK: 0 bit errors observed.

#### 1. Calculate the Bit Error Rate (BER) for each modulation scheme:
$$\text{BER}_{\text{ASK}} = \frac{\text{Number of errors}}{\text{Total transmitted bits}} = \frac{4}{20} = \mathbf{0.20} \quad (20\%)$$
$$\text{BER}_{\text{BPSK}} = \frac{\text{Number of errors}}{\text{Total transmitted bits}} = \frac{0}{20} = \mathbf{0.00} \quad (0\%)$$

#### 2. Explain why the two modulation types give different results under the same noise conditions:
1. **Minimum Euclidean Distance ($d_{\min}$):**
   * In ASK (OOK), the two constellation points are $\{0, A\}$. The Euclidean distance separating the symbols is $d_{\min} = A$. The decision threshold sits at $A/2$, giving a noise margin of only $A/2$.
   * In BPSK, the signaling is antipodal with points at $\{-A, +A\}$. The Euclidean distance is $d_{\min} = 2A$ (**twice** the distance of ASK for the same peak amplitude). The decision threshold sits at $0\text{ V}$, giving a noise margin of $A$ (double that of ASK). Because error probability decays exponentially with $d_{\min}^2$, BPSK achieves vastly superior noise immunity.
2. **Receiver Detection Mechanism:**
   * ASK typically uses noncoherent envelope detection with an amplitude threshold. Additive noise during a "0" bit easily spikes above the threshold, triggering false alarms.
   * BPSK uses coherent matched filtering / correlator detection. The receiver integrates over the entire bit duration against a synchronized carrier replica, which averages out zero-mean Gaussian noise and rejects out-of-phase noise components.

#### 3. Which modulation would you recommend for a system that must operate reliably in a noisy environment and why?
* **Recommendation:** **BPSK (Binary Phase Shift Keying)**.
* **Justification:**
  * **Superior Noise Resilience:** BPSK requires approximately $3\text{ dB}$ to $4\text{ dB}$ less SNR than ASK to achieve the same target BER thanks to its antipodal constellation ($d_{\min} = 2\sqrt{E_b}$).
  * **Empirical Proof:** Under the tested SNR of $7.8\text{ dB}$, BPSK suffered zero errors ($\text{BER} = 0\%$), whereas ASK experienced an intolerable $20\%$ error rate ($\text{BER} = 0.20$).
  * **Constant Envelope:** BPSK maintains constant transmit power across all bits, preventing issues with power amplifier non-linearities and channel gain fluctuations.
