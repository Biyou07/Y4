# Project 16: Inter-Annotator Agreement Report (Agreement Note)
**Dataset Quality Gate – Algerian Dialect Addiction Support Assistant**  
**Authors / Annotators:** Ahmed Yassine Gasmi (Annotator 1) & Mohamed Ayoub Belhimer (Annotator 2)  
**Date:** November 2026  
**Reference Specification:** `label-guide-v1.docx` | `dataset-format-v1.docx`

---

## 1. Executive Summary & Objective

In accordance with Stage 3 ("Quality Gate") of the project pipeline and the methodology required for the research paper, an **Inter-Annotator Agreement (IAA)** study was conducted to empirically validate the reliability and objectivity of the annotation guidelines (`label-guide-v1`).

* **Sample Size**: 40 real-world Darija comments drawn from public Algerian social media sources (YouTube community comments and Telegram public channels).
* **Experimental Setup**: A double-blind annotation setup where Annotator 2 (Mohamed Ayoub Belhimer) independently labeled the 40 messages without access to Annotator 1's (Ahmed Yassine Gasmi) prior annotations.
* **Core Metrics Evaluated**:
  1. Percentage of identical agreement for **`danger`**: **97.5%** (39/40 matching).
  2. Percentage of identical agreement for **`request`**: **100.0%** (40/40 matching).
  3. **Cohen's Kappa ($\kappa$)** for **`danger`**: **0.9572** ($P_o = 0.9750$, $P_e = 0.4156$).

Under standard biostatistical and NLP benchmarks (Landis & Koch, 1977), a Cohen's Kappa score $\kappa > 0.81$ denotes **"Almost Perfect Agreement"**, demonstrating that the taxonomy and decision boundaries established in `label-guide-v1` are robust, reliable, and reproducible for safety triage modeling.

---

## 2. Quantitative Results & Confusion Matrix

### 2.1 Summary of Agreement Across All Fields

| Annotation Field | Identical Matches | Total Rows | Raw Agreement (%) | Metric Type |
| :--- | :---: | :---: | :---: | :--- |
| **`danger`** | **39** | **40** | **97.5%** | Primary Metric (Cohen's $\kappa = 0.9572$) |
| **`request`** | **40** | **40** | **100.0%** | Secondary Metric (Perfect Agreement) |
| **`user_type`** | **40** | **40** | **100.0%** | Contextual Taxonomy |
| **`drug`** | **39** | **40** | **97.5%** | Substance Entity Recognition |
| **`drug_sense`**| **38** | **40** | **95.0%** | Context Rule Disambiguation |

### 2.2 Confusion Matrix for `danger`

| Annotator 1 (Ahmed) \ Annotator 2 (Mohamed) | `none` | `low` | `high` | `crisis` | `Skip` | Total |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **`none`** | **23** | 1 | 0 | 0 | 0 | 24 |
| **`low`** | 0 | **9** | 0 | 0 | 0 | 9 |
| **`high`** | 0 | 0 | 0 | 0 | 0 | 0 |
| **`crisis`** | 0 | 0 | 0 | 0 | 0 | 0 |
| **`Skip`** | 0 | 0 | 0 | 0 | **7** | 7 |
| **Total** | 23 | 10 | 0 | 0 | 7 | **40** |

* Observed Agreement ($P_o$): $\frac{23 + 9 + 7}{40} = \frac{39}{40} = 0.9750$
* Expected Chance Agreement ($P_e$): $(0.60 \times 0.575) + (0.225 \times 0.25) + (0.175 \times 0.175) = 0.345 + 0.05625 + 0.030625 = 0.4156$
* Cohen's Kappa: $\kappa = \frac{0.9750 - 0.4156}{1 - 0.4156} = \frac{0.5594}{0.5844} \approx \mathbf{0.9572}$

---

## 3. In-Depth Disagreement Analysis

Out of the 40 blind evaluations, exactly **3 messages** yielded minor boundary divergences between the two annotators. These discrepancies provide valuable qualitative insights:

### Case 1: `M-S34-0003` – Societal Exposure vs. Clinical Personal Risk
* **Text:**  
  *"الاحياء الشعبية كلها اصبحت وكرا للمخذرات و الفساد .الله يجيبلهم طامة كبرى تمحيهم"*  
  *(Working-class neighborhoods have all become dens of drugs and corruption. May Allah bring upon them a great catastrophe that wipes them out.)*
* **Ahmed (Annotator 1):** `danger = none` | `drug_sense = drug` | `drug = unspecified`
* **Mohamed (Annotator 2):** `danger = low` | `drug_sense = drug` | `drug = unspecified`
* **Analysis:**  
  Annotator 2 evaluated the text from an **environmental/exposure risk** perspective (the presence of drug dens and violence in the community). In contrast, Annotator 1 applied the **strict clinical triage criteria** of `label-guide-v1`, which explicitly specifies that `danger = low` requires an active personal user or craving (*"use or an urge is mentioned"*). Because the speaker is an outside observer venting about neighborhood crime without personal involvement, the clinical chatbot safety risk is strictly `none`.

### Case 2: `M-S35-0015` – Implicit Post-Cessation Anxiety vs. Drug Entity Presence
* **Text:**  
  *"Habasto hekamni waswas 9ahri w khl3a"*  
  *(I stopped it; obsessive fear and panic seized me.)*
* **Ahmed (Annotator 1):** `drug_sense = unclear` | `drug = unspecified` | `request = withdrawal` | `danger = low`
* **Mohamed (Annotator 2):** `drug_sense = drug` | `drug = unspecified` | `request = withdrawal` | `danger = low`
* **Analysis:**  
  Both annotators fully agreed on `user_type` (`person who uses`), `request` (`withdrawal`), and `danger` (`low`). The minor difference in `drug_sense` stems from the fact that no drug noun appears in the text ("Habasto" = I stopped it). Annotator 1 marked `unclear` because the noun was elided, while Annotator 2 inferred that within the context of an addiction recovery channel, stopping a substance that induces obsessive withdrawal symptoms confirms the drug context.

### Case 3: `M-S35-0024` – Granular Slang Mapping vs. General Substance Entity
* **Text:**  
  *"...ومبتلية ناكل الساروخ ونبكي على روحي من القهرة ربي يفرج عليا وعلى كامل المبتليين ادعولي خاوتي ربي يشافيني"*  
  *(...and I am afflicted eating saroukh and crying for myself from agony; may Allah relieve me and all those afflicted, pray for me brothers...)*
* **Ahmed (Annotator 1):** `drug_sense = unclear` | `drug = unspecified` | `request = other` | `danger = low`
* **Mohamed (Annotator 2):** `drug_sense = drug` | `drug = pills` | `request = other` | `danger = low`
* **Analysis:**  
  Both annotators agreed on `person who uses`, `other` (prayer request), and `danger = low`. However, Annotator 2 specifically recognized the street argot *"الساروخ"* (*saroukh*, literally rocket) as psychotropic pills (Lyrica / pregabalin / Rivotril), mapping it to `pills` as cataloged in `slang-glossary-v1.xlsx`. Annotator 1 marked `unspecified` because no pharmaceutical brand was named.

---

## 4. Recommendations & Clarifications for Guide v1.1

Following the review of these borderline cases, the following refinements are recommended for inclusion in the final thesis/paper documentation:

1. **Environmental Complaints Rule**:  
   Explicitly specify that general societal or political complaints concerning neighborhood drug crime (without personal consumption, cravings, or an active user described) must strictly be classified as `danger = none`.
2. **Argot Granularity Rule**:  
   When a verified street slang term from `slang-glossary-v1` (e.g., *saroukh*, *karkoubi*, *zatla*) is used alongside unambiguous consumption verbs (such as *"ناكل الساروخ"* or *"نتكيف زطلة"*), annotators should assign the specific substance class (`pills`, `cannabis`) rather than defaulting to `unspecified`.

---

## 5. Conclusion

The exceptionally high Cohen's Kappa score ($\mathbf{0.9572}$) and raw agreement rates ($\ge 95\%$) provide definitive empirical validation of the dataset's quality. These results establish that the annotation framework is statistically reliable, ensuring high-fidelity training data for the upstream safety triage model and downstream RAG conversational components.
