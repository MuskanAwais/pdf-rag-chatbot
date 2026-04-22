from core.supabase_client import supabase
from core.embeddings import get_embeddings_batch


def search_similar_chunks(query, pdf_id, device_id, top_k=5):

    # embed query
    query_embedding = get_embeddings_batch([query])[0]

    response = supabase.rpc(
        "match_chunks",
        {
            "query_embedding": query_embedding,
            "match_count": top_k,
            "p_pdf_id": pdf_id,
            "p_device_id": device_id
        }
    ).execute()

    return response.data