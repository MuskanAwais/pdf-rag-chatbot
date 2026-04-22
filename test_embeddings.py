from core.pdf_loader import extract_text_from_pdf
from core.chunker import chunk_text
from core.embeddings import embed_chunks

def test_embeddings():
    file_path = "sample.pdf"

    pages = extract_text_from_pdf(file_path)
    chunks = chunk_text(pages)

    print("\n🧠 Generating embeddings (this may take time)...\n")

    embedded = embed_chunks(chunks[:2])  # only test 2 chunks

    print("\n✅ EMBEDDING TEST RESULT\n")

    for i, c in enumerate(embedded):
        print(f"CHUNK {i}")
        print("Vector length:", len(c["embedding"]))
        print("First 5 values:", c["embedding"][:5])
        print("-" * 50)


if __name__ == "__main__":
    test_embeddings()