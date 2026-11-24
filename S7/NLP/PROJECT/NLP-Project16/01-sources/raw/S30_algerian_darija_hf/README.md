---
language:
- ar
license: cc-by-4.0
size_categories:
- 100K<n<1M
task_categories:
- text-generation
pretty_name: Algerian Darija
dataset_info:
  features:
  - name: Text
    dtype: string
  splits:
  - name: train
    num_bytes: 30499704
    num_examples: 2324
  - name: v1
    num_bytes: 23477688
    num_examples: 168655
  download_size: 44762377
  dataset_size: 53977392
configs:
- config_name: default
  data_files:
  - split: train
    path: data/train-*
  - split: v1
    path: data/v1-*
tags:
- Darija
- Algeria
---


## Overview
This dataset contains text in `Algerian Darija`, collected from a variety of sources including **existing datasets on Hugging Face**, **web scraping**, and **YouTube transcript APIs**. 

- The **`train`** **split** consists more then **2k rows** of uncleaned text data.

- The **`v1`** **split** consists more than **170k rows** of split and partially cleaned text.

## Sources
The text data was gathered from:

- **Hugging Face Datasets**: Pre-existing datasets relevant to Algerian Darija.
- **Web Scraping**: Content from various online sources.
- **YouTube API**: Transcriptions from Algerian Darija videos and comments on YouTube.


## Data Cleaning
Initial data cleaning steps included:

- Removing duplicate emojis and characters.
- Removing URLs, email addresses, and phone numbers.

**Note**: Some text data from the YouTube Transcript API may contain imperfections due to limitations in speech-to-text technology for Algerian Darija. Additionally, the dataset still requires further cleaning to improve its quality for more advanced NLP tasks.