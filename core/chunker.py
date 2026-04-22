def chunk_text(pages, chunk_size=500, overlap=50):
    """
    Convert extracted pages into overlapping chunks
    pages = [{page, text}]
    """

    chunks = []
    current_chunk = ""
    chunk_index = 0

    for page in pages:
        words = page["text"].split()

        for word in words:
            current_chunk += word + " "

            # when chunk reaches size
            if len(current_chunk.split()) >= chunk_size:
                
                chunks.append({
                    "chunk_index": chunk_index,
                    "text": current_chunk.strip(),
                    "page": page["page"]
                })

                chunk_index += 1

                # overlap logic (keep last words)
                overlap_words = current_chunk.split()[-overlap:]
                current_chunk = " ".join(overlap_words) + " "

    # last chunk
    if current_chunk.strip():
        chunks.append({
            "chunk_index": chunk_index,
            "text": current_chunk.strip(),
            "page": pages[-1]["page"]
        })

    return chunks