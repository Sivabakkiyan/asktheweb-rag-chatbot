# AskTheWeb – RAG Powered Website Chatbot

## Overview

AskTheWeb is a Retrieval-Augmented Generation (RAG) project that allows users to chat with the content of any website.

The project is being developed in phases. The current implementation focuses on building a clean and modular website ingestion pipeline that will later power the RAG system.

---

## Current Features

- Modular project architecture
- Website URL normalization
- HTML page fetching using Requests
- HTML parsing using BeautifulSoup
- Title extraction
- Clean text extraction
- Internal link extraction
- Smart link filtering
- Structured page representation

---

## Project Structure

```
AskTheWeb/
│
├── app.py
├── scraper/
│   ├── crawler.py
│   ├── parser.py
│   └── filters.py
│
├── utils/
│   └── url_utils.py
│
├── rag/
├── data/
├── docs/
│
├── requirements.txt
├── README.md
└── .gitignore
```

---

## Tech Stack

- Python
- Requests
- BeautifulSoup4

---

## Current Status

✅ Phase 1 Completed

The project can:

- Fetch a website
- Parse its HTML
- Extract clean text
- Extract valid internal links
- Return structured webpage data

---

## Upcoming Phases

- Recursive website crawling
- Knowledge base generation
- Text chunking
- Embedding generation
- FAISS vector database
- Semantic retrieval
- Gemini integration
- Grok fallback
- Streamlit chat interface
- Source citations