# Modular RAG Assistant with Self-Learning Memory

An Object-Oriented Retrieval-Augmented Generation (RAG) system powered by **Llama 3.2**. This project provides a plug-and-play JavaScript chat widget that can be embedded into any website to instantly create a context-aware virtual assistant.

## Features

- **Zero-Config Ingestion**: The JS widget automatically scrapes the visual text of the host website and sends it to the backend. It bypasses captchas and login walls because it reads exactly what the user sees in their DOM.
- **Context-Aware RAG**: Uses ChromaDB to store website content locally, organized by domain, ensuring the AI only answers questions relevant to the specific site it's embedded on.
- **Product Availability Logic**: Automatically detects when users ask about item availability and responds with explicit "Yes/No" answers followed by helpful context.
- **Wikipedia Fallback & Persistence**: If the local vector store cannot answer a general knowledge question, it queries Wikipedia. The answer is then **permanently cached** in ChromaDB so future identical questions are answered instantly from local memory.
- **User Feedback Loop**: Users can rate AI responses with Thumbs Up/Down. Positive feedback stores the Q&A pair in the vector database, enabling the model to learn and improve its answers over time.
- **Offline & Local Testing Support**: Fully supports `file:///` URLs, making it easy to test on local HTML files without needing a web server for the frontend.

## Technology Stack

- **Backend framework**: Python / Flask
- **LLM**: Llama 3.2 (via Ollama & Langchain)
- **Vector Database**: ChromaDB
- **Embeddings**: Sentence-Transformers (`all-MiniLM-L6-v2`)
- **Frontend**: Vanilla JavaScript & CSS (Glassmorphism design)

## Prerequisites

1. **Python 3.8+** installed.
2. **Ollama** installed on your system.
3. The **Llama 3.2** model downloaded via Ollama:
   ```bash
   ollama run llama3.2
   ```

## Installation & Setup

1. **Clone or navigate to the repository folder:**
   ```bash
   cd "chatbot + persistence+ wiki api"
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   
   # On Windows:
   .\venv\Scripts\activate
   # On Mac/Linux:
   source venv/bin/activate
   ```

3. **Install the dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Start the Flask Backend Server:**
   ```bash
   python app.py
   ```
   *The backend will run on `http://localhost:5000`.*

## How to Use & Test Locally

1. Ensure the Flask server and Ollama are running.
2. Open the included `ecommerce-shop.html` file directly in your web browser (you can just double-click it).
3. Wait a second for the chat widget to appear in the bottom right corner. In the background, it will automatically scrape the page text and send it to the backend for ingestion.
4. **Test Site Knowledge:** Ask *"What items do you have on sale?"* or *"Is the Quantum X1 Laptop available?"*
5. **Test Wikipedia Fallback:** Ask a general question like *"Who is Albert Einstein?"*.
6. **Test Persistence:** Ask the exact same general question again. The system will retrieve the answer instantly from your local ChromaDB memory instead of making another Wikipedia API request.
7. **Test Feedback:** Click the "👍" button on an AI response to store that interaction in the system's memory for future use.

##  Deploying to Production

To use this on a live website on the internet:
1. Deploy the Python backend (including ChromaDB and Ollama) to a cloud provider (e.g., AWS, Render, DigitalOcean).
2. Open `static/chat-widget.js`.
3. Change the `API_BASE` variable from `http://localhost:5000` to your new live backend URL.
4. Embed the `<script>` and `<link>` tags into the `<head>` of your live website.
