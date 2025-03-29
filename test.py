
import cv2
from ultralytics import YOLO



model = YOLO("datasets/runs/detect/train2/weights/best.pt")

cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret,frame = cap.read()

    if not ret:
        break

    results = model(frame, show=True)

    for r in results:
        for box in r.boxes:
            cls = int(box.cls[0])
            conf = float(box.conf[0])
            x1,y1,x2,y2 = map(int,box.xyxy[0])

            label = f"{model.names[cls]} {conf:.2f}"

            color = (0,255,0) if cls == 0 else (255,0,0)

            cv2.rectangle(frame, (x1,y1), (x2,y2), color, 2)
            cv2.putText(frame, label, (x1,y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

            if cls == 1:
                print("Drowsiness detected!")
                cv2.putText(frame, "Drowsiness detected!", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)



    cv2.imshow("Drowsiness Detection", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()