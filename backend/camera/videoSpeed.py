import sys
sys.path.insert(0, "/usr/lib/python3/dist-packages/") 

import cv2
import csv
import time
import numpy as np
from datetime import datetime
from ultralytics import YOLO

MODEL_PATH = "yolov8n.engine"
VIDEO_PATH = "/home/esls/Dev/uiTest/backend/camera/video1.mp4"
KNOWN_DISTANCE_METERS = 35.0
SPEED_DISPLAY_DURATION = 2.0
ALLOWED_CLASSES = [0, 1, 2, 3, 5, 7]  # person, car, truck, bus, motorcycle, bicycle

ROI_LINE_1 = np.array([[0, 250], [640, 250]], dtype=int)
ROI_LINE_2 = np.array([[0, 300], [640, 300]], dtype=int)
ROI_LINES = [ROI_LINE_1, ROI_LINE_2]

cap = cv2.VideoCapture(VIDEO_PATH)

model = YOLO("yolov8n.engine", task="detect")

now = datetime.now()
csv_file = open("speed_log.csv", mode="w", newline="")
csv_writer = csv.writer(csv_file)
csv_writer.writerow(["timestamp", "track_id", "class", "speed_kmph", "distance_m"])

prev_centers = {}
line1_pass_times = {}
speed_display = {}
id_color_map = {}

# GStreamer UDP 출력
gst_output = (
    "appsrc ! videoconvert ! "
    "x264enc tune=zerolatency bitrate=2000 speed-preset=ultrafast ! "
    "rtph264pay config-interval=1 pt=96 ! "
    "udpsink host=192.168.10.101 port=8554"
)
# GStreamer 스트리밍 파이프라인 (H.264 UDP 전송)
out = cv2.VideoWriter(
    gst_output,
    cv2.CAP_GSTREAMER,
    0,
    30.0,
    (640, 480)
)

def intersects(p1, p2, q1, q2):
    def ccw(a, b, c):
        return (c[1] - a[1]) * (b[0] - a[0]) > (b[1] - a[1]) * (c[0] - a[0])
    return ccw(p1, q1, q2) != ccw(p2, q1, q2) and ccw(p1, p2, q1) != ccw(p1, p2, q2)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.resize(frame, (640, 480))
    results = model.track(frame, persist=True, conf=0.4, iou=0.5, verbose=False)
    boxes = results[0].boxes

    if boxes.id is None:
        out.write(frame)
        continue

    xyxy = boxes.xyxy.cpu().numpy()
    class_ids = boxes.cls.cpu().numpy().astype(int)
    track_ids = boxes.id.cpu().numpy().astype(int)

    for i, cls in enumerate(class_ids):
        if cls not in ALLOWED_CLASSES:
            continue

        box = xyxy[i]
        x1, y1, x2, y2 = map(int, box)
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
        track_id = int(track_ids[i])
        class_name = model.names[int(cls)]

        if track_id not in id_color_map:
            np.random.seed(track_id)
            id_color_map[track_id] = tuple(np.random.randint(0, 255, 3).tolist())

        color = id_color_map[track_id]
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        cv2.putText(frame, f"ID:{track_id} | {class_name}", (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)

        if track_id in prev_centers:
            prev_center = prev_centers[track_id]

            if track_id in line1_pass_times:
                if intersects(prev_center, (cx, cy), *ROI_LINE_2):
                    t1 = line1_pass_times.pop(track_id)
                    elapsed = time.time() - t1
                    speed_mps = KNOWN_DISTANCE_METERS / elapsed
                    speed_kmph = speed_mps * 3.6
                    print(f"🚗 ID: {track_id} | Class: {class_name} | Speed: {speed_kmph:.2f} km/h")
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    csv_writer.writerow([timestamp, track_id, class_name, round(speed_kmph, 2), KNOWN_DISTANCE_METERS])
                    speed_display[track_id] = (speed_kmph, time.time())
            else:
                if intersects(prev_center, (cx, cy), *ROI_LINE_1):
                    line1_pass_times[track_id] = time.time()

        prev_centers[track_id] = (cx, cy)

    for line in ROI_LINES:
        cv2.line(frame, tuple(line[0]), tuple(line[1]), (0, 255, 0), 2)

    for track_id, (speed_kmph, shown_time) in list(speed_display.items()):
        if time.time() - shown_time < SPEED_DISPLAY_DURATION:
            center = prev_centers.get(track_id)
            if center:
                cv2.putText(frame, f"{speed_kmph:.1f} km/h", center, cv2.FONT_HERSHEY_SIMPLEX, 0.6, id_color_map[track_id], 2)

    out.write(frame)

cap.release()
csv_file.close()
out.release()
cv2.destroyAllWindows()
