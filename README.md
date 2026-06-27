# AskTheWeb 🌐
### Ask anything. Get answers directly from any website using RAG.

---

## Overview

AskTheWeb is a Retrieval-Augmented Generation (RAG) powered chatbot that allows users to chat with the content of any website. Simply provide a URL, and the app scrapes the website, builds a knowledge base, and answers your questions accurately based on the actual content.

---

## Features

- 🔗 **Multi-URL Support** — Load multiple websites at once
- 🕷️ **Recursive Web Scraping** — Crawls the given URL and linked pages automatically
- 🧠 **RAG Pipeline** — Retrieves most relevant content before answering
- ⚡ **Fast Vector Search** — Uses FAISS for millisecond-level chunk retrieval
- 🤖 **Dual AI Support** — Groq (primary) and Gemini (backup) for reliability
- 📄 **Source Citations** — Every answer shows which page it came from
- 📊 **Confidence Score** — Shows how relevant the retrieved content is
- 💬 **Chat History** — Remembers all questions and answers in the session
- 🛡️ **Robust Error Handling** — Handles broken URLs, blocked sites, empty pages gracefully
- 🎨 **Clean Streamlit UI** — Simple and professional chat interface

---

## Project Structure
AskTheWeb/

│

├── app.py                  → Main Streamlit chat application

│

├── scraper/

│   ├── crawler.py          → Recursive web crawler

│   ├── parser.py           → HTML parser and text extractor

│   └── filters.py          → Smart link filter

│

├── rag/

│   ├── chunker.py          → Text chunking with overlap

│   ├── embedder.py         → HuggingFace embeddings + FAISS storage

│   ├── retriever.py        → Semantic chunk retrieval

│   └── generator.py        → AI answer generation (Groq + Gemini)

│

├── utils/

│   ├── url_utils.py        → URL normalization

│   └── file_utils.py       → File save/load utilities

│

├── data/                   → FAISS index storage

├── docs/                   → Documentation

├── requirements.txt        → Python dependencies

├── .gitignore              → Git ignore rules

└── README.md               → Project documentation
---

## Tech Stack

|Tool                    |Purpose                         |
|----------------------- |------------------------------- |
| Python                 | Core language                  |
| Streamlit              | Chat UI                        |
| Requests               | Fetch web pages                |
| BeautifulSoup4         | Parse HTML                     |
| LangChain              | Text chunking                  |
| HuggingFace Embeddings | Convert text to vectors        |
| FAISS                  | Fast vector storage and search |
| Groq (LLaMA 3.1)       | Primary AI model               |
| Gemini 2.5 Flash       | Backup AI model                |
| python-dotenv          | Secure API key management      |

---

## How It Works
User enters a website URL

↓
App scrapes the page and follows internal links (up to 10 pages)

↓
All text is split into overlapping chunks (1000 words each)

↓
Chunks are converted to vectors using HuggingFace embeddings

↓
Vectors stored in FAISS index for fast search

↓
User asks a question

↓
Question converted to vector → FAISS finds top 3 relevant chunks

↓
Chunks + question sent to Groq (or Gemini as backup)

↓
AI generates accurate answer with source citation
---

## Setup Instructions

### 1. Clone the repository
```bash
git clone https://github.com/Sivabakkiyan/AskTheWeb.git
cd AskTheWeb
```

### 2. Create virtual environment
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Create `.env` file
GEMINI_API_KEY=your_gemini_api_key_here

GROQ_API_KEY=your_groq_api_key_here

GOOGLE_API_KEY=your_gemini_api_key_here
### 5. Run the app
```bash
streamlit run app.py
```

---

## Usage

1. Open the app in browser at `http://localhost:8501`
2. Enter any website URL in the sidebar
3. Click **Load Website**
4. Wait for scraping and indexing to complete
5. Ask any question about the website content
6. Get accurate answers with source citations!

---

## API Keys

| API        | Where to Get       | Free Limit          |
|-----       |-------------       |------------         |
| Groq API   | console.groq.com   | 14,400 requests/day |
| Gemini API | aistudio.google.com| 20 requests/day     |

---

## Solution Approach

The project uses a RAG (Retrieval Augmented Generation) architecture:

- **Scraping** — BeautifulSoup4 recursively crawls websites staying within the same domain
- **Chunking** — LangChain splits text into 1000-word chunks with 200-word overlap to preserve context
- **Embedding** — HuggingFace `all-MiniLM-L6-v2` model converts chunks to semantic vectors locally (no API needed)
- **Retrieval** — FAISS finds the top 3 most semantically similar chunks for any question
- **Generation** — Groq (LLaMA 3.1) generates accurate answers using only retrieved content
- **Fallback** — If Groq fails, Gemini 2.5 Flash automatically takes over

---

## Status

✅ Phase 1 — Web scraping pipeline completed

✅ Phase 2 — Recursive crawling with smart link filtering

✅ Phase 3 — Text chunking and FAISS vector storage

✅ Phase 4 — AI integration with Groq and Gemini fallback

✅ Phase 5 — Streamlit chat UI with source citations and confidence scores