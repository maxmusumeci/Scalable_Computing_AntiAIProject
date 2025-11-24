from flask import Flask, send_file, jsonify, request
from flask_cors import CORS
import numpy as np
from collections import deque
import cv2
import os
import base64

app = Flask(__name__)
# Replace 'your-app.web.app' with your actual Firebase hosting URL
CORS(app, resources={
    r"/*": {
        "origins": [
            "https://exam-portal-captcha-test.web.app",
            "https://your-app.firebaseapp.com",
            "http://localhost:5000",  # Keep for local testing
            "http://127.0.0.1:5000"
        ]
    }
})

class EyeTracker:

    def __init__(self, angle_threshold = 15, violation_threshold=80, max_violations=5):
        self.angle_threshold = angle_threshold
        self.violation_threshold = violation_threshold
        self.max_violations = max_violations

        self.frame_history = deque(maxlen=violation_threshold)
        self.violation_count = 0
        self.consecutive_violations = 0

    def get_center(self, box):
        x, y, w, h = box
        return ((x + w) // 2, (y + h)// 2)
    
    def calculate_angle(self, center1, center2):
        x1, y1, = center1
        x2, y2 = center2

        dx = x2 - x1
        dy = y2 - y1

        if dx == 0:
            return 90

        angle = abs(np.degrees(np.arctan(dy / dx)))
        return angle
    
    def update(self, detections):
        """Filter detections to find the two most horizontally aligned eyes"""
        if len(detections) == 0:
            return []
        
        if len(detections) <= 2:
            return list(detections)
        
        centers = [self.get_center(det) for det in detections]
        
        valid_pairs = []
        
        for i in range(len(centers)):
            for j in range(i + 1, len(centers)):
                angle = self.calculate_angle(centers[i], centers[j])
                
                if angle <= self.angle_threshold:
                    valid_pairs.append((i, j, angle))
        
        if len(valid_pairs) == 0:
            sorted_dets = sorted(enumerate(detections), key=lambda x: x[1][0])
            return [sorted_dets[0][1], sorted_dets[1][1]]
        
        best_pair = min(valid_pairs, key=lambda x: x[2])
        i, j, _ = best_pair
        
        return [detections[i], detections[j]]


    # def tracking(self, frame, face_cascade, eye_cascade):

    #     gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    #     faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)

    #     for (x, y, w, h) in faces:

    #         cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)

    #         roi_gray = gray[y: y + h, x: x + w]
    #         roi_color = frame[y: y + h, x: x + w]

    #         eyes = eye_cascade.detectMultiScale(roi_gray)

    #         filtered_eyes = self.update(eyes)

    #         for (ex, ey, ew, eh) in eyes:
    #             cv2.rectangle(roi_color, (ex, ey), (ex+ew, ey + eh), (0, 255, 0), 2)

        
    #     cv2.imshow('Eye Tracking', frame)

    def process_frame(self, frame, face_cascade, eye_cascade):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)

        face_detected = len(faces) > 0
        eyes_detected = 0

        for (x, y, w, h) in faces:
            roi_gray = gray[y: y + h, x: x + w]

            eyes = eye_cascade.detectMultiScale(roi_gray)
            filtered_eyes = self.update(eyes)
            eyes_detected = len(filtered_eyes)

        frame_valid = face_detected and eyes_detected >= 2
        self.frame_history.append(frame_valid)

        if len(self.frame_history) == self.violation_threshold:
            if not any(self.frame_history):
                self.violation_count += 1
            else:
                self.consecutive_violations = 0

        status = "ACTIVE"
        warning_message = None
        should_terminate = False

        if self.violation_count >= self.max_violations:
            status = "TERMINATED"
            warning_message = "Exam terminated: Attention violation"
            should_terminate = True

        elif self.consecutive_violations > 0:
            status = "WARNING"
            warning_message = f"Warning: Not looking at screen"

        return frame, {
            'face_detected': face_detected,
            'eyes_detected': eyes_detected,
            'frame_valid': frame_valid,
            'violation_count': self.violation_count,
            'max_violations': self.max_violations,
            'status': status,
            'warning_message': warning_message,
            'should_terminate': should_terminate,
            'consecutive_invalid_frames': self.violation_threshold - sum(self.frame_history)
        }
    
    def reset(self):
        self.frame_history.clear()
        self.violation_count = 0
        self.consecutive_violations = 0



script_dir = os.path.dirname(os.path.abspath(__file__))
face_cascade_path = os.path.join(script_dir, "haarcascade_frontalface_default.xml")
eye_cascade_path = os.path.join(script_dir, "haarcascade_eye.xml")

face_cascade = cv2.CascadeClassifier(face_cascade_path)
eye_cascade = cv2.CascadeClassifier(eye_cascade_path)

assert not face_cascade.empty()
assert not eye_cascade.empty()

#cap = cv2.VideoCapture(0)

#fourcc = cv2.VideoWriter_fourcc(*'MP4V')
#out = cv2.VideoWriter('output.mp4', fourcc, 20.0, (640, 480))

# scoring should start with no doubt...

eye_tracker = EyeTracker(violation_threshold=80, max_violations=5)

    # while True:

    #     ret, frame = cap.read()

    #     eye_tracker.process_frame(frame, face_cascade, eye_cascade)
    #     out.write(frame)

    #     if cv2.waitKey(1) & 0xFF == ord('q'):
    #         break

    # cap.release()
    # cv2.destroyAllWindows()

@app.route('/')
def index():
    return send_file('index.html')

@app.route('/process_frame', methods=['POST'])
def process_frame():
    try:
        data = request.get_json()
        image_data = data['image'].split(',')[1]

        nparr = np.frombuffer(base64.b64decode(image_data), np.uint8)

        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        processed_frame, tracking_data = eye_tracker.process_frame(frame, face_cascade, eye_cascade)
        _, buffer = cv2.imencode('.jpg', processed_frame)
        processed_image = base64.b64encode(buffer).decode('utf-8')

        return jsonify({
            'success': True,
            'image': f'data:image/jpeg;base64,{processed_image}',
            'tracking': tracking_data
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    
@app.route('/reset_tracking', methods=['POST'])
def reset_tracking():
    eye_tracker.reset()
    return jsonify({'success': True})

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)