from services.mistral_service import client


def get_embeddings_batch(texts):
    response = client.embeddings.create(
        model="mistral-embed",
        inputs=texts
    )
    return [d.embedding for d in response.data]


def embed_chunks(chunks, batch_size=10):
    embedded_chunks = []

    for i in range(0, len(chunks), batch_size):

        batch = chunks[i:i + batch_size]
        texts = [c["text"] for c in batch]

        try:
            embeddings = get_embeddings_batch(texts)

            for j, chunk in enumerate(batch):
                embedded_chunks.append({
                    **chunk,
                    "embedding": embeddings[j]
                })

        except Exception as e:
            print("Embedding batch failed:", e)

    return embedded_chunks

