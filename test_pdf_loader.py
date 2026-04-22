from core.pdf_loader import extract_text_from_pdf

def test_pdf():
    file_path = "sample.pdf"  # put any PDF in root folder

    pages = extract_text_from_pdf(file_path)

    print("\n📄 PDF LOADED SUCCESSFULLY\n")

    for p in pages[:2]:  # show first 2 pages only
        print(f"PAGE {p['page']}")
        print(p['text'][:300])
        print("-" * 50)


if __name__ == "__main__":
    test_pdf()