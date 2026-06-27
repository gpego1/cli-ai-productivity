import os
from dotenv import load_dotenv
from openai import OpenAI
from utils.file_reader import read_file, call_llm

def summarize(file_path: str) -> None:
    try:
        content = read_file(file_path)
        prompt = f""" 
        Summarize the following extracted document (TXT, MD, PDF, or CSV) into clear, concise bullet points. Ignore formatting artifacts, duplicate headers/footers, and extraction errors. Preserve only the most important facts, key concepts, numbers, dates, names, and technical terms. Remove redundancy, do not infer missing information, and group related points under headings if multiple topics exist.

            Output format:

            Summary
            Main Points
            ...
            ...
            Additional Details (if needed)
            ...

            Document:
            {content}
         """
        return call_llm(prompt)

    except FileNotFoundError as e:
        print(f"Error: {e}")
    except ValueError as e:
        print(f"Error: {e}")