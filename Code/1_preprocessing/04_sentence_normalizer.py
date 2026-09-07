import re
from pathlib import Path


ABBREVIATIONS = {
    "vb", "vs", "örn", "bkz", "dr", "prof", "doç", "yrd", "hz",
    "yy", "md", "no", "sn", "s", "sf"
}


def is_abbreviation(word):
    word = word.strip().lower().rstrip(".")
    return word in ABBREVIATIONS


def merge_lowercase_lines(text):
    lines = text.splitlines()
    merged_lines = []

    for line in lines:
        stripped = line.strip()

        if not stripped:
            continue

        if merged_lines and stripped[0].islower():
            merged_lines[-1] = merged_lines[-1].rstrip() + " " + stripped
        else:
            merged_lines.append(stripped)

    return "\n".join(merged_lines)


def merge_special_start_lines(text):
    special_starts = ('"', "”", "’", "'", ",", ":", ";", ")", "...", "–")
    lines = text.splitlines()
    merged_lines = []

    for line in lines:
        stripped = line.strip()

        if merged_lines and stripped.startswith(special_starts):
            merged_lines[-1] = merged_lines[-1].rstrip() + " " + stripped
        else:
            merged_lines.append(stripped)

    return "\n".join(merged_lines)


def split_sentences(text):
    sentences = []

    for line in text.splitlines():
        words = line.split()
        current_sentence = []

        for i, word in enumerate(words):
            current_sentence.append(word)

            if word.endswith((".", "?", "!")):
                if is_abbreviation(word):
                    continue

                if re.search(r"\d+\.$", word):
                    continue

                sentences.append(" ".join(current_sentence).strip())
                current_sentence = []

        if current_sentence:
            sentences.append(" ".join(current_sentence).strip())

    return "\n".join(sentences)


def normalize_sentence_initials(text):
    lines = []

    for line in text.splitlines():
        line = line.strip()

        if not line:
            continue

        if re.match(r"^[a-f][.)]\s", line, flags=re.IGNORECASE):
            lines.append(line)
            continue

        line = line[0].upper() + line[1:] if line else line
        lines.append(line)

    return "\n".join(lines)


def normalize_sentences(text):
    text = merge_lowercase_lines(text)
    text = merge_special_start_lines(text)
    text = split_sentences(text)
    text = normalize_sentence_initials(text)
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
        normalized_text = normalize_sentences(text)
        output_file.write_text(normalized_text, encoding="utf-8")

        print(f"Processed: {input_file} -> {output_file}")


if __name__ == "__main__":
    input_folder = input("Input folder: ").strip()
    output_folder = input("Output folder: ").strip()

    process_folder(input_folder, output_folder)
    print("Sentence normalization completed.")