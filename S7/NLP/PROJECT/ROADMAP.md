# Comprehensive Project Roadmap & Technical Specification
## Project 16: Conversational Agent in Algerian Dialect for Drug Addiction Support

This document details every system component, technical stage, and execution step required to build, evaluate, and deploy the application.

---

## 1. System Architecture Overview

The system consists of five interconnected subsystems:

```
[ User (Algerian Darija / Arabizi / French) ]
                     │
                     ▼
       ┌───────────────────────────┐
       │   Frontend / Client UI    │  <-- Goal Setting, Mood/Craving Log, Emergency SOS
       └─────────────┬─────────────┘
                     │ REST / WebSocket
                     ▼
       ┌───────────────────────────┐
       │     FastAPI Backend       │
       └──────┬─────────────┬──────┘
              │             │
     [Triage / Emergency]   │ [Conversational Flow]
              │             ▼
              │   ┌───────────────────────────────────┐
              │   │   Safety & Crisis Intent Filter   │  <-- DziriBERT / Regex Triage
              │   └──────┬─────────────────────┬──────┘
              │          │ Safe                │ Crisis (Overdose/Suicide)
              │          ▼                     ▼
              │   ┌───────────────┐     ┌────────────────────────┐
              │   │  RAG Pipeline │     │ Deterministic Response │
              │   │  (FAISS/BGE)  │     │ (Hotlines: 14 / 1548 / │
              │   └──────┬────────┘     │  Local CISA Clinics)   │
              │          ▼              └────────────────────────┘
              │   ┌───────────────┐
              │   │ Fine-Tuned    │
              │   │ Darija LLM    │  <-- Qwen-2.5 / Llama-3.1 with QLoRA Adapter
              │   └──────┬────────┘
              │          ▼
              │   ┌───────────────┐
              │   │ Guardrail /   │  <-- Strip unauthorized medical advice / check tone
              │   │ Post-Filter   │
              │   └──────┬────────┘
              │          │
              ▼          ▼
       [ Formatted Darija Response ]
```

---

## 2. Core Pillars & Detailed Action Steps

### Part 1: Domain Knowledge, Clinical Framing & Local Context
* **Step 1.1 — Define Therapeutic Scope & Philosophy:**
  * Adopt **Motivational Interviewing (MI)** (Miller & Rollnick): non-judgmental, rolling with resistance, open questions, affirmations, reflective listening, summaries (OARS).
  * Establish clear boundaries: support, psychoeducation, craving management, and harm reduction (needle hygiene, HIV/HCV risks) — **never** prescribing pharmaceuticals or managing acute withdrawal clinically.
* **Step 1.2 — Collect Official Health Resources:**
  * Gather health documents from INSP (*Institut National de Santé Publique*), Algerian Ministry of Health, and WHO guidelines on substance use disorders.
  * Extract verified guidance on transmission vectors (HIV, Hepatitis B/C), overdose recognition, and withdrawal timelines.
* **Step 1.3 — Map the Algerian Drug Lexicon & Referral Directory:**
  * Build a dictionary of Algerian street terminology for drugs (e.g., *saroukh*, *lyrica / prégabaline / madame courage*, *kachete*, *chira*, *exta / halawa*).
  * Compile an emergency and clinical referral database: Civil Protection (`14`), Police (`1548`), and regional *Centres Intermédiaires de Soins en Addictologie (CISA)* across wilayas.

---

### Part 2: Data Engineering & Corpus Preparation
* **Step 2.1 — Knowledge Base Processing for RAG:**
  * Clean, segment, and chunk medical guidelines into standardized passages (250–500 tokens).
  * Index chunks with bilingual/multilingual embeddings (e.g., `BAAI/bge-m3`) inside a vector store (ChromaDB or FAISS).
* **Step 2.2 — Motivational Dialogue Dataset Curation:**
  * Collect existing open-source addiction and counseling Q&A sets (e.g., standard clinical counseling prompts).
  * Translate and adapt prompts and responses into authentic **Algerian Darija** (handling both Arabic script and Latin/Arabizi).
  * Incorporate code-switching (mixing Darija with French terms commonly used in medical and daily life).
* **Step 2.3 — Quality & Safety Filtering:**
  * Review dialogues with native speakers to verify natural phrasing, empathy, and avoidance of toxic or lecturing tones.
  * Format dataset into standard instruction/chat format (`{"messages": [{"role": "user", ...}, {"role": "assistant", ...}]}`).

---

### Part 3: Model Selection, RAG & Fine-Tuning
* **Step 3.1 — Foundation Model Benchmarking:**
  * Test zero-shot capabilities in Arabic dialects across top lightweight open models:
    * `Qwen/Qwen2.5-7B-Instruct`
    * `meta-llama/Llama-3.1-8B-Instruct`
    * `FreedomIntelligence/AceGPT-7B`
  * Select the top performer based on Darija prompt comprehension and adherence to instructions.
* **Step 3.2 — RAG (Retrieval-Augmented Generation) Implementation:**
  * Build a retrieval engine to inject factual context into the prompt when users ask technical health questions (e.g., "What happens if I stop taking Lyrica suddenly?").
  * Ensure system prompts instruct the model to base factual health claims strictly on retrieved evidence.
* **Step 3.3 — Parameter-Efficient Fine-Tuning (PEFT / QLoRA):**
  * Train LoRA adapters (Rank 16–32) on 4-bit/8-bit quantized base models using the curated Algerian Darija MI dataset.
  * Focus fine-tuning on persona consistency, empathy, dialectal tone, and avoiding prescriptive lecturing.
* **Step 3.4 — Model Quantization & Export:**
  * Quantize the final adapter and base model to GGUF (e.g., Q4_K_M) or AWQ/vLLM formats for rapid inference on standard consumer GPUs or CPU instances.

---

### Part 4: Safety Guardrails & Crisis Triage Engine
* **Step 4.1 — Deterministic Crisis Intent Classification:**
  * Implement an upfront classification module (fine-tuned `alger-ia/dziribert` + regex keyword triggers) to detect high-risk signals:
    * Acute overdose indicators (loss of consciousness, respiratory distress).
    * Suicide / self-harm ideation.
    * Threats of violence.
  * **Fallback rule:** When a crisis is flagged, immediately bypass the LLM and return verified emergency contacts and emergency protocol steps.
* **Step 4.2 — Post-Generation Output Guardrail:**
  * Build checks to verify that the generated output does not prescribe medications (e.g., Methadone, Subutex, benzodiazepines) or make diagnostic claims.
  * Enforce persistent disclaimers clarifying that the agent is an AI support companion, not a licensed medical doctor.

---

### Part 5: Application Development (Frontend & Backend)
* **Step 5.1 — Backend API (FastAPI / Python):**
  * Session management: maintain conversation context window with rolling summary.
  * Integration of the triage classifier, RAG retrieval pipeline, and LLM inference engine.
  * User data encryption and privacy-preserving storage (anonymized session logs).
* **Step 5.2 — Frontend Interface (Web / Mobile):**
  * Clean, accessible UI (React, Flutter, or Streamlit prototype) with native RTL support for Arabic script and LTR for Arabizi/French.
  * **Core Interactive Features:**
    * **Chat Interface:** Low-latency conversational screen.
    * **Personalized Goal Tracker:** Tracking reduction goals, clean streaks, and mood logs.
    * **Educational Micro-Modules:** Bite-sized cards explaining harm reduction, physical risks, and mental health.
    * **One-Tap Emergency SOS:** Prominent button to dial emergency services or locate the nearest CISA clinic.

---

### Part 6: Multi-Dimensional Evaluation & Deliverables
* **Step 6.1 — Linguistic & Cultural Evaluation:**
  * Native speaker evaluation measuring:
    * Fluency and naturalness of Algerian Darija.
    * Handling of code-switching and Arabizi.
    * Appropriateness of cultural context.
* **Step 6.2 — Clinical & Behavioral Alignment (MITI Framework):**
  * Evaluate conversations against the *Motivational Interviewing Treatment Integrity (MITI)* standard:
    * Empathy score.
    * Ratio of reflections to questions.
    * Absence of confrontation, advice without permission, or shaming.
* **Step 6.3 — Safety & Red-Teaming Audits:**
  * Test adversarial prompts attempting to elicit drug recipes, suicide encouragement, or medical prescriptions.
  * Verify 100% triage capture rate on acute crisis triggers.
* **Step 6.4 — Deliverables & Documentation:**
  * Comprehensive GitHub codebase with clean setup instructions.
  * Curated Darija addiction-support dataset.
  * Technical report and academic research paper documenting architecture, empirical findings, and ethical considerations.

---

## 3. Timeline & Execution Phases

| Phase | Focus Area | Key Output |
| :--- | :--- | :--- |
| **Phase 1 (Weeks 1–2)** | Clinical Scope & Health Data Gathering | Lexicon, INSP/WHO documents, crisis protocols |
| **Phase 2 (Weeks 3–4)** | Data Curation & Darija Translation | Curated SFT dataset + RAG chunked knowledge base |
| **Phase 3 (Weeks 5–6)** | Model Fine-Tuning & RAG Pipeline | QLoRA fine-tuned model + RAG retrieval evaluation |
| **Phase 4 (Week 7)** | Safety Guardrails & Triage Engine | Crisis classifier (`dziribert` / regex) + output filters |
| **Phase 5 (Weeks 8–9)** | Full-Stack Application | Backend API + Frontend UI with goal tracker |
| **Phase 6 (Weeks 10–11)** | Evaluation, Red-Teaming & Paper | MITI scores, safety audit, final research paper |
