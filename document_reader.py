import io
import os
from pathlib import Path


def _pdf_text(data: bytes) -> str:
    import fitz
    doc = fitz.open(stream=data, filetype="pdf")
    return "\n\n".join(page.get_text("text") for page in doc).strip()


def _ocr_image(image):
    import pytesseract

    command = os.getenv("TESSERACT_CMD", "").strip()
    if not command:
        default_path = Path(r"C:\Program Files\Tesseract-OCR\tesseract.exe")
        if default_path.exists():
            command = str(default_path)
    if command:
        pytesseract.pytesseract.tesseract_cmd = command

    lang = os.getenv("TESSERACT_LANG", "kan+eng")
    try:
        available = pytesseract.get_languages(config="")
        missing = [item for item in lang.split("+") if item not in available]
        if missing:
            raise RuntimeError(
                f"Missing Tesseract languages: {missing}. Available languages: {available}"
            )
        return pytesseract.image_to_string(image, lang=lang).strip()
    except Exception as exc:
        raise RuntimeError(f"OCR failed: {type(exc).__name__}: {exc}") from exc


def extract_text(filename: str, data: bytes) -> str:
    ext = Path(filename).suffix.lower()
    try:
        if ext == ".pdf":
            text = _pdf_text(data)
            if len(text.strip()) >= 20:
                return text

            import fitz
            from PIL import Image
            doc = fitz.open(stream=data, filetype="pdf")
            pages = []
            for page in doc:
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
                image = Image.open(io.BytesIO(pix.tobytes("png")))
                pages.append(_ocr_image(image))
            return "\n\n".join(pages).strip()

        from PIL import Image
        image = Image.open(io.BytesIO(data))
        image.load()
        return _ocr_image(image)
    except Exception as exc:
        raise RuntimeError(
            f"Could not process {filename}: {type(exc).__name__}: {exc}"
        ) from exc
