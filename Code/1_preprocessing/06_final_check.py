import re
from pathlib import Path


def remove_empty_lines(text):
    lines = [line.strip() for line in text.splitlines()]
    lines = [line for line in lines if line]
    return "\n".join(lines)


def remove_numeric_or_punctuation_lines(text):
    cleaned_lines = []

    for line in text.splitlines():
        if re.fullmatch(r"[\d\s.,!?;:()\[\]{}<>=/\-\\+*]+", line):
            continue

        cleaned_lines.append(line)

    return "\n".join(cleaned_lines)


def simplify_repeated_characters(text):
    text = re.sub(r"([.,!?;:])\1{2,}", r"\1", text)
    return text


def normalize_final_text(text):
    text = remove_empty_lines(text)
    text = remove_numeric_or_punctuation_lines(text)
    text = simplify_repeated_characters(text)
    text = remove_empty_lines(text)
    return text.strip()


def process_folder(input_dir, output_dir):
    input_dir = Path(input_dir)
    output_dir = Path(output_dir)

    output_dir.mkdir(parents=True, exist_ok=True)

    for input_file in input_dir.rglob("*.txt"):
        relative_path = input_file.relative_to(input_dir)
        output_file = output_dir / relative_path

        output_file.parent.mkdir(parents=True, exist_ok=True)

        text = input_file.read_text(encoding="utf-8")
        cleaned_text = normalize_final_text(text)

        output_file.write_text(cleaned_text, encoding="utf-8")

        print(f"Processed: {input_file} -> {output_file}")


if __name__ == "__main__":
    input_folder = input("Input folder: ").strip()
    output_folder = input("Output folder: ").strip()

    process_folder(input_folder, output_folder)

    print("Final cleaning completed.")