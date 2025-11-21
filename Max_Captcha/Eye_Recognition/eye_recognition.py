import numpy as np
from collections import deque
import cv2
import os

#def update(eye_prediction, history):
#    pass

class EyeTracker:

    def __init__(self, angle_threshold = 15):
        self.angle_threshold = angle_threshold

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
        
        # Calculate centers for all detections
        centers = [self.get_center(det) for det in detections]
        
        # Find all pairs that are relatively horizontal
        valid_pairs = []
        
        for i in range(len(centers)):
            for j in range(i + 1, len(centers)):
                angle = self.calculate_angle(centers[i], centers[j])
                
                if angle <= self.angle_threshold:
                    # Store the pair with their indices and angle
                    valid_pairs.append((i, j, angle))
        
        if len(valid_pairs) == 0:
            # No horizontal pairs found, return two leftmost detections
            sorted_dets = sorted(enumerate(detections), key=lambda x: x[1][0])
            return [sorted_dets[0][1], sorted_dets[1][1]]
        
        # Find the most horizontal pair (smallest angle)
        best_pair = min(valid_pairs, key=lambda x: x[2])
        i, j, _ = best_pair
        
        # Return the two detections corresponding to this pair
        return [detections[i], detections[j]]


    def tracking(self, frame, face_cascade, eye_cascade):

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)

        for (x, y, w, h) in faces:

            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)

            roi_gray = gray[y: y + h, x: x + w]
            roi_color = frame[y: y + h, x: x + w]

            eyes = eye_cascade.detectMultiScale(roi_gray)

            filtered_eyes = self.update(eyes)

            for (ex, ey, ew, eh) in eyes:
                cv2.rectangle(roi_color, (ex, ey), (ex+ew, ey + eh), (0, 255, 0), 2)

        
        cv2.imshow('Eye Tracking', frame)


if __name__ == "__main__":

    script_dir = os.path.dirname(os.path.abspath(__file__))

    face_cascade_path = os.path.join(script_dir, "haarcascade_frontalface_default.xml")
    eye_cascade_path = os.path.join(script_dir, "haarcascade_eye.xml")

    face_cascade = cv2.CascadeClassifier(face_cascade_path)
    eye_cascade = cv2.CascadeClassifier(eye_cascade_path)

    assert not face_cascade.empty()
    assert not eye_cascade.empty()

    cap = cv2.VideoCapture(0)

    fourcc = cv2.VideoWriter_fourcc(*'MP4V')
    out = cv2.VideoWriter('output.mp4', fourcc, 20.0, (640, 480))

    # scoring should start with no doubt...

    eye_tracker = EyeTracker()

    while True:

        ret, frame = cap.read()

        eye_tracker.tracking(frame, face_cascade, eye_cascade)
        out.write(frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
