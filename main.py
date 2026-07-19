import json
from handler.handler import lambda_handler

def test_sumarize():
    event = {
        "path":"/summarize",
        "body": json.dumps({"file_path":"./cv.pdf"})
    }
    response = lambda_handler(event, None)
    print(json.dumps(response, indent=2, ensure_ascii=False))

def test_ask():
    event = {
        "path":"/ask",
        "body": json.dumps({
            "file_path":"./cv.pdf",
            "question": "Whats the main programming language from this CV"
        }),
    }
    response = lambda_handler(event, None)
    print(json.dumps(response, indent=2, ensure_ascii=False))

def test_report():
    event = {
        "path":"/report",
        "body": json.dumps({
            "file_path":"./cronograma.csv"
        }),
    }
    response = lambda_handler(event, None)
    print(json.dumps(response, indent=2, ensure_ascii=False))

    
    
if __name__ == '__main__':
    test_report()
    


