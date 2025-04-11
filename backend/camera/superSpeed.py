import sys
sys.path.insert(0, "/usr/lib/python3/dist-packages/") 

import os
import cv2
import csv
import time
import math
import numpy as np
from datetime import datetime
from ultralytics import YOLO
from supervision import Detections, ByteTrack
from supervision.geometry.core import Point
from supervision.draw.color import Color
from supervision.draw.utils import draw_line

# === 설정 ===
MODEL_PATH = "yolov8n.engine"
CSV_PATH = "speed_log.csv"
KNOWN_DISTANCE_METERS = 35.0

ROI_LINE_1 = np.array([[0, 250], [640, 250]], dtype=int)
ROI_LINE_2 = np.array([[0, 300], [640, 300]], dtype=int)
ROI_LINES = [ROI_LINE_1, ROI_LINE_2]
SPEED_DISPLAY_DURATION = 2.0  # 초

# GStreamer USB 카메라 입력
gst_input = (
    "v4l2src device=/dev/video0 ! "
    "video/x-raw, width=640, height=480, framerate=30/1 ! "
    "videoconvert ! appsink"
)

# GStreamer UDP 출력
gst_output = (
    "appsrc ! videoconvert ! "
    "x264enc tune=zerolatency bitrate=2000 speed-preset=ultrafast ! "
    "rtph264pay config-interval=1 pt=96 ! "
    "udpsink host=192.168.10.101 port=8554"
)

cap = cv2.VideoCapture(gst_input, cv2.CAP_GSTREAMER)
out = cv2.VideoWriter(gst_output, cv2.CAP_GSTREAMER, 0, 30, (640, 480), True)

# === 유틸 ===
def intersects(p1, p2, q1, q2):
    def ccw(a, b, c):
        return (c[1] - a[1]) * (b[0] - a[0]) > (b[1] - a[1]) * (c[0] - a[0])
    return ccw(p1, q1, q2) != ccw(p2, q1, q2) and ccw(p1, p2, q1) != ccw(p1, p2, q2)

def get_centroids_from_detections(detections: Detections) -> list:
    return [
        (
            int((x1 + x2) / 2),
            int((y1 + y2) / 2)
        )
        for (x1, y1, x2, y2) in detections.xyxy
    ]

def draw_annotated(frame, detections: Detections, id_color_map):
    for box, track_id in zip(detections.xyxy, detections.tracker_id):
        x1, y1, x2, y2 = map(int, box)
        color = id_color_map.get(track_id, (0, 255, 255))
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        if track_id is not None:
            cv2.putText(frame, f"ID: {int(track_id)}", (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
    return frame

def generate_color_for_id(track_id):
    np.random.seed(int(track_id))
    return tuple(np.random.randint(0, 255, 3).tolist())

# === 모델 & 트래커 ===
model = YOLO(MODEL_PATH, task="detect")
tracker = ByteTrack()

# === CSV 경로 설정 ===
now = datetime.now()
year = now.strftime("%Y")
month = now.strftime("%m")
day = now.strftime("%d")

# 경로 구성: logs/년/월
log_dir = os.path.join("logs", year, month)
os.makedirs(log_dir, exist_ok=True)  # 폴더 없으면 생성

# 파일명: speed_log_날짜.csv
log_filename = f"speed_log_{day}.csv"
CSV_PATH = os.path.join(log_dir, log_filename)

# === CSV 파일 열기 (쓰기 모드, 새로 생성) ===
csv_file = open(CSV_PATH, mode="w", newline="")
csv_writer = csv.writer(csv_file)
csv_writer.writerow(["timestamp", "track_id", "class", "speed_kmph", "distance_m"])

# === 상태 저장 ===
prev_centers = {}
line1_pass_times = {}
speed_display = {}
id_color_map = {}

# === 비디오 스트림 ===

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.resize(frame, (640, 480))
    results = model.track(frame, persist=True, conf=0.4, iou=0.5, verbose=False)
    detections = Detections.from_ultralytics(results[0])
    detections = tracker.update_with_detections(detections)

    centers = get_centroids_from_detections(detections)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for i, track_id in enumerate(detections.tracker_id):
        if track_id is None:
            continue

        center = centers[i]
        cls = detections.class_id[i]

        if track_id not in id_color_map:
            id_color_map[track_id] = generate_color_for_id(track_id)

        if track_id in prev_centers:
            prev_center = prev_centers[track_id]

            # ROI2 통과 시 속도 계산
            if track_id in line1_pass_times:
                if intersects(prev_center, center, *ROI_LINE_2):
                    t1 = line1_pass_times.pop(track_id)
                    t2 = time.time()
                    elapsed = t2 - t1
                    speed_mps = KNOWN_DISTANCE_METERS / elapsed
                    speed_kmph = speed_mps * 3.6

                    print(f"🚗 ID: {track_id} | Class: {cls} | Speed: {speed_kmph:.2f} km/h")
                    csv_writer.writerow([timestamp, track_id, cls, round(speed_kmph, 2), KNOWN_DISTANCE_METERS])
                    
                    speed_display[track_id] = (speed_kmph, time.time())

            else:
                if intersects(prev_center, center, *ROI_LINE_1):
                    line1_pass_times[track_id] = time.time()

        prev_centers[track_id] = center

    # === 시각화 ===
    frame = draw_annotated(frame, detections, id_color_map)

    for line in ROI_LINES:
        draw_line(
            frame,
            Point(*line[0]),
            Point(*line[1]),
            color=Color.GREEN,
            thickness=2
        )

    # 속도 표시 유지
    for track_id, (speed_kmph, shown_time) in speed_display.items():
        if time.time() - shown_time < SPEED_DISPLAY_DURATION:
            center = prev_centers.get(track_id)
            if center:
                cv2.putText(
                    frame,
                    f"{speed_kmph:.1f} km/h",
                    center,
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    id_color_map.get(track_id, (0, 0, 255)),
                    2
                )
    out.write(frame)  # GStreamer로 전송
    cv2.imshow("Speed Estimation", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
out.release()
csv_file.close()
cv2.destroyAllWindows()
