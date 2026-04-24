import uuid
from core.supabase_client import supabase


# =========================================================
# CHAT SYSTEM
# =========================================================

def create_chat(device_id):
    chat_id = str(uuid.uuid4())

    supabase.table("chats").insert({
        "chat_id": chat_id,
        "device_id": device_id,
        "title": "New Chat",
        "pdf_id": None
    }).execute()

    return chat_id


def get_chats(device_id):
    res = supabase.table("chats") \
        .select("*") \
        .eq("device_id", device_id) \
        .order("created_at", desc=True) \
        .execute()

    return res.data


def attach_pdf_to_chat(chat_id, pdf_id):
    supabase.table("chats") \
        .update({"pdf_id": pdf_id}) \
        .eq("chat_id", chat_id) \
        .execute()


# =========================================================
# MESSAGES
# =========================================================

def save_message(chat_id, role, content):
    supabase.table("messages").insert({
        "id": str(uuid.uuid4()),
        "chat_id": chat_id,
        "role": role,
        "content": content
    }).execute()


def get_messages(chat_id):
    res = supabase.table("messages") \
        .select("*") \
        .eq("chat_id", chat_id) \
        .order("created_at") \
        .execute()

    return res.data


# =========================================================
# PDF STORAGE
# =========================================================

def store_pdf(file_name, file_size, device_id):
    pdf_id = str(uuid.uuid4())

    supabase.table("pdf_metadata").insert({
        "pdf_id": pdf_id,
        "filename": file_name,   # 👈 FIXED HERE
        "file_size": file_size,
        "device_id": device_id
    }).execute()

    return pdf_id


def store_chunks(pdf_id, chunks, embeddings):
    data = []

    for i, (chunk, emb) in enumerate(zip(chunks, embeddings)):
        data.append({
            "id": str(uuid.uuid4()),
            "pdf_id": pdf_id,
            "chunk_index": i,
            "chunk_text": chunk,
            "embedding": emb
        })

    supabase.table("pdf_chunks").insert(data).execute()


# =========================================================
# OPTIONAL (VERY USEFUL)
# =========================================================

def get_chat(chat_id):
    res = supabase.table("chats") \
        .select("*") \
        .eq("chat_id", chat_id) \
        .single() \
        .execute()

    return res.data