---
pretty_name: Algerian Darja Sample
language: ar
license: mit
task_categories:
  - text-generation
tags:
  - algerian-darja
  - algerian-arabic
  - darija
  - arabic
  - nlp
  - language-modeling
  - text-generation
size_categories:
  - 1M<n<10M
---

# Algerian Darja Sample

[![Hugging Face](https://img.shields.io/badge/🤗-Hugging%20Face-yellow)](https://huggingface.co/datasets/DarjaCore/algerian-darja-sample)
[![Language](https://img.shields.io/badge/Language-Algerian%20Darja-red)](https://huggingface.co/datasets/DarjaCore/algerian-darja-sample)
[![License](https://img.shields.io/badge/License-MIT-lightgrey)](https://huggingface.co/datasets/DarjaCore/algerian-darja-sample)

A growing Algerian Darja text corpus collected for **NLP and language-modeling research**.

This dataset is updated incrementally as new sources are collected and processed. Exact sample counts, file sizes, and statistics change between releases — refer to the **Dataset Viewer** on the repository page for current figures rather than any numbers in this card.

## Dataset at a Glance

Sample count, file size, character/word counts, and other metrics are not fixed and grow over time as new batches are added. Check the repository's file listing and Dataset Viewer for up-to-date figures.

## Data Sources

The corpus is assembled from multiple sources over time, including:

- Algerian online forums
- Telegram channels and groups
- Academic and community text sources

Each new batch is deduplicated against the existing corpus before being added.

## Data Format

Single-column text dataset:

```text
text
```

Example:

```text
واش راك اليوم؟
```

Each row represents one independent text sample.

## Data Quality

- Samples are deduplicated within the corpus.
- Empty or whitespace-only samples are removed.
- Basic text cleaning is applied (mention stripping, repeated-character normalization) but the corpus has **not** been normalized into a single standardized Algerian Darja orthography.

## Intended Use

- Algerian Darja NLP research
- Language-model pretraining experiments
- Tokenizer evaluation
- Darja language analysis
- Text generation research
- Linguistic statistics

## Limitations

This is a **sample of an ongoing collection effort**, not a finished or complete corpus.

The data may contain:

- spelling variations
- informal language
- Arabizi / Latin-script text
- emojis
- noisy user-generated text
- potentially sensitive or context-dependent content

Statistics such as token counts depend on the tokenizer used and are not fixed values of the dataset itself.

## Preprocessing

- Empty-row detection and removal
- Duplicate detection and removal (within and across batches)
- Basic text cleaning

## Citation

```bibtex
@dataset{darjacore_algerian_darja_sample,
  author = {DarjaCore},
  title = {Algerian Darja Sample},
  year = {2026},
  publisher = {Hugging Face},
  url = {https://huggingface.co/datasets/DarjaCore/algerian-darja-sample}
}
```

## License

MIT

See the repository license for the applicable terms.

## Organization

**DarjaCore**

Open-source research focused on **Algerian Darja, NLP, and language technologies**.