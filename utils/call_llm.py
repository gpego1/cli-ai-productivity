import os
from dotenv import load_dotenv
from openai import OpenAI

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