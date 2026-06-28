import streamlit as st
from fpdf import FPDF
import base64
import html

from scraper.crawler import WebsiteCrawler
from rag.chunker import TextChunker
from rag.embedder import Embedder
from rag.retriever import Retriever
from rag.generator import AnswerGenerator
from utils.url_utils import normalize_url

# ──────────────────────────────────────────────────────────────────────────────
# Page config
# ──────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AskTheWeb — AI Website Assistant",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ──────────────────────────────────────────────────────────────────────────────
# CSS
# ──────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@500;600;700;800&family=Inter:wght@400;500;600&display=swap');

:root{
  --bg:#f6f7fb;
  --bg-soft:#eef1f8;
  --surface:#ffffff;
  --border:#e6e8f0;
  --border-soft:#edeef5;
  --text:#161827;
  --text-soft:#5b5f73;
  --text-faint:#9698ab;
  --primary:#0f766e;
  --primary-dark:#0b5d56;
  --primary-light:#e6f5f3;
  --shadow-sm:0 1px 2px rgba(16,24,40,0.05);
  --shadow-md:0 6px 16px rgba(16,24,40,0.07);
  --shadow-lg:0 14px 30px rgba(16,24,40,0.10);
  --radius-sm:10px;
  --radius-md:14px;
  --radius-lg:20px;
  --radius-pill:999px;
}

html, body, [class*="css"]{ font-family:'Inter', sans-serif !important; }

/* ── Hide only footer and the Deploy button text — nothing else ── */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }

/* Hide ONLY the Deploy button by targeting its text content precisely */
/* This hides the deploy button but keeps the sidebar toggle (>>) intact */
[data-testid="stBaseButton-header"] { display: none !important; }

::-webkit-scrollbar{ width:8px; height:8px; }
::-webkit-scrollbar-thumb{ background:#d7dae6; border-radius:8px; }
::-webkit-scrollbar-thumb:hover{ background:#c2c6d6; }

@keyframes fadeInUp{ from{opacity:0; transform:translateY(10px);} to{opacity:1; transform:translateY(0);} }
@keyframes pulseDot{ 0%{box-shadow:0 0 0 0 rgba(15,118,110,.45);} 70%{box-shadow:0 0 0 7px rgba(15,118,110,0);} 100%{box-shadow:0 0 0 0 rgba(15,118,110,0);} }
@keyframes bounceDot{ 0%,80%,100%{ transform:scale(.55); opacity:.45;} 40%{ transform:scale(1); opacity:1;} }

.stApp {
  background: radial-gradient(circle at 0% 0%, #eef6f5 0%, var(--bg) 42%);
}

/* ── SIDEBAR ── */
[data-testid="stSidebar"] {
  min-width: 300px !important;
  max-width: 340px !important;
}
[data-testid="stSidebar"] > div {
  background: var(--surface) !important;
  border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] [data-testid="stSidebarContent"] {
  padding: 1.4rem 1.2rem 1.5rem !important;
  background: var(--surface) !important;
}
[data-testid="stSidebar"] p { color: var(--text) !important; font-size: 15px !important; }
[data-testid="stSidebar"] label { color: var(--text) !important; font-size: 15px !important; }
[data-testid="stSidebar"] .stMarkdown { color: var(--text) !important; }

/* ── Main content ── */
.main .block-container{
  padding: 1.6rem 3rem 3rem !important;
  max-width: 920px;
}

/* ── Top bar ── */
.atw-topbar{
  display:flex; align-items:center; justify-content:space-between;
  padding-bottom:1.1rem; margin-bottom:1.3rem;
  border-bottom:1px solid var(--border-soft);
}
.atw-brand{ display:flex; align-items:center; gap:14px; }
.atw-logo{
  width:48px; height:48px; border-radius:14px;
  background:linear-gradient(135deg,var(--primary),#14b8a6);
  display:flex; align-items:center; justify-content:center;
  font-size:22px; color:#fff; box-shadow:var(--shadow-md);
}
.atw-title{
  font-family:'Plus Jakarta Sans', sans-serif;
  font-size:24px; font-weight:800; color:var(--text); letter-spacing:-0.4px;
}
.atw-subtitle{ font-size:14px; color:var(--text-soft); margin-top:-1px; }
.atw-status{
  display:flex; align-items:center; gap:7px; font-size:13px; font-weight:600;
  padding:7px 15px; border-radius:var(--radius-pill); white-space:nowrap;
}
.atw-status.ready{ background:var(--primary-light); color:var(--primary-dark); }
.atw-status.idle{ background:#f1f2f6; color:var(--text-faint); }
.dot{ width:8px; height:8px; border-radius:50%; background:currentColor; display:inline-block; }
.dot.live{ animation:pulseDot 1.7s infinite; }

/* ── Sidebar labels ── */
.atw-side-label{
  font-size:12px; font-weight:700; letter-spacing:0.9px; color:var(--text-faint);
  text-transform:uppercase; margin:0.4rem 0 0.8rem;
}
.atw-side-foot{
  font-size:12px; color:var(--text-faint); text-align:center; margin-top:1.5rem;
  padding-top:1rem; border-top:1px solid var(--border-soft);
}
.stat-row{ display:flex; gap:8px; margin:0.7rem 0; }
.stat-chip{
  background:var(--bg-soft); border:1px solid var(--border-soft); border-radius:10px;
  padding:8px 12px; font-size:12.5px; color:var(--text-soft); flex:1; text-align:center;
}
.stat-chip b{ color:var(--primary-dark); font-size:15px; display:block; }
.url-item{
  background:var(--bg-soft); border:1px solid var(--border-soft); border-radius:9px;
  padding:9px 12px; font-size:12.5px; color:var(--text-soft); margin:5px 0;
  overflow:hidden; text-overflow:ellipsis; white-space:nowrap;
}

/* ── Sidebar buttons — big and easy to click ── */
[data-testid="stSidebar"] .stButton > button {
  background: linear-gradient(135deg, var(--primary), #14b8a6) !important;
  color: #fff !important;
  border: none !important;
  font-weight: 700 !important;
  font-size: 15px !important;
  padding: 0.85rem 1rem !important;
  min-height: 52px !important;
  border-radius: var(--radius-md) !important;
  box-shadow: var(--shadow-md) !important;
  letter-spacing: 0.2px;
  width: 100%;
}
[data-testid="stSidebar"] .stButton > button:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-lg) !important;
  filter: brightness(1.06);
}

/* ── Main area buttons ── */
.stButton > button{
  background:#fff; color:var(--text); border:1px solid var(--border);
  border-radius:var(--radius-pill); font-size:14px; font-weight:500;
  font-family:'Inter', sans-serif; padding:0.55rem 1.2rem;
  box-shadow:var(--shadow-sm); transition:all .2s ease;
}
.stButton > button:hover{
  border-color:var(--primary); color:var(--primary-dark);
  background:var(--primary-light); transform:translateY(-1px);
  box-shadow:var(--shadow-md);
}
.stDownloadButton > button{
  background:#fff !important; color:var(--text) !important;
  border:1px solid var(--border) !important; border-radius:var(--radius-md) !important;
  font-size:13.5px !important; font-weight:600 !important;
  padding: 0.65rem 1rem !important;
  box-shadow:var(--shadow-sm) !important;
}
.stDownloadButton > button:hover{
  border-color:var(--primary) !important; color:var(--primary-dark) !important;
}

/* ── Text input ── */
.stTextInput > div > div > input{
  background:#fff !important; border:1.5px solid var(--border) !important;
  border-radius:var(--radius-md) !important; color:var(--text) !important;
  padding:0.7rem 1rem !important; font-size:15px !important;
  font-family:'Inter', sans-serif !important;
  min-height: 48px !important;
}
.stTextInput > div > div > input::placeholder{ color:var(--text-faint) !important; }
.stTextInput > div > div > input:focus{
  border-color:var(--primary) !important;
  box-shadow:0 0 0 3px rgba(15,118,110,0.14) !important;
}

/* ── Progress bar ── */
.stProgress > div{ background:var(--bg-soft) !important; border-radius:8px; }
.stProgress > div > div > div{
  background:linear-gradient(90deg,var(--primary),#14b8a6) !important;
}

/* ── Chat input ── */
[data-testid="stChatInput"]{
  background:#fff !important; border:1px solid var(--border) !important;
  border-radius:var(--radius-lg) !important; box-shadow:var(--shadow-md) !important;
}
[data-testid="stChatInputTextArea"], [data-testid="stChatInput"] textarea{
  color:var(--text) !important; font-family:'Inter', sans-serif !important;
  font-size:15px !important;
}
[data-testid="stChatInputTextArea"]::placeholder{ color:var(--text-faint) !important; }
section[data-testid="stBottom"]{ background:var(--bg) !important; }

/* ── Alerts ── */
.stAlert{
  background:#fff !important; border:1px solid var(--border) !important;
  border-radius:var(--radius-md) !important; color:var(--text) !important;
  box-shadow:var(--shadow-sm) !important; font-size:14px !important;
}

/* ── Cards ── */
.atw-card{
  background:var(--surface); border:1px solid var(--border);
  border-radius:var(--radius-lg); box-shadow:var(--shadow-sm);
  padding:1.2rem 1.5rem; animation:fadeInUp .45s ease;
  transition:box-shadow .25s ease;
}
.atw-card:hover{ box-shadow:var(--shadow-md); }
.summary-card{
  border-left:3px solid var(--primary);
  display:flex; gap:14px; align-items:flex-start;
}
.summary-icon{
  width:38px; height:38px; min-width:38px; border-radius:10px;
  background:var(--primary-light); color:var(--primary-dark);
  display:flex; align-items:center; justify-content:center; font-size:18px;
}
.summary-label{
  font-size:12px; font-weight:700; letter-spacing:0.8px; color:var(--primary-dark);
  text-transform:uppercase; margin-bottom:5px;
}
.summary-text{ font-size:15px; color:var(--text); line-height:1.75; }
.chips-label{
  font-size:12px; font-weight:700; letter-spacing:0.8px; color:var(--text-faint);
  text-transform:uppercase; margin:1.2rem 0 0.7rem;
}

/* ── Empty state ── */
.empty-wrap{ text-align:center; padding:3rem 1rem 1rem; animation:fadeInUp .5s ease; }
.empty-icon{
  width:70px; height:70px; border-radius:20px; margin:0 auto 1.2rem;
  background:linear-gradient(135deg,var(--primary-light),#fff);
  display:flex; align-items:center; justify-content:center; font-size:32px;
  box-shadow:var(--shadow-sm);
}
.empty-title{
  font-family:'Plus Jakarta Sans', sans-serif;
  font-size:22px; font-weight:800; color:var(--text); margin-bottom:0.5rem;
}
.empty-desc{
  font-size:15px; color:var(--text-soft); max-width:440px;
  margin:0 auto 2rem; line-height:1.8;
}
.feature-grid{ display:flex; gap:16px; justify-content:center; flex-wrap:wrap; }
.feature-card{
  background:#fff; border:1px solid var(--border); border-radius:var(--radius-md);
  padding:1.1rem 1.2rem; width:200px; text-align:left; box-shadow:var(--shadow-sm);
  transition:transform .2s ease, box-shadow .2s ease;
}
.feature-card:hover{ transform:translateY(-3px); box-shadow:var(--shadow-md); }
.feature-icon{ font-size:22px; margin-bottom:0.6rem; }
.feature-title{ font-size:14px; font-weight:700; color:var(--text); margin-bottom:0.3rem; }
.feature-desc{ font-size:12.5px; color:var(--text-soft); line-height:1.6; }

/* ── Chat bubbles ── */
.msg-row{ display:flex; margin:1rem 0; animation:fadeInUp .35s ease; }
.msg-row.user{ justify-content:flex-end; }
.msg-row.ai{ justify-content:flex-start; gap:10px; }
.avatar{
  width:36px; height:36px; border-radius:11px; flex:0 0 36px;
  display:flex; align-items:center; justify-content:center; font-size:16px;
  box-shadow:var(--shadow-sm);
}
.avatar.ai{ background:linear-gradient(135deg,var(--primary),#14b8a6); color:#fff; }
.avatar.user{ background:var(--bg-soft); color:var(--text-soft); }
.bubble{ max-width:72%; padding:0.85rem 1.15rem; font-size:15px; line-height:1.7; word-wrap:break-word; }
.bubble.user{
  background:linear-gradient(135deg,var(--primary),#0d9488); color:#fff;
  border-radius:16px 16px 4px 16px; box-shadow:var(--shadow-sm);
}
.bubble.ai{
  background:#fff; border:1px solid var(--border); color:var(--text);
  border-radius:4px 16px 16px 16px; box-shadow:var(--shadow-sm);
}
.msg-meta{ display:flex; gap:6px; margin-top:7px; flex-wrap:wrap; padding-left:2px; }
.meta-pill{
  font-size:11.5px; font-weight:600; color:var(--text-soft);
  background:var(--bg-soft); border:1px solid var(--border-soft);
  padding:3px 10px; border-radius:var(--radius-pill);
}
.thinking-row{ display:flex; gap:10px; align-items:center; margin:1rem 0; animation:fadeInUp .3s ease; }
.thinking-bubble{
  background:#fff; border:1px solid var(--border); border-radius:4px 16px 16px 16px;
  padding:0.85rem 1.2rem; display:flex; gap:5px; box-shadow:var(--shadow-sm);
}
.thinking-bubble span{
  width:8px; height:8px; border-radius:50%; background:var(--primary);
  display:inline-block; animation:bounceDot 1s infinite;
}
.thinking-bubble span:nth-child(2){ animation-delay:.15s; }
.thinking-bubble span:nth-child(3){ animation-delay:.3s; }

.atw-divider{ border:none; border-top:1px solid var(--border-soft); margin:2rem 0; }
.export-title{
  font-size:12px; font-weight:700; letter-spacing:0.8px; color:var(--text-faint);
  text-transform:uppercase; margin-bottom:0.9rem;
}
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────────────
# Session state
# ──────────────────────────────────────────────────────────────────────────────
if "vectorstore" not in st.session_state:
    st.session_state.vectorstore = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "urls_loaded" not in st.session_state:
    st.session_state.urls_loaded = []
if "summary" not in st.session_state:
    st.session_state.summary = None
if "suggested_questions" not in st.session_state:
    st.session_state.suggested_questions = []
if "pages_count" not in st.session_state:
    st.session_state.pages_count = 0
if "chunks_count" not in st.session_state:
    st.session_state.chunks_count = 0


def short_source(url):
    return str(url).replace("https://", "").replace("http://", "")


def ask_question(question_text):
    thinking_ph = st.empty()
    thinking_ph.markdown("""
    <div class="thinking-row">
        <div class="avatar ai">✦</div>
        <div class="thinking-bubble"><span></span><span></span><span></span></div>
    </div>
    """, unsafe_allow_html=True)

    retriever = Retriever(st.session_state.vectorstore)
    chunks = retriever.get_relevant_chunks(question_text)

    generator = AnswerGenerator()
    result = generator.generate(question_text, chunks)

    answer = result["answer"]
    model_used = result["model_used"]
    source = chunks[0]["source"] if chunks else "Unknown"
    confidence = chunks[0]["confidence"] if chunks else 0

    thinking_ph.empty()

    st.session_state.chat_history.append({
        "question": question_text,
        "answer": answer,
        "source": source,
        "model": model_used,
        "confidence": confidence
    })


# ──────────────────────────────────────────────────────────────────────────────
# Sidebar
# ──────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="atw-side-label">📥 Load Website</div>', unsafe_allow_html=True)

    url_input = st.text_input(
        "Website URL",
        placeholder="https://example.com",
        label_visibility="collapsed"
    )

    load_button = st.button("🚀  Load Website", use_container_width=True)

    if load_button:
        if not url_input.strip():
            st.warning("Enter a URL first.")
        else:
            try:
                url = normalize_url(url_input)
                progress = st.progress(0)
                status = st.empty()

                status.text("Scraping website...")
                progress.progress(20)

                crawler = WebsiteCrawler()

                def update_progress(msg):
                    status.text(msg)

                pages = crawler.crawl(url, progress_callback=update_progress)

                if len(pages) == 0:
                    st.error("Could not scrape this website. Try another URL.")
                else:
                    progress.progress(50)
                    status.text("Creating chunks...")

                    chunker = TextChunker()
                    chunks = chunker.chunk_pages(pages)

                    if len(chunks) == 0:
                        st.error("No readable content found. Try another URL.")
                    else:
                        progress.progress(70)
                        status.text("Building knowledge base...")

                        embedder = Embedder()
                        vectorstore = embedder.build_vectorstore(chunks)

                        progress.progress(100)
                        status.text("Ready!")

                        st.session_state.vectorstore = vectorstore
                        st.session_state.urls_loaded.append(url)
                        st.session_state.pages_count = len(pages)
                        st.session_state.chunks_count = len(chunks)

                        summary_chunks = chunker.chunk_pages(pages[:2])[:3]
                        all_chunks_sample = chunks[:5]  # Use first 5 chunks from ALL pages
                        if summary_chunks:
                            generator = AnswerGenerator()
                            summary_result = generator.generate(
                                "Give a brief 3-4 line summary of what this website is about.",
                                summary_chunks
                            )
                            st.session_state.summary = summary_result['answer']

                            questions_result = generator.generate(
                                "Based on the content below, suggest exactly 3 simple factual questions that can be directly answered from this content. The questions must have clear answers in the text.Return only 3 questions as a numbered list. No extra text.",
                                all_chunks_sample
                            )
                            raw = questions_result['answer']
                            lines = [l.strip() for l in raw.split('\n') if l.strip()]
                            cleaned = []
                            for line in lines:
                                for prefix in ['1.', '2.', '3.', '1)', '2)', '3)']:
                                    if line.startswith(prefix):
                                        line = line[len(prefix):].strip()
                                if '?' in line and len(line)<120 and not line.startswith('('):
                                  cleaned.append(line)
                            st.session_state.suggested_questions = cleaned[:3]

                        st.success(f"Loaded {len(pages)} pages!")

            except ValueError as e:
                st.error(f"{e}")
            except Exception as e:
                st.error(f"Something went wrong: {e}")

    if st.session_state.urls_loaded:
        st.markdown('<div class="atw-side-label" style="margin-top:1.4rem;">✅ Loaded Sources</div>', unsafe_allow_html=True)
        for u in st.session_state.urls_loaded:
            st.markdown(f'<div class="url-item">🔗 {short_source(u)}</div>', unsafe_allow_html=True)

        st.markdown(f"""
        <div class="stat-row">
            <div class="stat-chip"><b>{st.session_state.pages_count}</b>pages</div>
            <div class="stat-chip"><b>{st.session_state.chunks_count}</b>chunks</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height:0.8rem;'></div>", unsafe_allow_html=True)

    if st.button("🗑️  Clear All", use_container_width=True):
        st.session_state.chat_history = []
        st.session_state.vectorstore = None
        st.session_state.urls_loaded = []
        st.session_state.summary = None
        st.session_state.suggested_questions = []
        st.session_state.pages_count = 0
        st.session_state.chunks_count = 0
        st.rerun()

    st.markdown('<div class="atw-side-foot">Built with RAG · FAISS · LLM</div>', unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────────────────────
# Top bar
# ──────────────────────────────────────────────────────────────────────────────
status_class = "ready" if st.session_state.vectorstore is not None else "idle"
status_text = "Knowledge base ready" if st.session_state.vectorstore is not None else "No source loaded"
dot_class = "live" if st.session_state.vectorstore is not None else ""

st.markdown(f"""
<div class="atw-topbar">
    <div class="atw-brand">
        <div class="atw-logo">🌐</div>
        <div>
            <div class="atw-title">AskTheWeb</div>
            <div class="atw-subtitle">AI assistant for any website, powered by RAG</div>
        </div>
    </div>
    <div class="atw-status {status_class}"><span class="dot {dot_class}"></span>{status_text}</div>
</div>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────────────
# Main content
# ──────────────────────────────────────────────────────────────────────────────
if st.session_state.vectorstore is None:
    st.markdown("""
    <div class="empty-wrap">
        <div class="empty-icon">🌐</div>
        <div class="empty-title">No website loaded yet</div>
        <div class="empty-desc">Paste any website URL in the sidebar and load it to start asking questions grounded in its real content.</div>
        <div class="feature-grid">
            <div class="feature-card">
                <div class="feature-icon">🌍</div>
                <div class="feature-title">Any Website</div>
                <div class="feature-desc">Crawls and indexes pages from the URL you provide.</div>
            </div>
            <div class="feature-card">
                <div class="feature-icon">💬</div>
                <div class="feature-title">Ask Naturally</div>
                <div class="feature-desc">Chat like you would with a person — no special syntax.</div>
            </div>
            <div class="feature-card">
                <div class="feature-icon">📌</div>
                <div class="feature-title">Cited Answers</div>
                <div class="feature-desc">Every answer is traced back to its source page.</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

else:
    if st.session_state.summary:
        st.markdown(f"""
        <div class="atw-card summary-card">
            <div class="summary-icon">📋</div>
            <div>
                <div class="summary-label">Website Summary</div>
                <div class="summary-text">{html.escape(st.session_state.summary)}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    if st.session_state.suggested_questions:
        st.markdown('<div class="chips-label">✨ Suggested Questions</div>', unsafe_allow_html=True)
        cols = st.columns(len(st.session_state.suggested_questions))
        for i, q in enumerate(st.session_state.suggested_questions):
            with cols[i]:
                if st.button(q, key=f"chip_{i}", use_container_width=True):
                    ask_question(q)
                    st.rerun()

    if st.session_state.chat_history:
        chat_blocks = []
        for i, chat in enumerate(st.session_state.chat_history):
            q_safe = html.escape(chat["question"])
            a_safe = html.escape(chat["answer"])

            meta_html = f'<span class="meta-pill">📄 {html.escape(short_source(chat["source"])[:40])}</span>'
            meta_html += f'<span class="meta-pill">🤖 {html.escape(str(chat["model"]))}</span>'
            confidence = chat.get("confidence", 0)
            conf_display = f"{confidence:.1f}" if isinstance(confidence, float) else confidence
            meta_html += f'<span class="meta-pill">📊 {conf_display}%</span>'

            span_id = f"ai-ans-{i}"
            chat_blocks.append(
                f'<div class="msg-row user"><div class="bubble user">{q_safe}</div></div>'
                f'<div class="msg-row ai"><div class="avatar ai">✦</div><div>'
                f'<div class="bubble ai"><span id="{span_id}">{a_safe}</span></div>'
                f'<div class="msg-meta">{meta_html}</div></div></div>'
            )
        chat_blocks.append('<div id="atw-bottom-anchor"></div>')
        st.markdown("".join(chat_blocks), unsafe_allow_html=True)

        last_idx = len(st.session_state.chat_history) - 1
        last_answer = st.session_state.chat_history[last_idx]["answer"]
        b64_answer = base64.b64encode(last_answer.encode("utf-8")).decode("ascii")
        last_span_id = f"ai-ans-{last_idx}"

        st.markdown(f"""
        <img src="data:," style="display:none" onerror="
            this.remove();
            try{{
                var bin = atob('{b64_answer}');
                var bytes = new Uint8Array(bin.length);
                for (var k = 0; k < bin.length; k++) {{ bytes[k] = bin.charCodeAt(k); }}
                var full = new TextDecoder('utf-8').decode(bytes);
                var el = document.getElementById('{last_span_id}');
                if (el) {{
                    el.textContent = '';
                    var idx = 0;
                    var iv = setInterval(function() {{
                        if (idx > full.length) {{ clearInterval(iv); return; }}
                        el.textContent = full.slice(0, idx);
                        idx++;
                    }}, 9);
                }}
                var anchor = document.getElementById('atw-bottom-anchor');
                if (anchor) {{ anchor.scrollIntoView({{behavior:'smooth', block:'end'}}); }}
            }} catch(e) {{}}
        ">
        """, unsafe_allow_html=True)

    question = st.chat_input("Ask anything about the loaded website...")

    if question:
        if len(question.strip()) < 3:
            st.warning("Enter a valid question.")
        else:
            ask_question(question)
            st.rerun()

    if len(st.session_state.chat_history) > 0:
        st.markdown('<hr class="atw-divider">', unsafe_allow_html=True)
        st.markdown('<div class="export-title">📤 Export Conversation</div>', unsafe_allow_html=True)

        current_history = st.session_state.chat_history.copy()

        chat_text = "AskTheWeb — Chat History\n"
        chat_text += "=" * 50 + "\n\n"
        for chat in current_history:
            chat_text += f"Q: {chat['question']}\n"
            chat_text += f"A: {chat['answer']}\n"
            chat_text += f"Source: {chat['source']}\n"
            chat_text += "-" * 50 + "\n\n"

        col1, col2 = st.columns(2)

        with col1:
            st.download_button(
                label="📥 Download TXT",
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

                pdf.set_font("Helvetica", style="B", size=14)
                pdf.cell(0, 10, text="AskTheWeb - Chat History", ln=True)
                pdf.ln(5)

                for i, chat in enumerate(current_history):
                    pdf.set_font("Helvetica", style="B", size=11)
                    q_clean = f"Q{i+1}: {chat['question']}".encode('latin-1', 'replace').decode('latin-1')
                    pdf.multi_cell(0, 8, text=q_clean)
                    pdf.ln(2)

                    pdf.set_font("Helvetica", size=10)
                    a_clean = f"A: {chat['answer']}".encode('latin-1', 'replace').decode('latin-1')
                    pdf.multi_cell(0, 8, text=a_clean)
                    pdf.ln(2)

                    pdf.set_font("Helvetica", style="I", size=9)
                    s_clean = f"Source: {chat['source']}".encode('latin-1', 'replace').decode('latin-1')
                    pdf.multi_cell(0, 6, text=s_clean)
                    pdf.ln(5)

                pdf_bytes = pdf.output()

                st.download_button(
                    label="📄 Download PDF",
                    data=bytes(pdf_bytes),
                    file_name="asktheweb_chat.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )

            except Exception as e:
                st.warning(f"PDF failed: {e}")