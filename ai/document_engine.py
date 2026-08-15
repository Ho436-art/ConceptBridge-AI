"""
ConceptBridge AI - Document & File Extraction Engine
Handles parsing and extracting contextual text from uploaded PDFs, Images, and Text files.
"""

import io
from typing import Tuple, Optional


def extract_content_from_file(file_name: str, file_bytes: bytes) -> Tuple[bool, str]:
    """
    Extracts text/context from uploaded file bytes.
    Supports PDF, TXT, PY, MD, CSV, and image descriptions.
    
    Returns:
        Tuple[bool, str]: (Success, Extracted text content or error description).
    """
    if not file_bytes:
        return False, "File is empty."

    name_lower = file_name.lower().strip()

    # 1. PDF Documents
    if name_lower.endswith(".pdf"):
        try:
            import pypdf
            reader = pypdf.PdfReader(io.BytesIO(file_bytes))
            extracted_pages = []
            max_pages = min(len(reader.pages), 10)
            for i in range(max_pages):
                text = reader.pages[i].extract_text()
                if text and text.strip():
                    extracted_pages.append(f"--- Page {i+1} ---\n{text.strip()}")
            
            if extracted_pages:
                full_text = "\n\n".join(extracted_pages)
                # Cap at 4000 characters to keep prompt focused
                if len(full_text) > 4000:
                    full_text = full_text[:4000] + "\n...[Content truncated for brevity]..."
                return True, full_text
            else:
                return True, f"[PDF Document '{file_name}': Contains scanned or visual pages without direct text layer. Processed for concept analysis.]"
        except Exception as e:
            return False, f"Could not read PDF '{file_name}': {e}"

    # 2. Text / Code Files
    if name_lower.endswith((".txt", ".py", ".md", ".json", ".csv", ".html", ".js", ".java", ".cpp", ".c", ".sql")):
        try:
            text = file_bytes.decode("utf-8", errors="replace").strip()
            if len(text) > 4000:
                text = text[:4000] + "\n...[Content truncated]..."
            return True, text
        except Exception as e:
            return False, f"Could not decode text file: {e}"

    # 3. Image Files (PNG, JPG, JPEG, WEBP)
    if name_lower.endswith((".png", ".jpg", ".jpeg", ".webp")):
        return True, f"[Attached Image Diagram / Homework Photo: '{file_name}' ({len(file_bytes)//1024} KB)]"

    return True, f"[Attached File: '{file_name}']"
