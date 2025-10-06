import cv2
import mediapipe as mp
import math

# Khởi tạo MediaPipe Pose
mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

# Hàm tính góc giữa 3 điểm (vai - khuỷu tay - cổ tay)
def calculate_angle(a, b, c):
    a = [a.x, a.y]
    b = [b.x, b.y]
    c = [c.x, c.y]

    radians = math.atan2(c[1]-b[1], c[0]-b[0]) - math.atan2(a[1]-b[1], a[0]-b[0])
    angle = abs(radians*180.0/math.pi)
    if angle > 180.0:
        angle = 360 - angle
    return angle

# Mở webcam (0) hoặc video (đổi đường dẫn nếu cần)
cap = cv2.VideoCapture(0)

counter = 0
stage = None  # "up" hoặc "down"

with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Đọc ảnh và xử lý bằng mediapipe
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(image)
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        try:
            landmarks = results.pose_landmarks.landmark

            # Lấy khớp vai, khuỷu tay, cổ tay bên phải
            shoulder = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value]
            elbow = landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value]
            wrist = landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value]

            # Tính góc khuỷu tay
            angle = calculate_angle(shoulder, elbow, wrist)

            # Đếm số lần push-up
            if angle > 160:
                stage = "up"
            if angle < 90 and stage == "up":
                stage = "down"
                counter += 1
                print(f"Đã đếm được: {counter}")

            # Hiển thị kết quả lên màn hình
            cv2.putText(image, f'Push-up count: {counter}', (10, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0,255,0), 3, cv2.LINE_AA)
            cv2.putText(image, f'Angle: {int(angle)}', (10, 100),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2, cv2.LINE_AA)

            # Vẽ khung xương
            mp_drawing.draw_landmarks(
                image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
        
        except:
            pass

        cv2.imshow('Push-up Counter', image)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()

