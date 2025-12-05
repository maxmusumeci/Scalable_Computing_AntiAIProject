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
            "http://localhost:5500",  # Keep for local testing
            "http://127.0.0.1:5500"
        ]
    }
})

class FaceOrientationTracker:
    def __init__(self, window_size=30, switch_threshold=5):
        self.orientation_history = deque(maxlen=window_size)
        self.switch_threshold = switch_threshold

    def update(self, detected_orientation):
        self.orientation_history.append(detected_orientation)

        if len(self.orientation_history) < 2:
            return False, 0
        
        switches = 0
        for i in range(1, len(self.orientation_history)):
            prev = self.orientation_history[i-1]
            curr = self.orientation_history[i]

            if prev is not None and curr is not None and prev != curr:
                switches += 1

        is_suspicious = switches > self.switch_threshold
        return is_suspicious, switches
    
class StillnessDetector:
    def __init__(self, history_size=150, stillness_threshold=5.0):
        self.frame_history = deque(maxlen=2)
        self.movement_history = deque(maxlen=history_size)
        self.stillness_threshold = stillness_threshold

    def calculate_movement(self, frame1, frame2):

        if frame1 is None or frame2 is None:
            return None
        
        if len(frame1.shape) == 3:
            gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
            gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)

        else:
            gray1, gray2 = frame1, frame2

        if gray1.shape != gray2.shape:
            return None

        diff = cv2.absdiff(gray1, gray2)

        return np.mean(diff)
    
    def update(self, face_region):
        self.frame_history.append(face_region.copy() if face_region is not None else None)

        if len(self.frame_history) < 2:
            return False, None
        
        movement = self.calculate_movement(self.frame_history[0], self.frame_history[1])

        if movement is not None:
            self.movement_history.append(movement)

        if len(self.movement_history) < self.movement_history.maxlen * 0.8:
            return False, None
        
        avg_movement = np.mean(self.movement_history)
        is_suspicious = avg_movement < self.stillness_threshold

        return is_suspicious, avg_movement

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


    def process_frame(self, frame, face_cascades, eye_cascade, orientation_tracker, stillness_tracker):
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        #faces = face_cascades.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)

        detected_orientation = None
        face_found = None
        is_flipped = False
        is_orientation_suspicous = False
        is_stillness_suspicious = False

        for orientation_name, cascade in face_cascades.items():
            faces = cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)

            if len(faces) > 0:
                detected_orientation = orientation_name + '_left' if orientation_name == 'profile' else orientation_name
                face_found = faces[0]
                break

            if orientation_name == 'profile':
                flipped_gray = cv2.flip(gray, 1)
                faces = cascade.detectMultiScale(flipped_gray, scaleFactor=1.3, minNeighbors=5)

                if len(faces) > 0:
                    detected_orientation = 'profile_right'
                    x, y, w, h = faces[0]
                    x_original = gray.shape[1] - x - w
                    face_found = (x_original, y, w, h)
                    is_flipped = True
                    break

        is_orientation_suspicous, switch_count = orientation_tracker.update(detected_orientation)

        face_detected = face_found is not None
        eyes_detected = 0

        if face_detected:
            x, y, w, h = face_found
            if is_flipped:
                flipped_gray = cv2.flip(gray, 1)
                x_flipped = gray.shape[1] - x - w
                roi_gray = flipped_gray[y: y + h, x_flipped: x_flipped + w]
            else:
                roi_gray = gray[y: y + h, x: x + w]

            is_stillness_suspicious, avg_movement = stillness_tracker.update(roi_gray)

            eyes = eye_cascade.detectMultiScale(roi_gray)
            filtered_eyes = self.update(eyes)
            eyes_detected = len(filtered_eyes)

        frame_valid = face_detected and eyes_detected >= 1
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
            'orientation_suspicious': is_orientation_suspicous,
            'stillness_suspicious': is_stillness_suspicious,
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
side_cascade_path = os.path.join(script_dir, "haarcascade_profileface.xml")

face_cascades = {
    'frontal': cv2.CascadeClassifier(face_cascade_path),
    'profile': cv2.CascadeClassifier(side_cascade_path)
}

eye_cascade = cv2.CascadeClassifier(eye_cascade_path)

for name, cascade in face_cascades.items():
    assert not cascade.empty()

assert not eye_cascade.empty()

#cap = cv2.VideoCapture(0)

#fourcc = cv2.VideoWriter_fourcc(*'MP4V')
#out = cv2.VideoWriter('output.mp4', fourcc, 20.0, (640, 480))

# scoring should start with no doubt...

eye_tracker = EyeTracker(violation_threshold=80, max_violations=5)
orientation_tracker = FaceOrientationTracker(window_size=30, switch_threshold=5)
stillness_tracker = StillnessDetector(history_size=150, stillness_threshold=5.0)

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
    return send_file('public/exam.html')

@app.route('/process_frame', methods=['POST'])
def process_frame():
    try:
        data = request.get_json()
        image_data = data['image'].split(',')[1]

        nparr = np.frombuffer(base64.b64decode(image_data), np.uint8)

        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        processed_frame, tracking_data = eye_tracker.process_frame(frame, face_cascades, eye_cascade, orientation_tracker, stillness_tracker)
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
    app.run(debug=True, host='0.0.0.0', port=5501)