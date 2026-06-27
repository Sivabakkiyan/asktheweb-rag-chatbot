class Retriever:
    """
    Searches FAISS vector store and retrieves most relevant chunks.
    """

    def __init__(self, vectorstore, top_k=3):
        self.vectorstore = vectorstore
        # top_k = how many chunks to retrieve
        self.top_k = top_k

    def get_relevant_chunks(self, question):
        """
        Takes user question and returns most relevant chunks with sources.
        """
        # Search FAISS for similar chunks
        results = self.vectorstore.similarity_search_with_score(
            question,
            k=self.top_k
        )

        chunks = []

        for doc, score in results:
            chunks.append({
                "text": doc.page_content,
                "source": doc.metadata.get("source", "Unknown"),
                "title": doc.metadata.get("title", "Unknown"),
                # Convert score to confidence percentage
                "confidence": round((1 / (1 + score)) * 100, 2)
            })

        return chunks