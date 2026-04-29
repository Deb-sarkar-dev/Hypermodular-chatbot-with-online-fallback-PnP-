#  Modular RAG Assistant with Persistent Memory

##  Overview

This project is a localized, Object-Oriented Retrieval-Augmented Generation (RAG) system built with **Llama 3.2**, **ChromaDB**, and **Flask**. Designed as a modular, plug-and-play solution, it allows any website to embed a smart chat widget that automatically ingests site-specific context and provides intelligent answers. 

A core focus of this project is **Self-Learning and Persistent Memory**: the system can fall back to Wikipedia for general knowledge and automatically cache new knowledge locally, reducing external API reliance and improving latency over time.

---

##  Architecture & Component Breakdown

### 1. `app.py` (The Backend API)
A lightweight Flask server that handles CORS and exposes three primary RESTful endpoints:
- **`POST /ingest`**: Receives scraped webpage text from the frontend and passes it to the RAG engine for chunking and vectorization.
- **`POST /chat`**: Receives user queries, orchestrates the retrieval process, and returns the generated LLM response along with the data source (local vs. wikipedia).
- **`POST /feedback`**: Captures user upvotes/downvotes. Positive feedback triggers the system to permanently store the interaction.

### 2. `rag_engine.py` (The Core Logic)
An Object-Oriented Python module (`RAGEngine` class) handling the heavy lifting:
- **LLM Integration**: Uses Langchain to interface with the local **Ollama** instance running Llama 3.2.
- **Vector Database**: Manages a persistent **ChromaDB** client. Text is chunked via `RecursiveCharacterTextSplitter` and embedded using `Sentence-Transformers (all-MiniLM-L6-v2)`.
- **Wikipedia Fallback**: Uses the `wikipedia` Python library to fetch summaries if local domain context is insufficient.
- **Self-Learning Mechanism**: The `store_learned_interaction` method saves successful Wikipedia answers and user-upvoted interactions back into ChromaDB for instant future retrieval.

### 3. `static/chat-widget.js` (The Frontend Integration)
A vanilla JavaScript chat widget featuring a modern, glassmorphism UI. 
- **Zero-Config Scraping**: Automatically reads the DOM (`document.body.innerText`), cleans the text, and sends it to `/ingest` when initialized.
- **Multi-Tenant Support**: Automatically detects the current URL/domain to ensure the backend isolates knowledge strictly for that website.
- **Feedback UI**: Provides 👍/👎 buttons on AI responses to trigger the feedback loop.

---

## System Workflow: How It Works

1. **Initialization (Zero-Config Ingestion)**
   - The user loads an HTML page with the widget embedded.
   - `chat-widget.js` scrapes the visible page content and sends it to `/ingest`.
   - `RAGEngine` checks if this URL is already in ChromaDB. If not, it chunks the text, creates embeddings, and stores them under that specific domain.

2. **Query Processing & Retrieval**
   - User types a question in the widget.
   - `RAGEngine` searches the local ChromaDB for the most relevant chunks matching the user's domain.
   - If a relevant match is found (distance < 1.75), Llama 3.2 formulates an answer using this local context.

3. **Wikipedia Fallback & Persistence**
   - If no local context matches, the system queries the Wikipedia API.
   - If Wikipedia finds an answer, Llama 3.2 synthesizes it.
   - **Crucial Step**: The system immediately stores this Q&A pair in ChromaDB tagged as `wiki_fallback`. The next time someone asks the same question, it is answered instantly from local memory.

4. **Human-in-the-loop Feedback**
   - If the user upvotes an answer, the interaction is stored in ChromaDB as `user_feedback`, dynamically expanding the local knowledge base based on user satisfaction.

---

## Technology Stack

| Component | Technology Used |
| :--- | :--- |
| **Language Model** | Llama 3.2 (Locally hosted via Ollama) |
| **Vector Database** | ChromaDB (Persistent local storage) |
| **Embeddings** | Sentence-Transformers (`all-MiniLM-L6-v2`) |
| **Orchestration** | Python, Langchain |
| **Web Server** | Flask, Flask-CORS |
| **Frontend UI** | Vanilla JavaScript, CSS (No external frameworks) |

---

## Setup & Installation

### Prerequisites
1. **Python 3.8+**
2. **Ollama** installed on your system.
3. Download the Llama 3.2 model:
   ```bash
   ollama run llama3.2
   ```

### Installation Steps
1. **Clone/Navigate to the directory**:
   ```bash
   cd "chatbot + persistence+ wiki api"
   ```

2. **Set up a Virtual Environment**:
   ```bash
   python -m venv venv
   
   # Windows:
   .\venv\Scripts\activate
   # Mac/Linux:
   source venv/bin/activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Backend Server**:
   ```bash
   python app.py
   ```
   *Server will start on `http://localhost:5000`.*

---

## Local Testing & Evaluation

1. **Start the backend** (`python app.py`) and ensure Ollama is running.
2. **Open the Test Site**: Simply double-click `ecommerce-shop.html` to open it in your browser (uses `file:///`).
3. **Wait for Ingestion**: The widget will appear and silently scrape the HTML content into the local vector DB.
4. **Test Domain Knowledge**: 
   - Ask: *"What items do you have on sale?"*
   - Ask: *"Is the Quantum X1 Laptop available?"* (Notice the strict Yes/No logic enforced by the system prompt).
5. **Test Fallback & Memory**:
   - Ask a factual question: *"Who is Nikola Tesla?"* (Takes a few seconds to fetch from Wikipedia).
   - Ask it again: *"Who is Nikola Tesla?"* (Returns instantly from ChromaDB memory).
6. **Test Feedback Loop**: Click 👍 on a response to permanently embed it in the database.

---
*Developed as an academic project demonstrating advanced applied AI concepts including local inference, RAG memory persistence, and dynamic web scraping.*
