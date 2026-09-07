import re
from pathlib import Path


ALLOWED_CHARACTERS = (
    r"a-zA-ZçğıöşüÇĞİÖŞÜ0-9"
    r"\s\.,!\?;:'\"()\[\]\-–"
)


def remove_repeated_punctuation(text):
    return re.sub(
        r"([.,!?;:])\1{2,}",
        r"\1",
        text,
    )


def remove_non_linguistic_symbols(text):
    return re.sub(
        rf"[^{ALLOWED_CHARACTERS}]",
        "",
        text,
    )


def normalize_quotes_and_dashes(text):
    replacements = {
        "“": '"',
        "”": '"',
        "‘": "'",
        "’": "'",
        "—": "-",
        "–": "-",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    return text


def normalize_whitespace(text):
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n\s*\n+", "\n", text)
    return text.strip()


def normalize_characters(text):
    text = normalize_quotes_and_dashes(text)
    text = remove_repeated_punctuation(text)
    text = remove_non_linguistic_symbols(text)
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

        normalized_text = normalize_characters(text)

        output_file.write_text(
            normalized_text,
            encoding="utf-8",
        )

        print(f"Processed: {input_file} -> {output_file}")


if __name__ == "__main__":
    input_folder = input("Input folder: ").strip()
    output_folder = input("Output folder: ").strip()

    process_folder(input_folder, output_folder)

    print("Character normalization completed.")