import streamlit as st
from fpdf import FPDF
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

                # Auto generate website summary
                with st.spinner("Generating website summary..."):
                    summary_chunks = chunker.chunk_pages(pages[:2])[:3]
                    if summary_chunks:
                        generator = AnswerGenerator()
                        summary_result = generator.generate(
                            "Give a brief 3-4 line summary of what this website is about.",
                            summary_chunks
                        )
                        st.info(f"📋 **Website Summary:** {summary_result['answer']}")

                        # Auto suggest questions
                        with st.spinner("Generating suggested questions..."):
                            questions_result = generator.generate(
                                "Based on the content, suggest exactly 3 interesting questions a user might ask. Return only the 3 questions as a numbered list.",
                                summary_chunks
                            )
                            st.success(f"💡 **Suggested Questions:**\n{questions_result['answer']}")

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

    # Export section - shown below chat after all questions
    if len(st.session_state.chat_history) > 0:
        st.divider()
        st.markdown("### 📥 Export Chat History")
        st.caption("💡 All your questions and answers are included!")

        current_history = st.session_state.chat_history.copy()

        # Build chat text
        chat_text = "AskTheWeb - Chat History\n"
        chat_text += "=" * 50 + "\n\n"
        for chat in current_history:
            chat_text += f"Q: {chat['question']}\n"
            chat_text += f"A: {chat['answer']}\n"
            chat_text += f"Source: {chat['source']}\n"
            chat_text += "-" * 50 + "\n\n"

        col1, col2 = st.columns(2)

        with col1:
            st.download_button(
                label="📥 Download as TXT",
                data=chat_text,
                file_name="asktheweb_chat.txt",
                mime="text/plain",
                use_container_width=True
            )

        with col2:
            try:
                pdf = FPDF()
                pdf.add_page()
                pdf.set_margins(15, 15, 15)
                pdf.set_auto_page_break(auto=True, margin=15)

                # Title
                pdf.set_font("Helvetica", style="B", size=14)
                pdf.cell(0, 10, text="AskTheWeb - Chat History", ln=True)
                pdf.ln(5)

                for i, chat in enumerate(current_history):
                    # Question
                    pdf.set_font("Helvetica", style="B", size=11)
                    q_clean = f"Q{i+1}: {chat['question']}".encode(
                        'latin-1', 'replace').decode('latin-1')
                    pdf.multi_cell(0, 8, text=q_clean)
                    pdf.ln(2)

                    # Answer
                    pdf.set_font("Helvetica", size=10)
                    a_clean = f"A: {chat['answer']}".encode(
                        'latin-1', 'replace').decode('latin-1')
                    pdf.multi_cell(0, 8, text=a_clean)
                    pdf.ln(2)

                    # Source
                    pdf.set_font("Helvetica", style="I", size=9)
                    s_clean = f"Source: {chat['source']}".encode(
                        'latin-1', 'replace').decode('latin-1')
                    pdf.multi_cell(0, 6, text=s_clean)
                    pdf.ln(5)

                pdf_bytes = pdf.output()

                st.download_button(
                    label="📄 Download as PDF",
                    data=bytes(pdf_bytes),
                    file_name="asktheweb_chat.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )

            except Exception as e:
                st.warning(f"PDF failed: {e}")