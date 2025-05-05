# 🚗 Driver Drowsiness Detection System with Automated Retraining

A real-time, cloud-integrated driver drowsiness detection system that uses deep learning, big data pipelines, and feedback-driven retraining to minimize false alerts and maximize reliability.

---

## 📌 Overview

This project detects driver drowsiness in real-time using computer vision and fine-tuned YOLOv8. It integrates an end-to-end feedback loop using Kafka, Spark, AWS, and Airflow to support automated retraining on misclassified data. Metrics and model performance are tracked using MLflow.

---

## 🔧 Technologies Used

| Layer                     | Tech Stack                                           |
| ------------------------- | ---------------------------------------------------- |
| **Model Inference**       | YOLOv8, OpenCV, PyTorch                              |
| **Streaming**             | Apache Kafka, Spark Streaming                        |
| **Data Storage**          | AWS S3                                               |
| **Feedback Collection**   | AWS Lambda, FastAPI (or Flask), WhatsApp (CallMeBot) |
| **Retraining**            | Apache Airflow, MLflow                               |
| **Deployment (Optional)** | Docker, EC2, Lambda                                  |

---

## ⚙️ Architecture

```text
Cameras → Kafka (Raw Frames) → Spark Streaming (YOLOv8 Inference) → Kafka (Drowsiness Alerts) → WhatsApp
                                           ↓
                            AWS S3 (Frame Storage + Metadata)
                                           ↓
                             FastAPI / Lambda (False Positive Reporting)
                                           ↓
              Airflow DAG → Fetch + Label False Positives → Retrain Model → MLflow → Upload to S3

```

## 🚀 Getting Started Locally

---

### 📦 1. Clone the Repository

```bash
git clone https://github.com/yourusername/driver-drowsiness-detection.git
cd driver-drowsiness-detection
```

### 📂 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### ⚙️ 3. Configure Environment Variables

```bash
CALLMEBOT_API_KEY=your_callmebot_api_key
ALERT_PHONE_NUMBER=+1xxxxxxxxxx
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
```

### 🔄 4. Set Up Kafka & Zookeeper

```bash
# Start Zookeeper
bin/zookeeper-server-start.sh config/zookeeper.properties

# Start Kafka Broker
bin/kafka-server-start.sh config/server.properties

# Create Topic
bin/kafka-topics.sh --create --topic drowsinesstopic \
  --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1
```

### 🧪 5. Run the detection pipeline

```bash
# Starts collecting data frames from webcam
python kafka_producer.py

# Displays frames from stream to the user
python kafka_consumer.py

# YoloV8 inferencing and whatsapp alerts
python main.py
```
