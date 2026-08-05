from django.conf import settings
import os
import time
import cv2
import numpy as np
from keras.models import load_model
from pygame import mixer

class FatigueDetections:
    def start_process(self):
        # Initialize pygame mixer for alarm
        mixer.init()
        sound = mixer.Sound(os.path.join(settings.MEDIA_ROOT, 'alarm.wav'))

        # Load Haar cascade classifiers
        face = cv2.CascadeClassifier(
            os.path.join(settings.MEDIA_ROOT, 'haar cascade files', 'haarcascade_frontalface_alt.xml'))
        leye = cv2.CascadeClassifier(
            os.path.join(settings.MEDIA_ROOT, 'haar cascade files', 'haarcascade_lefteye_2splits.xml'))
        reye = cv2.CascadeClassifier(
            os.path.join(settings.MEDIA_ROOT, 'haar cascade files', 'haarcascade_righteye_2splits.xml'))

        # Load pre-trained model
        model = load_model(os.path.join(settings.MEDIA_ROOT, 'models', 'cnncat2.h5'))

        # Initialize video capture
        cap = cv2.VideoCapture(0)
        font = cv2.FONT_HERSHEY_COMPLEX_SMALL
        
        # Drowsiness detection variables
        drowsiness_score = 0
        drowsiness_threshold = 10  # Adjusted threshold for drowsiness detection
        alarm_triggered = False
        closed_eye_duration = None
        total_frames = 0
        closed_frames = 0
        warning_thickness = 2

        while True:
            ret, frame = cap.read()
            if not ret:
                break
                
            height, width = frame.shape[:2]
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Detect faces and eyes
            faces = face.detectMultiScale(gray, minNeighbors=5, scaleFactor=1.1, minSize=(25, 25))
            left_eye = leye.detectMultiScale(gray)
            right_eye = reye.detectMultiScale(gray)

            # Draw status bar
            cv2.rectangle(frame, (0, height - 50), (250, height), (0, 0, 0), thickness=cv2.FILLED)

            # Process face detection
            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (100, 100, 100), 1)

            # Initialize predictions
            rpred = [99]
            lpred = [99]

            # Process right eye
            for (x, y, w, h) in right_eye:
                r_eye = frame[y:y + h, x:x + w]
                r_eye = cv2.cvtColor(r_eye, cv2.COLOR_BGR2GRAY)
                r_eye = cv2.resize(r_eye, (24, 24))
                r_eye = r_eye / 255.0
                r_eye = r_eye.reshape(24, 24, -1)
                r_eye = np.expand_dims(r_eye, axis=0)
                rpred = np.argmax(model.predict(r_eye), axis=-1)
                break

            # Process left eye
            for (x, y, w, h) in left_eye:
                l_eye = frame[y:y + h, x:x + w]
                l_eye = cv2.cvtColor(l_eye, cv2.COLOR_BGR2GRAY)
                l_eye = cv2.resize(l_eye, (24, 24))
                l_eye = l_eye / 255.0
                l_eye = l_eye.reshape(24, 24, -1)
                l_eye = np.expand_dims(l_eye, axis=0)
                lpred = np.argmax(model.predict(l_eye), axis=-1)
                break

            # Update frame counter
            total_frames += 1

            # Drowsiness detection logic
            if rpred[0] == 0 and lpred[0] == 0:  # Both eyes closed
                drowsiness_score += 1
                closed_frames += 1
                cv2.putText(frame, "Eyes Closed", (10, height - 20), font, 1, (0, 0, 255), 1, cv2.LINE_AA)

                if closed_eye_duration is None:
                    closed_eye_duration = time.time()

                # Trigger alarm if eyes closed for 3+ seconds
                if closed_eye_duration and time.time() - closed_eye_duration >= 3 and not alarm_triggered:
                    try:
                        sound.play()
                        alarm_triggered = True
                    except:
                        pass
            else:  # Eyes open
                drowsiness_score = max(0, drowsiness_score - 1)
                cv2.putText(frame, "Eyes Open", (10, height - 20), font, 1, (0, 255, 0), 1, cv2.LINE_AA)
                closed_eye_duration = None
                alarm_triggered = False

            # Calculate drowsiness percentage
            drowsiness_percentage = (closed_frames / total_frames) * 100 if total_frames > 0 else 0

            # Display drowsiness metrics
            cv2.putText(frame, f'Drowsiness: {drowsiness_percentage:.2f}%', 
                       (10, height - 60), font, 1, (0, 255, 255), 1, cv2.LINE_AA)
            cv2.putText(frame, f'Score: {drowsiness_score}', 
                       (100, height - 20), font, 1, (255, 255, 255), 1, cv2.LINE_AA)

            # Visual warning for high drowsiness
            if drowsiness_score > drowsiness_threshold:
                warning_thickness = min(warning_thickness + 2, 16)
                cv2.rectangle(frame, (0, 0), (width, height), (0, 0, 255), warning_thickness)
                cv2.putText(frame, "DROWSINESS DETECTED!", (width//4, height//2), 
                           font, 2, (0, 0, 255), 2, cv2.LINE_AA)
                # Save snapshot
                cv2.imwrite(os.path.join(os.getcwd(), 'assets', 'static', 'drowsy_image.jpg'), frame)
            else:
                warning_thickness = max(warning_thickness - 2, 2)

            # Display frame
            cv2.imshow('Driver Drowsiness Detection (Press Q to Exit)', frame)
            
            # Exit on 'q' key
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        # Cleanup
        cap.release()
        cv2.destroyAllWindows()
        return alarm_triggered