import cv2
import os

def tracking(frame, face_cascade, eye_cascade):

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)

    for (x, y, w, h) in faces:

        cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)

        roi_gray = gray[y: y + h, x: x + w]
        roi_color = frame[y: y + h, x: x + w]

        eyes = eye_cascade.detectMultiScale(roi_gray)

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

    while True:

        ret, frame = cap.read()

        tracking(frame, face_cascade, eye_cascade)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
