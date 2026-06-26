import os
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from dotenv import load_dotenv

load_dotenv()


class Embedder:
    """
    Converts text chunks into embeddings and stores them in FAISS.
    """

    def __init__(self):
        # Load Google embeddings using Gemini API key
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001",
            google_api_key=os.getenv("GEMINI_API_KEY")
        )

    def build_vectorstore(self, chunks):
        """
        Takes list of chunks and builds a FAISS vector store.
        """
        # Extract just the text from each chunk
        texts = [chunk["text"] for chunk in chunks]

        # Extract source info for each chunk
        metadatas = [
            {
                "source": chunk["source"],
                "title": chunk["title"]
            }
            for chunk in chunks
        ]

        print("Building FAISS index... please wait")

        # Create FAISS vector store
        vectorstore = FAISS.from_texts(
            texts,
            embedding=self.embeddings,
            metadatas=metadatas
        )

        print("FAISS index built successfully!")

        return vectorstore

    def save_vectorstore(self, vectorstore, path="data/faiss_index"):
        """
        Save FAISS index to disk so we don't rebuild every time.
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