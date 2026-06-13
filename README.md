# Sehatek Medical KNOWLAGE RAG 
The Knowledge System is the intelligent knowledge layer of the Se7tek platform, designed to provide accurate, context-aware medical information through Retrieval-Augmented Generation (RAG).

This repository enables healthcare professionals and patients to interact with trusted pregnancy-related knowledge sources using natural language queries. By combining document retrieval with Large Language Models (LLMs), the system delivers grounded and reliable responses based on verified medical content rather than model memory alone.

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