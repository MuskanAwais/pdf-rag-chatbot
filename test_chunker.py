from core.pdf_loader import extract_text_from_pdf
from core.chunker import chunk_text

def test_chunking():
    file_path = "sample.pdf"

    pages = extract_text_from_pdf(file_path)
    chunks = chunk_text(pages)

    print("\n✂️ CHUNKING RESULT\n")
    print(f"Total chunks: {len(chunks)}\n")

    for i, c in enumerate(chunks[:3]):
        print(f"CHUNK {i}")
        print("Page:", c["page"])
        print("Text preview:", c["text"][:300])
        print("-" * 50)


if __name__ == "__main__":
    test_chunking()