**# Text Wrangling and Corpus Preprocessing Pipeline**



A modular Python-based preprocessing pipeline for converting, cleaning, normalizing, and preparing heterogeneous textual resources for corpus-based linguistic analysis.



This pipeline supports `.pdf`, `.docx`, `.txt`, and `.srt` files. It also provides optional OCR support for image-based PDFs.



**## Features**



\- Multi-format document conversion

\- OCR-based text extraction

\- Subtitle preprocessing

\- Structural noise removal

\- Sentence normalization

\- Character normalization

\- Residual noise filtering

\- Batch processing

\- Folder structure preservation

\- UTF-8 compatible output



**## Repository Structure**



```text

project/

│

├── scripts/

│   ├── 01\_extract\_to\_txt.py

│   ├── 02\_subtitle\_cleaner.py

│   ├── 03\_text\_cleaner.py

│   ├── 04\_sentence\_normalizer.py

│   ├── 05\_character\_normalizer.py

│   └── 06\_final\_check.py

│

├── data/

│   ├── raw/

│   ├── extracted/

│   ├── cleaned/

│   └── final/

│

├── requirements.txt

└── README.md



**Install dependencies:**



pip install -r requirements.txt



**Requirements**



pymupdf

python-docx

pillow

pytesseract

Tesseract OCR





**OCR functionality requires Tesseract OCR to be installed separately.**



For Windows users, if Tesseract is not automatically detected, add the following line to 01\_extract\_to\_txt.py after importing pytesseract:



pytesseract.pytesseract.tesseract\_cmd = (

&#x20;   r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"

)





**Pipeline Overview**





**1. File Conversion and OCR**



Script:



01\_extract\_to\_txt.py



Converts heterogeneous document formats into machine-readable plain text.



Supported formats:



.pdf

.docx

.txt

.srt



OCR can optionally be applied to image-based PDFs.



Run:



python scripts/01\_extract\_to\_txt.py



**2. Subtitle Cleaning**



Script:



02\_subtitle\_cleaner.py



Performs subtitle-specific preprocessing:



timestamp removal

subtitle annotation cleaning

dialogue reconstruction

subtitle metadata filtering



Important:



02\_subtitle\_cleaner.py should only be applied to subtitle-derived text files. It should not be used for general document corpora such as books, articles, reports, or educational materials.



Run:



python scripts/02\_subtitle\_cleaner.py



**3. General Text Cleaning**



Script:



03\_text\_cleaner.py



Performs:



metadata removal

OCR artifact cleaning

visual reference removal

whitespace normalization

hyphenated line repair



Run:



python scripts/03\_text\_cleaner.py



**4. Sentence Normalization**



Script:



04\_sentence\_normalizer.py



Performs:



line merging

sentence boundary normalization

abbreviation-aware sentence splitting

capitalization normalization



Run:



python scripts/04\_sentence\_normalizer.py



**5. Character Normalization**



Script:



05\_character\_normalizer.py



Performs:



Unicode normalization

punctuation normalization

OCR symbol filtering

whitespace normalization

Non-linguistic Unicode symbols are removed during character normalization.

Run:



python scripts/05\_character\_normalizer.py



**6. Final Cleaning**



Script:



06\_final\_check.py



Performs:



empty-line removal

punctuation-only line filtering

residual noise cleaning



Run:



python scripts/06\_final\_check.py





**Recommended Processing Order**



**For subtitle-based corpora**

01\_extract\_to\_txt.py

→ 02\_subtitle\_cleaner.py

→ 03\_text\_cleaner.py

→ 04\_sentence\_normalizer.py

→ 05\_character\_normalizer.py

→ 06\_final\_check.py



**For general document corpora**

01\_extract\_to\_txt.py

→ 03\_text\_cleaner.py

→ 04\_sentence\_normalizer.py

→ 05\_character\_normalizer.py

→ 06\_final\_check.py

Suggested Folder Workflow



Example:



data/

│

├── raw/

│   ├── books/

│   ├── articles/

│   └── subtitles/

│

├── extracted/

├── cleaned/

└── final/



The scripts preserve the original folder hierarchy while writing processed files into a separate output directory.



Example Usage



For file extraction:



python scripts/01\_extract\_to\_txt.py



When prompted:



Input folder: data/raw

Output folder: data/extracted

Use OCR for image-based PDFs? y/n: y



For general document cleaning:



python scripts/03\_text\_cleaner.py



When prompted:



Input folder: data/extracted

Output folder: data/cleaned

Notes

Raw files are not modified.

Each script writes output to a separate folder.

Subtitle cleaning should be applied only to subtitle-derived .txt files.

OCR quality may vary depending on image quality, page layout, font, and scan resolution.

For Turkish OCR, make sure the Turkish language package is installed for Tesseract.



**Academic Purpose**



**This preprocessing pipeline was designed for:**



corpus linguistics

natural language processing

educational text analysis

OCR-based corpus recovery

linguistic preprocessing research



The pipeline emphasizes:



reproducibility

modular preprocessing

structural normalization

OCR-aware text recovery

character-level consistency

Citation



**If you use this pipeline in academic work, please cite the related study or repository.**



**License**



**MIT License**





