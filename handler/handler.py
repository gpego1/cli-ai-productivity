import json 
import os
import base64
import binascii
import boto3
import magic
import uuid
from commands import summarize, ask, report

s3 = boto3.client("s3")
UPLOAD_BUCKET = os.getenv("UPLOAD_BUCKET")
RESULTS_BUCKET = os.getenv("RESULTS_BUCKET")

MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024

def _response(status_code, body_dict):
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body_dict)
    }

def upload_file_to_s3(file_base64: str, file_name: str):
    try:
        file_bytes = base64.b64decode(file_base64, validate=True)
    except (binascii.Error, ValueError):
        raise ValueError("Invalid Base64 content")

    if len(file_bytes) > MAX_FILE_SIZE_BYTES:
        raise ValueError("File is bigger than the allowed size.")

    key = f"{uuid.uuid4()}_{file_name}"
    tmp_path = f"/tmp/{key}"

    with open(tmp_path, "wb") as f:
        f.write(file_bytes)

    try:
        content_type = magic.from_file(tmp_path, mime=True)

        s3.put_object(
            Bucket=UPLOAD_BUCKET,
            Key=key,
            Body=file_bytes,
            ContentType=content_type
        )
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

    return key

def lambda_handler(event, context):
    try:
        path = event.get("rawPath", "")
        body = json.loads(event.get("body") or "{}")

        if path == "/upload":
            file_base64 = body.get("file_base64")
            file_name = body.get("file_name")

            if not file_base64 or not file_name:
                return _response(400, {"error":"No file on the request Body"})
        
            try:
                file_key = upload_file_to_s3(file_base64, file_name)
                return _response(201, {"file_key":file_key})
            
            except ValueError as e:
                return _response(404, {"error": str(e)})

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