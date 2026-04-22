from pypdf import PdfReader

def extract_text_from_pdf(pdf_file):
    """
    Extract text page by page from uploaded PDF
    """

    reader = PdfReader(pdf_file)
    pages_text = []

    for i, page in enumerate(reader.pages):
        text = page.extract_text()

        if text:
            pages_text.append({
                "page": i + 1,
                "text": text.strip()
            })

    return pages_text