import json 
import os
import boto3
from commands import summarize, ask, report

s3 = boto3.client("s3")
UPLOAD_BUCKET = os.getenv("UPLOAD_BUCKET")
RESULTS_BUCKET = os.getenv("RESULTS_BUCKET")

def _response(status_code, body_dict):
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body_dict)
    }

def lambda_handler(event, context):
    try:
        path = event.get("rawPath", "")
        body = json.loads(event.get("body") or "{}")

        file_key = body.get("file_key")

        if not file_key:
            return _response(404, {"error":"File path is required"})
        
        local_path = f"/tmp/{file_key.split("/")[-1]}"
        s3.download_file(UPLOAD_BUCKET, file_key, local_path)
        
        if path == "/summarize":
            result = summarize.run(local_path)

        elif path == "/ask":
            question = body.get("question")
            if not question:
                return _response(400, {"error": "question is required"})
            result = ask.run(local_path, question)

        elif path == "/report":
            result = report.run(local_path)
        
        else:
            return _response(404, {"error": "no route found"})
        
        result_key = f"results/{file_key.split(".")[0]}.txt"
        s3.put_object(Bucket=RESULTS_BUCKET, Key=result_key, Body=result)

        return _response(200, {"result": result, "result_key": result_key})
    
    except FileNotFoundError:
        return _response(404, {"error": "The specified file was not found"})
    except Exception as e:
        print(f"Error: {e}")
        return _response(500, {"error": "Internal server error"})