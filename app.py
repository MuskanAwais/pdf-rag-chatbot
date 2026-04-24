import streamlit as st
import uuid

st.set_page_config(page_title="RAG PDF Assistant", layout="wide")

# -------------------------
# CONFIG
# -------------------------
MAX_PDF_SIZE_MB = 3

# -------------------------
# SESSION STATE (ONLY ONCE)
# -------------------------
if "device_id" not in st.session_state:
    st.session_state.device_id = str(uuid.uuid4())

if "chats" not in st.session_state:
    st.session_state.chats = {}

if "current_chat" not in st.session_state:
    chat_id = str(uuid.uuid4())
    st.session_state.current_chat = chat_id
    st.session_state.chats[chat_id] = {
        "messages": [],
        "pdf_id": None
    }

if "last_pdf_id" not in st.session_state:
    st.session_state.last_pdf_id = None


# -------------------------
# IMPORTS (CORE)
# -------------------------
from core.pdf_loader import extract_text_from_pdf
from core.chunker import chunk_text
from core.embeddings import embed_chunks
from core.storage import store_pdf_metadata, store_chunks
from core.chat_engine import ask_question


# -------------------------
# GET CURRENT CHAT DATA
# -------------------------
chat_id = st.session_state.current_chat

if chat_id not in st.session_state.chats:
    st.session_state.chats[chat_id] = {
        "messages": [],
        "pdf_id": None
    }

chat_data = st.session_state.chats[chat_id]
messages = chat_data["messages"]


# -------------------------
# SIDEBAR (CHAT LIST + CONTROL)
# -------------------------
with st.sidebar:

    st.title("💬 Chats")

    # NEW CHAT
    if st.button("➕ New Chat"):
        new_chat = str(uuid.uuid4())
        st.session_state.current_chat = new_chat
        st.session_state.chats[new_chat] = {
            "messages": [],
            "pdf_id": None
        }
        st.rerun()

    st.divider()

    # CHAT HISTORY
    for cid in list(st.session_state.chats.keys())[::-1]:

        msgs = st.session_state.chats[cid]["messages"]
        title = msgs[0]["content"] if msgs else "New Chat"

        if st.button(f"🗂 {title[:20]}", key=cid):
            st.session_state.current_chat = cid
            st.rerun()

    st.divider()

    # PDF STATUS (per chat)
    if chat_data["pdf_id"]:
        st.success("📄 PDF Loaded for this chat")
    else:
        st.warning("⚠️ No PDF in this chat")


# -------------------------
# TITLE
# -------------------------
st.title("📄 RAG PDF Assistant")


# -------------------------
# PDF SECTION (ONLY CONTROL, NO STOP)
# -------------------------
if chat_data["pdf_id"] is None:

    st.info("📌 Upload PDF or use last PDF")

    option = st.radio("Choose PDF option:", ["Upload New PDF", "Use Last PDF"])

    if option == "Upload New PDF":

        uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])

        if uploaded_file:

            file_size_mb = uploaded_file.size / (1024 * 1024)
            st.info(f"📦 File Size: {file_size_mb:.2f} MB")

            if file_size_mb > MAX_PDF_SIZE_MB:
                st.error("❌ File too large")
            else:

                status = st.empty()
                progress = st.progress(0)

                status.info("📄 Reading PDF...")
                pages = extract_text_from_pdf(uploaded_file)
                progress.progress(30)

                status.info("✂️ Chunking...")
                chunks = chunk_text(pages)
                progress.progress(60)

                status.info("🧠 Embedding...")
                embedded = embed_chunks(chunks)
                progress.progress(85)

                status.info("💾 Saving...")

                pdf_id = store_pdf_metadata(
                    uploaded_file.name,
                    uploaded_file.size,
                    len(pages),
                    st.session_state.device_id
                )

                store_chunks(embedded, pdf_id, st.session_state.device_id)

                chat_data["pdf_id"] = pdf_id
                st.session_state.last_pdf_id = pdf_id

                progress.progress(100)
                status.success("✅ PDF Ready!")

    else:
        if st.session_state.last_pdf_id:
            chat_data["pdf_id"] = st.session_state.last_pdf_id
            st.success("📄 Using last PDF")
        else:
            st.warning("⚠️ No previous PDF found")


# -------------------------
# CHAT UI (CENTER LIKE)
# -------------------------
st.subheader("💬 Chat")

for msg in messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# -------------------------
# INPUT BOX (ALWAYS FIXED)
# -------------------------
user_input = st.chat_input("Ask something about your PDF...")

if user_input:

    # SAVE USER MESSAGE
    messages.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.write(user_input)

    # -------------------------
    # RAG ANSWER
    # -------------------------
    if not chat_data["pdf_id"]:
        answer = "⚠️ Please upload a PDF first for this chat."
    else:
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                answer = ask_question(
                    user_input,
                    chat_data["pdf_id"],
                    st.session_state.device_id,
                    chat_id
                )

    # SHOW ANSWER
    with st.chat_message("assistant"):
        st.write(answer)

    messages.append({"role": "assistant", "content": answer})