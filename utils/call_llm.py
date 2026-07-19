import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
model = os.getenv("MODEL")
api_key = os.getenv("GROQ_API_KEY")

client = Groq(api_key=api_key)


def call_llm(prompt: str) -> str:
    response = client.chat.completions.create(
        model = model,
        messages = [{"role" : "user", "content": prompt}],
        temperature = 0.7,
        max_completion_tokens=2048,
        top_p=1,
        stream=True,
        stop=None
    )
    full_text = ""

    for chunk in response:
        content = chunk.choices[0].delta.content
        if content:
            full_text += content
        
    return full_text
    