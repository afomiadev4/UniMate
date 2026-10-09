import pymupdf
from pathlib import Path

DATA_DIR = Path("data/raw")


def extract_pdf(pdf_path):
    document = pymupdf.open(pdf_path)

    extracted_pages = []

    for page_number, page in enumerate(document, start=1):

        text = page.get_text("text")

        if text.strip():
            extracted_pages.append({
                "page": page_number,
                "text": text
            })

    document.close()

    return extracted_pages


if __name__ == "__main__":

    pdf_files = list(DATA_DIR.glob("*.pdf"))

    if not pdf_files:
        print("No PDF documents found in data/raw/")
    else:
        for pdf_file in pdf_files:

            print(f"\nProcessing: {pdf_file.name}")

            pages = extract_pdf(pdf_file)

            print(f"Extracted {len(pages)} pages")

            if pages:
                print("\nSample extracted text:")
                print(pages[0]["text"][:1000])