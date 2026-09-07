from pathlib import Path
import tempfile

import fitz
from docx import Document
from PIL import Image
import pytesseract


def extract_txt(file_path):
    return file_path.read_text(encoding="utf-8", errors="ignore")


def extract_srt(file_path):
    return file_path.read_text(encoding="utf-8", errors="ignore")


def extract_docx(file_path):
    document = Document(file_path)
    paragraphs = [p.text.strip() for p in document.paragraphs if p.text.strip()]
    return "\n".join(paragraphs)


def extract_pdf_text(file_path):
    text_parts = []

    with fitz.open(file_path) as pdf:
        for page in pdf:
            text = page.get_text().strip()

            if text:
                text_parts.append(text)

    return "\n".join(text_parts)


def extract_pdf_with_ocr(file_path):
    text_parts = []

    with fitz.open(file_path) as pdf:
        for page in pdf:
            pix = page.get_pixmap(dpi=300)

            with tempfile.NamedTemporaryFile(suffix=".png", delete=True) as temp_image:
                pix.save(temp_image.name)

                image = Image.open(temp_image.name)
                text = pytesseract.image_to_string(image, lang="tur+eng")

                if text.strip():
                    text_parts.append(text.strip())

    return "\n".join(text_parts)


def extract_file(file_path, use_ocr=False):
    suffix = file_path.suffix.lower()

    if suffix == ".txt":
        return extract_txt(file_path)

    if suffix == ".srt":
        return extract_srt(file_path)

    if suffix == ".docx":
        return extract_docx(file_path)

    if suffix == ".pdf":
        text = extract_pdf_text(file_path)

        if text.strip():
            return text

        if use_ocr:
            return extract_pdf_with_ocr(file_path)

        return ""

    return ""


def convert_to_txt(input_dir, output_dir, use_ocr=False):
    input_dir = Path(input_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    supported_extensions = {".txt", ".srt", ".docx", ".pdf"}

    for input_file in input_dir.rglob("*"):
        if input_file.suffix.lower() not in supported_extensions:
            continue

        relative_path = input_file.relative_to(input_dir)
        output_file = output_dir / relative_path.with_suffix(".txt")
        output_file.parent.mkdir(parents=True, exist_ok=True)

        text = extract_file(input_file, use_ocr=use_ocr)

        if text.strip():
            output_file.write_text(text, encoding="utf-8")
            print(f"Converted: {input_file} -> {output_file}")
        else:
            print(f"No text extracted: {input_file}")


if __name__ == "__main__":
    input_folder = input("Input folder: ").strip()
    output_folder = input("Output folder: ").strip()
    ocr_choice = input("Use OCR for image-based PDFs? y/n: ").strip().lower()

    use_ocr = ocr_choice == "y"

    convert_to_txt(
        input_folder,
        output_folder,
        use_ocr=use_ocr,
    )

    print("File conversion completed.")