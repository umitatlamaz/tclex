import re
from pathlib import Path


TIMESTAMP_PATTERN = (
    r"\d{2}:\d{2}:\d{2},\d{3}"
    r"\s*-->\s*"
    r"\d{2}:\d{2}:\d{2},\d{3}"
)


def remove_timestamps(lines):
    return [
        line
        for line in lines
        if not re.match(TIMESTAMP_PATTERN, line.strip())
    ]


def remove_annotations(lines):
    cleaned_lines = []

    for line in lines:
        line = re.sub(r"\(.*?\)|\[.*?\]", "", line).strip()

        if line:
            cleaned_lines.append(line)

    return cleaned_lines


def merge_dialogue_lines(lines):
    merged_lines = []
    buffer = ""

    for line in lines:
        line = line.strip()

        if line.isdigit():
            if buffer:
                merged_lines.append(buffer.strip())
                buffer = ""
            continue

        if line.startswith("-"):
            if buffer:
                merged_lines.append(buffer.strip())

            buffer = line.lstrip("-").strip()
            continue

        if buffer:
            buffer += " " + line.lstrip(".").strip()
        else:
            buffer = line.lstrip(".").strip()

    if buffer:
        merged_lines.append(buffer.strip())

    return merged_lines


def normalize_ellipses(lines):
    normalized_lines = []

    for line in lines:
        line = line.replace("...", " ")
        line = re.sub(r"\s+", " ", line).strip()

        if line:
            normalized_lines.append(line)

    return normalized_lines


def remove_subtitle_metadata(lines):
    metadata_patterns = [
        r"erişim:",
        r"betimleme",
        r"trt çocuk",
    ]

    filtered_lines = []

    for line in lines:
        if any(re.search(pattern, line, re.IGNORECASE) for pattern in metadata_patterns):
            continue

        filtered_lines.append(line)

    return filtered_lines


def clean_subtitle_text(text):
    lines = text.splitlines()

    lines = remove_timestamps(lines)
    lines = remove_annotations(lines)
    lines = merge_dialogue_lines(lines)
    lines = normalize_ellipses(lines)
    lines = remove_subtitle_metadata(lines)

    return "\n".join(lines).strip()


def process_folder(input_dir, output_dir):
    input_dir = Path(input_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    for input_file in input_dir.rglob("*.txt"):
        relative_path = input_file.relative_to(input_dir)
        output_file = output_dir / relative_path
        output_file.parent.mkdir(parents=True, exist_ok=True)

        text = input_file.read_text(encoding="utf-8", errors="ignore")
        cleaned_text = clean_subtitle_text(text)

        output_file.write_text(cleaned_text, encoding="utf-8")

        print(f"Processed: {input_file} -> {output_file}")


if __name__ == "__main__":
    input_folder = input("Input folder: ").strip()
    output_folder = input("Output folder: ").strip()

    process_folder(input_folder, output_folder)

    print("Subtitle cleaning completed.")