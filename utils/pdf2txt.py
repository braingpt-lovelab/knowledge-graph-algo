import os
from pathlib import Path
import PyPDF2
import re

def extract_text_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ''
        for page in reader.pages:
            text += page.extract_text() + '\n'
    return text

def clean_text(text):
    # Remove multiple consecutive newlines
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    # Remove page numbers (assuming they are standalone numbers)
    text = re.sub(r'^\s*\d+\s*$', '', text, flags=re.MULTILINE)
    
    # Try to identify potential headers (all caps lines)
    lines = text.split('\n')
    cleaned_lines = []
    for line in lines:
        if line.isupper() and len(line.split()) > 1:
            cleaned_lines.append(f"\n# {line}\n")
        else:
            cleaned_lines.append(line)
    
    return '\n'.join(cleaned_lines)

def main():
    pdf_dir = Path('data/pdf_articles')
    txt_dir = Path('data/txt_articles')
    txt_dir.mkdir(exist_ok=True)

    for pdf_file in pdf_dir.glob('*.pdf'):
        text = extract_text_from_pdf(pdf_file)
        cleaned_text = clean_text(text)
        
        txt_file = txt_dir / f"{pdf_file.stem}.txt"
        with open(txt_file, 'w', encoding='utf-8') as f:
            f.write(cleaned_text)
        
        print(f"Processed {pdf_file.name} -> {txt_file.name}")

if __name__ == "__main__":
    main()