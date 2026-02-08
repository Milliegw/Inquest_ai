import os
import shutil

# Move all .pdf.txt files from the downloads folder to the plain_texts folder
src = "downloads"
dst = "plain_texts"
os.makedirs(dst, exist_ok=True)
for f in os.listdir(src):
    if f.endswith(".pdf.txt"):
        shutil.move(os.path.join(src, f), os.path.join(dst, f))