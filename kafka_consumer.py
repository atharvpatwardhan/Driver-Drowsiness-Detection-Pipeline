from kafka import KafkaConsumer
import cv2
import base64
import numpy as np


consumer = KafkaConsumer('drowsinesstopic', bootstrap_servers='54.146.153.16:9092', auto_offset_reset='earliest')

for message in consumer:
    try:
        # Decode Base64 Frame (Handle Padding)
        frame_data = message.value.decode('utf-8')
        frame_data += "=" * ((4 - len(frame_data) % 4) % 4)  # Fix padding

        decoded_frame = base64.b64decode(frame_data)
        np_arr = np.frombuffer(decoded_frame, np.uint8)
        frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        # Display Frame
        cv2.imshow('Kafka Stream', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    except Exception as e:
        print(f"Error decoding frame: {e}")

cv2.destroyAllWindows()
