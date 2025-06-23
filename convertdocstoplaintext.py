import pdfplumber
import os

pdf_folder = "downloads"
for filename in os.listdir(pdf_folder):
    if filename.lower().endswith(".pdf"):
        pdf_path = os.path.join(pdf_folder, filename)
        print(f"Processing: {pdf_path}")
        try:
            with pdfplumber.open(pdf_path) as pdf:
                text = "\n".join(page.extract_text() or "" for page in pdf.pages)
            txt_path = os.path.join(pdf_folder, filename + ".txt")
            with open(txt_path, "w") as f:
                f.write(text)
            print(f"Saved text to {txt_path}")
        except Exception as e:
            print(f"Failed to process {pdf_path}: {e}")