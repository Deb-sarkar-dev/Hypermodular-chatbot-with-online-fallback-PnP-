import os
import uuid
import wikipedia
from langchain_community.llms import Ollama
from langchain_text_splitters import RecursiveCharacterTextSplitter
import chromadb
from chromadb.utils import embedding_functions

class RAGEngine:
    def __init__(self, model_name="llama3.2"):
        # Initialize Llama 3.2 via Ollama
        self.llm = Ollama(model=model_name)
        
        # Initialize ChromaDB
        self.chroma_client = chromadb.PersistentClient(path="./chroma_db")
        
        # Default embedding function (sentence-transformers: all-MiniLM-L6-v2)
        self.ef = embedding_functions.DefaultEmbeddingFunction()
        
        # Get or create collections
        self.collection = self.chroma_client.get_or_create_collection(
            name="knowledge_base",
            embedding_function=self.ef
        )
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50
        )

    def ingest_content(self, domain, url, content):
        """Ingests text content scraped from a website into ChromaDB."""
        # Check if already ingested (basic check by url)
        existing = self.collection.get(where={"url": url})
        if existing and len(existing['ids']) > 0:
            print(f"[{domain}] Content for {url} already ingested.")
            return True

        chunks = self.text_splitter.split_text(content)
        
        ids = [str(uuid.uuid4()) for _ in range(len(chunks))]
        metadatas = [{"domain": domain, "url": url, "type": "scraped"} for _ in range(len(chunks))]
        
        if chunks:
            self.collection.add(
                documents=chunks,
                metadatas=metadatas,
                ids=ids
            )
            print(f"[{domain}] Ingested {len(chunks)} chunks from {url}")
        return True

    def _query_wikipedia(self, query):
        """Fallback to Wikipedia if local context is insufficient."""
        try:
            print(f"Searching Wikipedia for: {query}")
            # Get a quick summary
            wiki_summary = wikipedia.summary(query, sentences=3)
            return wiki_summary
        except wikipedia.exceptions.DisambiguationError as e:
            return f"Wikipedia has multiple entries for this. Could you be more specific? For example: {', '.join(e.options[:3])}"
        except wikipedia.exceptions.PageError:
            return None
        except Exception as e:
            print(f"Wikipedia API error: {e}")
            return None

    def store_learned_interaction(self, domain, query, response, source_type="wiki_fallback"):
        """Store Wikipedia fallback or positive feedback persistently in the database."""
        doc_id = str(uuid.uuid4())
        content = f"Q: {query}\nA: {response}"
        self.collection.add(
            documents=[content],
            metadatas=[{"domain": domain, "type": source_type}],
            ids=[doc_id]
        )
        print(f"[{domain}] Stored learned interaction: {source_type}")

    def generate_response(self, domain, query):
        """Main chat generation logic."""
        # 1. Search Vector DB for domain knowledge (or previously learned interactions)
        results = self.collection.query(
            query_texts=[query],
            n_results=3,
            where={"domain": domain}
        )
        
        context_docs = []
        if results['documents'] and len(results['documents'][0]) > 0:
            distances = results['distances'][0]
            # Filter by distance (lower is closer).
            for doc, dist in zip(results['documents'][0], distances):
                if dist < 1.75:
                    context_docs.append(doc)
        
        context = "\n".join(context_docs)
        
        # 2. Check if we found relevant local context
        if context:
            # We found something locally. Could be scraped data, or a previously learned Wiki answer!
            system_prompt = (
                "You are a helpful virtual assistant for a website. "
                "Use the provided context to answer the user's question.\n"
                "CRITICAL INSTRUCTION: If the user is asking if an item or product is available, "
                "you MUST start your response with 'Yes' or 'No', and then provide a brief explanation or details to be helpful.\n\n"
                f"Context:\n{context}"
            )
            
            prompt = f"{system_prompt}\n\nUser Query: {query}\nResponse:"
            response = self.llm.invoke(prompt)
            return response, "local"
            
        else:
            # 3. Fallback to Wikipedia
            wiki_content = self._query_wikipedia(query)
            
            if wiki_content:
                system_prompt = (
                    "You are a virtual assistant for a website. The user's question was not found in the website's content. "
                    "You performed a Wikipedia search and found the following context. "
                    "CRITICAL INSTRUCTION: If the user is asking about the website's specific services, policies, or products (like shipping, pricing, returns, or features), "
                    "you MUST reply that you do not have that information, and do NOT use the Wikipedia context. "
                    "Only use the Wikipedia context if the user is asking a general knowledge or factual question.\n\n"
                    f"Wikipedia Context:\n{wiki_content}"
                )
                prompt = f"{system_prompt}\n\nUser Query: {query}\nResponse:"
                response = self.llm.invoke(prompt)
                
                # 4. Self-Learning: Store this answer locally so we don't need Wikipedia next time!
                self.store_learned_interaction(domain, query, response, source_type="wiki_fallback")
                
                return response, "wikipedia"
            else:
                return "I'm sorry, I dont know about that.", "none"
