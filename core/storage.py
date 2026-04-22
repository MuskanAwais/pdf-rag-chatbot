import uuid
from core.supabase_client import supabase


def store_pdf_metadata(filename, file_size, page_count, device_id):
    """
    Insert PDF metadata and return pdf_id
    """

    pdf_id = str(uuid.uuid4())

    data = {
        "pdf_id": pdf_id,
        "device_id": device_id,
        "filename": filename,
        "file_size": file_size,
        "page_count": page_count,
        "is_processed": True
    }

    supabase.table("pdf_metadata").insert(data).execute()

    return pdf_id


def store_chunks(chunks, pdf_id, device_id):
    """
    Store chunks with embeddings
    """

    records = []

    for chunk in chunks:
        records.append({
            "pdf_id": pdf_id,
            "device_id": device_id,
            "chunk_text": chunk["text"],
            "embedding": chunk["embedding"],
            "chunk_index": chunk["chunk_index"]
        })

    supabase.table("pdf_chunks").insert(records).execute()