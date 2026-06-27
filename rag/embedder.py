import os
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from dotenv import load_dotenv

load_dotenv()


class Embedder:
    """
    Converts text chunks into embeddings and stores them in FAISS.
    Uses HuggingFace local embeddings - no API quota needed.
    """

    def __init__(self):
        # Free local embeddings - runs on your laptop, no quota limit
        self.embeddings = HuggingFaceEmbeddings(
            model_name="all-MiniLM-L6-v2"
        )

    def build_vectorstore(self, chunks):
        """
        Takes list of chunks and builds a FAISS vector store.
        """
        texts = [chunk["text"] for chunk in chunks]

        metadatas = [
            {
                "source": chunk["source"],
                "title": chunk["title"]
            }
            for chunk in chunks
        ]

        print("Building FAISS index... please wait")

        vectorstore = FAISS.from_texts(
            texts,
            embedding=self.embeddings,
            metadatas=metadatas
        )

        print("FAISS index built successfully!")

        return vectorstore

    def save_vectorstore(self, vectorstore, path="data/faiss_index"):
        """
        Save FAISS index to disk.
        """
        vectorstore.save_local(path)
        print(f"FAISS index saved to {path}")

    def load_vectorstore(self, path="data/faiss_index"):
        """
        Load existing FAISS index from disk.
        """
        vectorstore = FAISS.load_local(
            path,
            embeddings=self.embeddings,
            allow_dangerous_deserialization=True
        )
        print("FAISS index loaded from disk!")
        return vectorstore