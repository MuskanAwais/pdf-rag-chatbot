from core.vector_search import search_similar_chunks

def test_search():
    query = "what is this document about?"

    pdf_id = "e6cb5c39-7f94-4d28-a32d-4137b71baeaf"   # replace from Step 6 output
    device_id = "test_device_123"

    results = search_similar_chunks(query, pdf_id, device_id)

    print("\n🔍 SEARCH RESULTS\n")

    for i, r in enumerate(results):
        print(f"RESULT {i+1}")
        print("Similarity:", r["similarity"])
        print("Text:", r["chunk_text"][:200])
        print("-" * 50)


if __name__ == "__main__":
    test_search()