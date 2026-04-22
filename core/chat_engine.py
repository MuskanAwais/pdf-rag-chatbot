from services.mistral_service import client
from core.vector_search import search_similar_chunks
from core.supabase_client import supabase


def get_chat_history(chat_id, device_id, limit=10):
    """
    Fetch last messages for memory
    """

    response = supabase.table("conversations") \
        .select("*") \
        .eq("chat_id", chat_id) \
        .eq("device_id", device_id) \
        .order("created_at", desc=True) \
        .limit(limit) \
        .execute()

    return response.data[::-1]  # reverse to chronological order


def build_prompt(context_chunks, chat_history, user_question):
    """
    Create final prompt for LLM
    """

    context_text = "\n\n".join(
        [f"- {c['chunk_text']}" for c in context_chunks]
    )

    history_text = "\n".join(
        [f"{m['role']}: {m['message']}" for m in chat_history]
    )

    prompt = f"""
You are a helpful AI assistant. Answer ONLY using the provided context.

Context:
{context_text}

Chat History:
{history_text}

User Question:
{user_question}

Answer:
"""

    return prompt


def save_message(chat_id, pdf_id, device_id, role, message):
    """
    Store conversation in Supabase
    """

    supabase.table("conversations").insert({
        "chat_id": chat_id,
        "pdf_id": pdf_id,
        "device_id": device_id,
        "role": role,
        "message": message
    }).execute()


def ask_question(query, pdf_id, device_id, chat_id):
    """
    MAIN RAG PIPELINE
    """

    # 1. Retrieve relevant chunks
    chunks = search_similar_chunks(query, pdf_id, device_id)

    # 2. Get chat history
    history = get_chat_history(chat_id, device_id)

    # 3. Build prompt
    prompt = build_prompt(chunks, history, query)

    # 4. Call Mistral Chat Model
    response = client.chat.complete(
        model="mistral-small",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    answer = response.choices[0].message.content

    # 5. Save conversation
    save_message(chat_id, pdf_id, device_id, "user", query)
    save_message(chat_id, pdf_id, device_id, "assistant", answer)

    return answer