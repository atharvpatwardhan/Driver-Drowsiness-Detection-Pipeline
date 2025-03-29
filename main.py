from pyspark.sql import SparkSession
from pyspark.sql.functions import col
from pyspark.streaming import StreamingContext
from pyspark.sql.types import StringType
from kafka import KafkaProducer
import torch
import cv2
import base64
import numpy as np
from ultralytics import YOLO
import boto3
import json

spark = SparkSession.builder \
    .appName("DrowsinessDetection") \
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.2.1") \
    .getOrCreate()


model = YOLO("datasets/runs/detect/train2/weights/best.pt")

producer = KafkaProducer(bootstrap_servers='54.146.153.16:9092', value_serializer=lambda v: json.dumps(v).encode('utf-8'))

s3_client = boto3.client('s3')
S3_BUCKET = "drowsiness-detection-project-bucket"

df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "54.146.153.16:9092") \
    .option("subscribe", "drowsinesstopic") \
    .load()

df = df.selectExpr("CAST(value AS STRING)").withColumnRenamed("value", "frame_data")

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




# cap = cv2.VideoCapture(0)

# while cap.isOpened():
#     ret,frame = cap.read()

#     if not ret:
#         break

#     results = model(frame, show=True)

#     for r in results:
#         for box in r.boxes:
#             cls = int(box.cls[0])
#             conf = float(box.conf[0])
#             x1,y1,x2,y2 = map(int,box.xyxy[0])

#             label = f"{model.names[cls]} {conf:.2f}"

#             color = (0,255,0) if cls == 0 else (255,0,0)

#             cv2.rectangle(frame, (x1,y1), (x2,y2), color, 2)
#             cv2.putText(frame, label, (x1,y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

#             if cls == 1:
#                 print("Drowsiness detected!")
#                 cv2.putText(frame, "Drowsiness detected!", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)



#     cv2.imshow("Drowsiness Detection", frame)

#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break

# cap.release()
# cv2.destroyAllWindows()