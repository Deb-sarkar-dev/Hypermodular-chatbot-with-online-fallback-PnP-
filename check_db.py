import chromadb
from chromadb.utils import embedding_functions

client = chromadb.PersistentClient(path="./chroma_db")
ef = embedding_functions.DefaultEmbeddingFunction()
collection = client.get_collection(name="knowledge_base", embedding_function=ef)

docs = collection.get()
print(f"Total documents: {len(docs['ids'])}")
print("Metadata:")
for m in docs['metadatas']:
    print(m)
