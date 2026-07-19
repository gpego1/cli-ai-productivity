import json 
from commands import summarize, ask, report

def _response(status_code, body_dict):
    return {
        "status": status_code,
        "headers": {"Content-Type": "appllication/json"},
        "body": json.dumps(body_dict)
    }

def lambda_handler(event, context):
    try:
        path = event.get("path", "")
        body = json.loads(event.get("body") or "{}")

        file_path = body.get("file_path")

        if not file_path:
            return _response(404, {"error":"File path is required"})
        
        if path == "/summarize":
            result = summarize.run(file_path)
        elif path == "/ask":
            question = body.get("question")
            result = ask.run(file_path, question)
        elif path == "/report":
            result = report.run(file_path)
        
        else:
            return _response(404, {"error": "no route found"})
        
        return _response(200, {"result": result})
    
    except FileNotFoundError:
        return _response(404, {"error": "The specified file was not found"})
    except Exception as e:
        print(f"Error: {e}")
        return _response(500, {"error": "Internal server error"})