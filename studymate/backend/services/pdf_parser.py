import fitz  # PyMuPDF
import io


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """
    Extract clean text from a PDF file given as bytes.
    Handles multi-column layouts and removes excessive whitespace.
    """
    try:
        doc = fitz.open(stream=io.BytesIO(file_bytes), filetype="pdf")
        full_text = []

        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text("text")

            # Clean up the text
            lines = text.split("\n")
            cleaned_lines = []
            for line in lines:
                line = line.strip()
                # Skip very short lines (likely headers/footers/page numbers)
                if len(line) > 2:
                    cleaned_lines.append(line)

            if cleaned_lines:
                full_text.append(f"\n--- Page {page_num + 1} ---\n")
                full_text.append("\n".join(cleaned_lines))

        doc.close()
        result = "\n".join(full_text)

        # Remove excessive blank lines
        import re
        result = re.sub(r'\n{3,}', '\n\n', result)

        return result.strip()

    except Exception as e:
        print(f"PDF extraction error: {e}")
        return ""


def get_text_preview(text: str, max_chars: int = 500) -> str:
    """Return a short preview of extracted text."""
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "..."
