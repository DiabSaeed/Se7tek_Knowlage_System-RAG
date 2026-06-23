<div align="center">
  <img src="assets/Se7tek_logo.png" alt="Se7tek Logo">
  # Sehatek Medical KNOWLEDGE RAG 🩺🚀

  <p>
    <img src="https://img.shields.io/badge/Python-3.13+-blue.svg?logo=python&logoColor=white" alt="Python">
    <img src="https://img.shields.io/badge/FastAPI-005571?style=flat&logo=fastapi" alt="FastAPI">
    <img src="https://img.shields.io/badge/Qdrant-FF5252?style=flat&logo=qdrant&logoColor=white" alt="Qdrant">
    <img src="https://img.shields.io/badge/MongoDB-4EA94B?style=flat&logo=mongodb&logoColor=white" alt="MongoDB">
    <img src="https://img.shields.io/badge/LangChain-121212?style=flat&logo=chainlink&logoColor=white" alt="LangChain">
    <img src="https://img.shields.io/badge/Docker-2496ED?style=flat&logo=docker&logoColor=white" alt="Docker">
  </p>
</div>

The Knowledge System is the intelligent knowledge layer of the Se7tek platform, designed to provide accurate, context-aware medical information through Retrieval-Augmented Generation (RAG).

This repository enables healthcare professionals and patients to interact with trusted pregnancy-related knowledge sources using natural language queries. By combining document retrieval with Large Language Models (LLMs), the system delivers grounded and reliable responses based on verified medical content rather than model memory alone.

---
## Requirements 

- installing python 3.13 or later 
### installing python with mini-conda 

1) install conda from [here](https://www.anaconda.com/docs/getting-started/miniconda/install)
2) create virtual environment by using:
``` bash    
$ conda create -n knowlage-rag
```
3) activate virtual env by using:
```bash
$ conda activate knowlage-rag
```

## Installation

### install required packages

```bash 
$ pip install -r requirements.txt
```
### Setup the env variables

```bash 
$ cp .env.example .env
```

Setup your environments variables in the `.env` file. Like `OPENAI_KEY` value.

### 🚀 Run the Application 

``` bash 
$ cd src/
$ uvicorn main:app --host 0.0.0.0 --port 5000 --reload
```

## 🏗️ Core Architecture & Features

Unlike standard RAG implementations, the **Sehatek Knowledge System** is engineered to handle highly complex medical literature, including multi-page clinical tables and dense statistical data (e.g., Systematic Reviews and Meta-Analyses).

* **Advanced Document Parsing:** Utilizes **LlamaParse (Premium Vision Mode)** with custom parsing instructions to extract borderless, complex clinical tables into continuous, self-contained, and context-rich markdown strings, preventing "orphaned rows" and data loss.
* **Smart Chunking Strategy:** Implements a multi-layered chunking pipeline using LangChain's `MarkdownHeaderTextSplitter` and a `RecursiveCharacterTextSplitter` with dynamic sizes to preserve table integrity and hierarchical structure.
* **Hybrid Search Retrieval:** Combines Dense Vector Search and Sparse Search (BM25) using **Qdrant** to maximize retrieval recall across massive medical documents.
* **Cross-Encoder Reranking:** Applies a highly precise NLP Reranker layer (`sentence-transformers/cross-encoder`) on top of retrieved chunks. This overcomes BM25 dilution and ensures multi-entity queries (e.g., comparing AUCs across different studies) return exactly the right context.
* **Data Persistence:** Raw chunks and parsed metadata are safely stored in **MongoDB** for auditability and rapid retrieval tuning.

## 💻 Tech Stack

* **Backend Framework:** FastAPI (Python)
* **Vector Database:** Qdrant
* **Document Store:** MongoDB (Motor / Asyncio)
* **Parsing & Ingestion:** LlamaParse, PyMuPDF, Docling
* **NLP & Text Processing:** LangChain, Sentence-Transformers (Cross-Encoders)
* **LLM Integration:** OpenRouter API