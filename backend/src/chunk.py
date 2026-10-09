from pathlib import Path
import json

from extract import extract_pdf


DATA_DIR = Path("data/raw")
OUTPUT_DIR = Path("data/processed")


def chunk_text(text, chunk_size=800, overlap=150):
    """
    Split text into overlapping chunks.

    chunk_size: Maximum number of characters per chunk.
    overlap: Number of characters shared between chunks.
    """

    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")

    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap must be between 0 and chunk_size")

    chunks = []

    start = 0

    while start < len(text):

        end = min(start + chunk_size, len(text))

        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end == len(text):
            break

        start = end - overlap

    return chunks


def process_documents():

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    all_chunks = []

    for pdf_file in DATA_DIR.glob("*.pdf"):

        print(f"Processing: {pdf_file.name}")

        pages = extract_pdf(pdf_file)

        for page in pages:

            text_chunks = chunk_text(page["text"])

            for index, chunk in enumerate(text_chunks):

                all_chunks.append({
                    "id": f"{pdf_file.stem}_p{page['page']}_c{index}",
                    "source": pdf_file.name,
                    "page": page["page"],
                    "text": chunk
                })

    output_file = OUTPUT_DIR / "chunks.json"

    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(
            all_chunks,
            file,
            indent=4,
            ensure_ascii=False
        )

    print(f"\nTotal chunks created: {len(all_chunks)}")
    print(f"Saved to: {output_file}")


if __name__ == "__main__":
    process_documents()