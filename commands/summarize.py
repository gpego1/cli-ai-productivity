import os
from dotenv import load_dotenv
from openai import OpenAI
from utils.file_reader import read_file

load_dotenv()
model = os.getenv("MODEL")
api_key = os.getenv("OPENAI_API_KEY")
base_url = os.getenv("BASE_URL")

client = OpenAI(
    base_url = base_url, 
    api_key = api_key
)

def call_llm(prompt: str) -> str:
    response = client.chat.completions.create(
        model = model,
        messages = [{"role" : "user", "content": prompt}],
        temperature = 0.7
    )
    return response.choices[0].message.content

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