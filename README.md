# 🚗 Driver Drowsiness Detection System with Automated Retraining

A real-time, cloud-integrated driver drowsiness detection system that uses deep learning, big data pipelines, and feedback-driven retraining to minimize false alerts and maximize reliability.

---

## 📌 Overview

This project detects driver drowsiness in real-time using computer vision and fine-tuned YOLOv8. It integrates an end-to-end feedback loop using Kafka, Spark, AWS, and Airflow to support automated retraining on misclassified data. Metrics and model performance are tracked using MLflow.

---

## 🔧 Technologies Used

| Layer                  | Tech Stack |
|------------------------|------------|
| **Model Inference**    | YOLOv8, OpenCV, PyTorch |
| **Streaming**          | Apache Kafka, Spark Streaming |
| **Data Storage**       | AWS S3 |
| **Feedback Collection**| AWS Lambda, FastAPI (or Flask), WhatsApp (CallMeBot) |
| **Retraining**         | Apache Airflow, MLflow |
| **Deployment (Optional)** | Docker, EC2, Lambda |

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
