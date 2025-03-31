from fastapi import FastAPI, Query
import boto3
from mangum import Mangum  # Wraps FastAPI for AWS Lambda
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)  # Ensure INFO logs are captured

app = FastAPI()
lambda_handler = Mangum(app)

S3_BUCKET = "drowsiness-detection-project-bucket"
s3_client = boto3.client('s3')


@app.get("/")
async def root():
    return {"message": "Welcome to the Drowsiness Detection API!"}

@app.get("/report_false_alert/{batch_id}")
async def report_false_alert(batch_id: int):
    logger.info(f"Inside false alert function")
    print("Inside false alert function")


    # Define S3 paths
    source_key = f"drowsyframes/{batch_id}.jpg"
    destination_key = f"false_positives/{batch_id}.jpg"

    # Move the falsely classified frame
    copy_source = {"Bucket": S3_BUCKET, "Key": source_key}
    s3_client.copy_object(Bucket=S3_BUCKET, CopySource=copy_source, Key=destination_key)

    # Delete the original from "drowsyframes/"
    s3_client.delete_object(Bucket=S3_BUCKET, Key=source_key)

    return {"message": "False positive reported successfully!"}

