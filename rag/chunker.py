from langchain_text_splitters import RecursiveCharacterTextSplitter


class TextChunker:
    """
    Splits large text into smaller overlapping chunks for RAG processing.
    """

    def __init__(self, chunk_size=1000, chunk_overlap=200):
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )

    def chunk_pages(self, pages):
        """
        Takes list of crawled pages and returns list of chunks with source info.
        """
        all_chunks = []

        for page in pages:
            # Skip pages with very little text
            if len(page["text"].strip()) < 100:
                continue

            # Split page text into chunks
            chunks = self.splitter.split_text(page["text"])

            for chunk in chunks:
                all_chunks.append({
                    "text": chunk,
                    "source": page["url"],
                    "title": page["title"]
                })

        print(f"Total chunks created: {len(all_chunks)}")

        return all_chunks