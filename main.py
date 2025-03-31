from pyspark.sql import SparkSession
from pyspark.sql.functions import col
from pyspark.streaming import StreamingContext
from pyspark.sql.types import StringType
from kafka import KafkaProducer
import cv2
import base64
import numpy as np
from ultralytics import YOLO
import boto3
import json
from dotenv import load_dotenv
import os
import requests
from fastapi import FastAPI, Query

load_dotenv()

app = FastAPI()

def send_whatsapp_alert(batch_id: str):
    CALLMEBOT_API_KEY = os.getenv("CALLMEBOT_API_KEY")
    PHONE_NUMBER = os.getenv("ALERT_PHONE_NUMBER")
    REPORT_URL = f"https://qtawzqfhszbr22klbsjmdhvfqa0cnfni.lambda-url.us-east-1.on.aws/report_false_alert?batch_id={batch_id}"
    MESSAGE = f"🚨+Drowsiness+Alert!+ Take a break! \nIf+this+was+a+false alarm,+report+it+here:+ {REPORT_URL}"

    url = f"https://api.callmebot.com/whatsapp.php?phone={PHONE_NUMBER}&text={MESSAGE}&apikey={CALLMEBOT_API_KEY}"
    response = requests.get(url)

    print(f"Message sent! Status: {response.status_code}")


spark = SparkSession.builder \
    .appName("DrowsinessDetection") \
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.2.1") \
    .getOrCreate()


model = YOLO("datasets/runs/detect/train2/weights/best.pt")

producer = KafkaProducer(bootstrap_servers='54.146.161.205:9092', value_serializer=lambda v: json.dumps(v).encode('utf-8'))

s3_client = boto3.client('s3')
S3_BUCKET = "drowsiness-detection-project-bucket"

df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "54.146.161.205:9092") \
    .option("subscribe", "drowsinesstopic") \
    .load()

df = df.selectExpr("CAST(value AS STRING)").withColumnRenamed("value", "frame_data")


@app.get("/report_false_alert")
def report_false_alert(batch_id: str):
    try:
        source_key = f"drowsyframes/{batch_id}.jpg"
        destination_key = f"false_positives/{batch_id}.jpg"

        # Move the falsely classified frame
        copy_source = {"Bucket": S3_BUCKET, "Key": source_key}
        s3_client.copy_object(Bucket=S3_BUCKET, CopySource=copy_source, Key=destination_key)

        # Delete the original from "drowsyframes/"
        s3_client.delete_object(Bucket=S3_BUCKET, Key=source_key)

        return {"message": "False positive reported successfully!"}
    
    except Exception as e:
        return {"error": str(e)}


def process_frame(batch_df, batch_id):
    for row in batch_df.collect():
        try:
            frame_data = row["frame_data"]
            frame_data += "=" * ((4 - len(frame_data) % 4) % 4)  # Fix padding
            decoded_frame = base64.b64decode(frame_data)
            np_arr = np.frombuffer(decoded_frame, np.uint8)
            frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

            # Perform YOLOv8 Inference
            results = model(frame)
            alert = False

            for r in results:
                for box in r.boxes:
                    label = r.names[int(box.cls)]
                    if label in ["drowsy"]:  # Adjust based on dataset labels
                        alert = True
                        send_whatsapp_alert(batch_id)
                        producer.send("drowsiness_alerts", {"alert": "Drowsiness Detected"})
                        file_name = f"drowsyframes/{batch_id}.jpg"
                        s3_client.put_object(Bucket=S3_BUCKET, Key=file_name, Body=buffer.tobytes())


            # Store Frame in S3
            file_name = f"frames/{batch_id}.jpg"
            _, buffer = cv2.imencode('.jpg', frame)
            s3_client.put_object(Bucket=S3_BUCKET, Key=file_name, Body=buffer.tobytes())

        except Exception as e:
            print(f"Error processing frame: {e}")


# Apply Processing
query = df.writeStream \
    .foreachBatch(process_frame) \
    .start()

query.awaitTermination()

