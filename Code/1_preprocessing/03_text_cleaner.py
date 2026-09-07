import re
from pathlib import Path


def remove_metadata_lines(text):
    lines = text.splitlines()
    cleaned_lines = []

    for line in lines:
        line = line.strip()

        if not line:
            continue

        if re.fullmatch(r"\d+", line):
            continue

        if re.fullmatch(r"\d+\.", line):
            continue

        if re.fullmatch(r"\d{2}/\d{2}/\d{4}", line):
            continue

        if re.fullmatch(r"[%/.\-]+", line):
            continue

        if line.lower() == "tarih":
            continue

        cleaned_lines.append(line)

    return "\n".join(cleaned_lines)


def remove_non_linguistic_symbols(text):
    text = re.sub(r"[▶<>•●○■□◆◇►›∆]", "", text)
    text = re.sub(r"([.,!?;:])\1{2,}", r"\1", text)
    return text


def remove_visual_references(text):
    text = re.sub(
        r"\(?\s*\b(?:Şekil|Resim|Görsel)\b\s+\d+(?:\.\d+)?\s*-\s*",
        "",
        text,
        flags=re.IGNORECASE,
    )
    return text


def fix_hyphenated_line_breaks(text):
    return re.sub(r"-\n", "", text)


def normalize_whitespace(text):
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n\s*\n+", "\n", text)
    return text.strip()


def clean_text(text):
    text = remove_metadata_lines(text)
    text = remove_visual_references(text)
    text = remove_non_linguistic_symbols(text)
    text = fix_hyphenated_line_breaks(text)
    text = normalize_whitespace(text)
    return text


def process_folder(input_dir, output_dir):
    input_dir = Path(input_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    for input_file in input_dir.rglob("*.txt"):
        relative_path = input_file.relative_to(input_dir)
        output_file = output_dir / relative_path
        output_file.parent.mkdir(parents=True, exist_ok=True)

        text = input_file.read_text(encoding="utf-8")
        cleaned_text = clean_text(text)
        output_file.write_text(cleaned_text, encoding="utf-8")

        print(f"Processed: {input_file} -> {output_file}")


if __name__ == "__main__":
    input_folder = input("Input folder: ").strip()
    output_folder = input("Output folder: ").strip()

    process_folder(input_folder, output_folder)
    print("Text cleaning completed.")