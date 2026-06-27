import streamlit as st
from scraper.crawler import WebsiteCrawler
from rag.chunker import TextChunker
from rag.embedder import Embedder
from rag.retriever import Retriever
from rag.generator import AnswerGenerator
from utils.url_utils import normalize_url

# Page config
st.set_page_config(
    page_title="AskTheWeb",
    page_icon="🌐",
    layout="wide"
)

# Title
st.title("🌐 AskTheWeb")
st.subheader("Ask anything. Get answers directly from any website.")

# Initialize session state
if "vectorstore" not in st.session_state:
    st.session_state.vectorstore = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "urls_loaded" not in st.session_state:
    st.session_state.urls_loaded = []

# Sidebar for URL input
with st.sidebar:
    st.header("📥 Load Websites")

    url_input = st.text_input(
        "Enter Website URL",
        placeholder="https://example.com"
    )

    load_button = st.button("🚀 Load Website", use_container_width=True)

    if load_button and url_input:
        try:
            url = normalize_url(url_input)

            # Progress bar
            progress = st.progress(0)
            status = st.empty()

            # Scraping
            status.text("🔄 Scraping website...")
            progress.progress(20)

            crawler = WebsiteCrawler()
            pages_scraped = []

            def update_progress(msg):
                status.text(msg)

            pages = crawler.crawl(url, progress_callback=update_progress)

            if len(pages) == 0:
                st.error("❌ Could not scrape this website. Please try another URL.")
            else:
                progress.progress(50)
                status.text("🔄 Creating chunks...")

                # Chunking
                chunker = TextChunker()
                chunks = chunker.chunk_pages(pages)

                progress.progress(70)
                status.text("🔄 Building FAISS index...")

                # Embeddings
                embedder = Embedder()
                vectorstore = embedder.build_vectorstore(chunks)

                progress.progress(100)
                status.text("✅ Website loaded successfully!")

                # Save to session
                st.session_state.vectorstore = vectorstore
                st.session_state.urls_loaded.append(url)

                st.success(f"✅ Loaded {len(pages)} pages and {len(chunks)} chunks!")

        except Exception as e:
            st.error(f"❌ Error: {e}")

    # Show loaded URLs
    if st.session_state.urls_loaded:
        st.markdown("### ✅ Loaded URLs:")
        for u in st.session_state.urls_loaded:
            st.markdown(f"- {u}")

    # Clear button
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.chat_history = []
        st.session_state.vectorstore = None
        st.session_state.urls_loaded = []
        st.rerun()

# Main chat area
if st.session_state.vectorstore is None:
    st.info("👈 Please enter a website URL in the sidebar and click Load Website to begin.")

else:
    # Show chat history
    for chat in st.session_state.chat_history:
        with st.chat_message("user"):
            st.write(chat["question"])
        with st.chat_message("assistant"):
            st.write(chat["answer"])
            st.caption(f"📄 Source: {chat['source']} | 🤖 Model: {chat['model']}")

    # Chat input
    question = st.chat_input("Ask anything about the loaded website...")

    if question:
        with st.chat_message("user"):
            st.write(question)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                # Retrieve chunks
                retriever = Retriever(st.session_state.vectorstore)
                chunks = retriever.get_relevant_chunks(question)

                # Generate answer
                generator = AnswerGenerator()
                result = generator.generate(question, chunks)

                answer = result["answer"]
                model_used = result["model_used"]
                source = chunks[0]["source"] if chunks else "Unknown"
                confidence = chunks[0]["confidence"] if chunks else 0

                st.write(answer)
                st.caption(
                    f"📄 Source: {source} | "
                    f"🤖 Model: {model_used} | "
                    f"📊 Confidence: {confidence}%"
                )

        # Save to chat history
        st.session_state.chat_history.append({
            "question": question,
            "answer": answer,
            "source": source,
            "model": model_used
        })