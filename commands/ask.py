from utils.file_reader import read_file
from utils.call_llm import call_llm


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
    
