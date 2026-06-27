import csv
import pdfplumber
from pathlib import Path

def read_file(file_path : str | Path) -> str | list[dict]:
    try:
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"File Not Found: ${file_path}")
        
        suffix = file_path.suffix.lower()

        if suffix in (".txt", ".md"):
            return file_path.read_text(encoding="utf-8")
        
        if suffix == ".csv":
            with file_path.open(encoding = "utf-8", newline="") as f:
                reader = csv.DictReader(f)
                return list(reader)
            
        if suffix == ".pdf":
            pages: list[str] = []
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    text = page.extract_text() or ""
                    pages.append(text)
            return "\n\n".join(pages)
        
        raise ValueError(f"File extension could not be loaded '{suffix}'. Use .txt, .md, .csv or .pdf")
    
    except FileNotFoundError:
        print(f"Could not find file: {file_path}")
    
   