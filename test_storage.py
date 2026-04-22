import os
from core.pdf_loader import extract_text_from_pdf
from core.chunker import chunk_text
from core.embeddings import embed_chunks
from core.storage import store_pdf_metadata, store_chunks


def test_storage():
    file_path = "sample.pdf"

    print("\n📄 Loading PDF...")
    pages = extract_text_from_pdf(file_path)

    print("✂️ Chunking...")
    chunks = chunk_text(pages)

    print("🧠 Embedding (testing 2 chunks)...")
    embedded_chunks = embed_chunks(chunks[:2])  # limit for testing

    print("💾 Storing in Supabase...")

    device_id = "test_device_123"

    pdf_id = store_pdf_metadata(
        filename=os.path.basename(file_path),
        file_size=os.path.getsize(file_path),
        page_count=len(pages),
        device_id=device_id
    )

    store_chunks(embedded_chunks, pdf_id, device_id)

    print("\n✅ STORAGE SUCCESS")
    print("PDF ID:", pdf_id)


if __name__ == "__main__":
    test_storage()