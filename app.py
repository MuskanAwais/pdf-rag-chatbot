import streamlit as st
import uuid
import time

st.set_page_config(page_title="RAG ChatGPT Clone", layout="wide")

# -------------------------
# CONFIG
# -------------------------
MAX_PDF_SIZE_MB = 10

# -------------------------
# SESSION STATE
# -------------------------
if "device_id" not in st.session_state:
    st.session_state.device_id = str(uuid.uuid4())

if "pdf_id" not in st.session_state:
    st.session_state.pdf_id = None

if "chats" not in st.session_state:
    st.session_state.chats = {}   # chat_id -> messages

if "current_chat" not in st.session_state:
    st.session_state.current_chat = str(uuid.uuid4())

if st.session_state.current_chat not in st.session_state.chats:
    st.session_state.chats[st.session_state.current_chat] = []


# -------------------------
# IMPORTS
# -------------------------
from core.pdf_loader import extract_text_from_pdf
from core.chunker import chunk_text
from core.embeddings import embed_chunks
from core.storage import store_pdf_metadata, store_chunks
from core.chat_engine import ask_question


# -------------------------
# SIDEBAR (ChatGPT style)
# -------------------------
with st.sidebar:

    st.title("💬 Conversations")

    # NEW CHAT BUTTON
    if st.button("➕ New Chat"):
        new_chat = str(uuid.uuid4())
        st.session_state.current_chat = new_chat
        st.session_state.chats[new_chat] = []
        st.rerun()

    st.divider()

    # CHAT LIST
    for chat_id in list(st.session_state.chats.keys())[::-1]:
        if st.button(f"🗂 Chat {chat_id[:6]}", key=chat_id):
            st.session_state.current_chat = chat_id
            st.rerun()

    st.divider()

    # PDF STATUS
    if st.session_state.pdf_id:
        st.success("📄 PDF Loaded")
    else:
        st.warning("⚠️ No PDF")



# -------------------------
# TITLE
# -------------------------
st.title("📄 RAG ChatGPT Style PDF Assistant")


# -------------------------
# PDF UPLOAD
# -------------------------
uploaded_file = st.file_uploader("Upload PDF first", type=["pdf"])

if uploaded_file and st.session_state.pdf_id is None:

    file_size_mb = uploaded_file.size / (1024 * 1024)
    st.info(f"📦 File Size: {file_size_mb:.2f} MB")

    if file_size_mb > MAX_PDF_SIZE_MB:
        st.error("❌ File too large")
        st.stop()

    status = st.status("🚀 Processing PDF...", expanded=True)
    progress = st.progress(0)

    # STEP 1
    status.update(label="📄 Reading PDF", state="running")
    pages = extract_text_from_pdf(uploaded_file)
    progress.progress(25)

    # STEP 2
    status.update(label="✂️ Chunking text", state="running")
    chunks = chunk_text(pages)
    progress.progress(50)

    # STEP 3
    status.update(label="🧠 Embeddings", state="running")
    embedded_chunks = embed_chunks(chunks)
    progress.progress(75)

    # STEP 4
    status.update(label="💾 Saving", state="running")

    pdf_id = store_pdf_metadata(
        filename=uploaded_file.name,
        file_size=uploaded_file.size,
        page_count=len(pages),
        device_id=st.session_state.device_id
    )

    store_chunks(embedded_chunks, pdf_id, st.session_state.device_id)

    st.session_state.pdf_id = pdf_id

    progress.progress(100)
    status.update(label="✅ Ready!", state="complete")


# -------------------------
# BLOCK IF NO PDF
# -------------------------
if not st.session_state.pdf_id:
    st.warning("📌 Please upload a PDF first to start chatting")
    st.stop()


# -------------------------
# CHAT AREA (WhatsApp / ChatGPT STYLE)
# -------------------------
chat_id = st.session_state.current_chat
messages = st.session_state.chats[chat_id]


# SHOW MESSAGES (center like ChatGPT)
for msg in messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])


# INPUT BOX
user_input = st.chat_input("Ask something about your document...")

if user_input:

    # SAVE USER MESSAGE
    messages.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.write(user_input)

    # AI RESPONSE
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):

            answer = ask_question(
                user_input,
                st.session_state.pdf_id,
                st.session_state.device_id,
                chat_id
            )

            st.write(answer)

    # SAVE AI MESSAGE
    messages.append({"role": "assistant", "content": answer})