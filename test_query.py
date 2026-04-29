from rag_engine import RAGEngine

rag = RAGEngine()
query = "what items do you have on sale and how many in numbers?"
results = rag.collection.query(
    query_texts=[query],
    n_results=3,
    where={"domain": ""}
)
print("Distances:", results['distances'])
print("Documents:", results['documents'])
