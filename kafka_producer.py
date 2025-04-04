from ultralytics import YOLO
import cv2
from kafka import KafkaProducer
import base64
import time
from dotenv import load_dotenv
import os

load_dotenv()

aws_public_ipv4 = os.getenv("AWS_EC2_IPV4")
producer = KafkaProducer(bootstrap_servers=f'{aws_public_ipv4}:9092')

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Encode Frame as JPEG and Convert to Base64
    _, buffer = cv2.imencode('.jpg', frame)
    encoded_frame = base64.b64encode(buffer).decode('utf-8')

    encoded_frame += "=" * ((4 - len(encoded_frame) % 4) % 4)

    # Send to Kafka
    producer.send('drowsinesstopic', value=encoded_frame.encode('utf-8'))
    print("Sent frame to Kafka")

    time.sleep(1)  # Adjust frame rate

cap.release()
producer.close()