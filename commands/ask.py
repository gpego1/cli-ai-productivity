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

def ask(file_path: str, ask: str) -> str:
    content = read_file(file_path)
    prompt = f"""
        You will receive text extracted from a document 
        (TXT, MD, PDF, or CSV).
        Analyze the document and answer the user's 
        question using only the information contained in 
        the provided text. Ignore formatting artifacts or
        extraction errors, and provide the most accurate, 
        clear, and concise response possible.
        If the answer cannot be found in the document,
        clearly state that the information 
        is not available.

        Text from document: {content}
        ASK: {ask}
     """
    return call_llm(prompt)
    
