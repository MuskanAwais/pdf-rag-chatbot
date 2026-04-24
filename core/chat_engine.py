from services.mistral_service import client
from core.vector_search import search_similar_chunks
from core.supabase_client import supabase


# -------------------------
# CHAT HISTORY
# -------------------------
def get_chat_history(chat_id, device_id, limit=10):

    response = supabase.table("conversations") \
        .select("*") \
        .eq("chat_id", chat_id) \
        .eq("device_id", device_id) \
        .order("created_at", desc=True) \
        .limit(limit) \
        .execute()

    return response.data[::-1] if response.data else []


# -------------------------
# PROMPT BUILDER
# -------------------------
def build_prompt(context_chunks, chat_history, user_question):

    context_text = "\n\n".join(
        [f"- {c.get('chunk_text', '')}" for c in context_chunks]
    ) if context_chunks else "NO RELEVANT CONTEXT FOUND"

    history_text = "\n".join(
        [f"{m['role']}: {m['message']}" for m in chat_history]
    ) if chat_history else "No history"

    prompt = f"""
You are a smart AI assistant inside a RAG system.

=================================================
🧠 RULES
=================================================
1. Use document context when relevant.
2. If context is missing or irrelevant → say you don't know from document.
3. Be natural and conversational.
4. If context is not relevant, say: "This information is not in the document"
5. Do NOT guess
6. Do NOT answer general questions
7. If user is emotional → respond kindly and supportive.
8. Never repeat "I can only answer from context".
9. Avoid refusal loops.

=================================================
📚 CONTEXT
=================================================
{context_text}

=================================================
💬 HISTORY
=================================================
{history_text}

=================================================
❓ QUESTION
=================================================
{user_question}

=================================================
🎯 ANSWER:
Provide a clear, human-like response.
"""

    return prompt


# -------------------------
# SAVE MESSAGE
# -------------------------
def save_message(chat_id, pdf_id, device_id, role, message):

    supabase.table("conversations").insert({
        "chat_id": chat_id,
        "pdf_id": pdf_id,
        "device_id": device_id,
        "role": role,
        "message": message
    }).execute()


# -------------------------
# MAIN RAG PIPELINE
# -------------------------
def ask_question(query, pdf_id, device_id, chat_id):

    # ✅ FIX 1: validate early
    if not pdf_id:
        return "⚠️ Please upload a PDF first before asking questions."

    # 1. Retrieve chunks
    chunks = search_similar_chunks(query, pdf_id, device_id)

    # 2. History
    history = get_chat_history(chat_id, device_id)

    # 3. Build prompt
    prompt = build_prompt(chunks, history, query)

    # 4. Mistral call
    response = client.chat.complete(
        model="mistral-small",
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant. Follow instructions carefully."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    answer = response.choices[0].message.content

    # 5. Save chat
    save_message(chat_id, pdf_id, device_id, "user", query)
    save_message(chat_id, pdf_id, device_id, "assistant", answer)

    return answer