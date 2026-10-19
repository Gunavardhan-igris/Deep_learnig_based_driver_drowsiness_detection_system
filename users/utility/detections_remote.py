
from django.conf import settings
import os
import cv2
import numpy as np
import base64
from keras.models import load_model


class FatigueDetectionsRemote:
    model = None
    face_cascade = None
    leye_cascade = None
    reye_cascade = None

    def __init__(self):
        self._load_resources()

    def _load_resources(self):
        # Load the trained model only once.
        if FatigueDetectionsRemote.model is None:
            model_path = os.path.join(
                settings.MEDIA_ROOT,
                "models",
                "cnnCat2.h5"
            )

            if not os.path.isfile(model_path):
                raise FileNotFoundError(
                    f"Model file not found: {model_path}"
                )

            FatigueDetectionsRemote.model = load_model(model_path)

        # Load the face cascade only once.
        if FatigueDetectionsRemote.face_cascade is None:
            face_path = os.path.join(
                settings.MEDIA_ROOT,
                "haar cascade files",
                "haarcascade_frontalface_alt.xml"
            )

            FatigueDetectionsRemote.face_cascade = (
                cv2.CascadeClassifier(face_path)
            )

            if FatigueDetectionsRemote.face_cascade.empty():
                raise FileNotFoundError(
                    f"Could not load face cascade: {face_path}"
                )

        # Load the left-eye cascade only once.
        if FatigueDetectionsRemote.leye_cascade is None:
            left_eye_path = os.path.join(
                settings.MEDIA_ROOT,
                "haar cascade files",
                "haarcascade_lefteye_2splits.xml"
            )

            FatigueDetectionsRemote.leye_cascade = (
                cv2.CascadeClassifier(left_eye_path)
            )

            if FatigueDetectionsRemote.leye_cascade.empty():
                raise FileNotFoundError(
                    f"Could not load left-eye cascade: {left_eye_path}"
                )

        # Load the right-eye cascade only once.
        if FatigueDetectionsRemote.reye_cascade is None:
            right_eye_path = os.path.join(
                settings.MEDIA_ROOT,
                "haar cascade files",
                "haarcascade_righteye_2splits.xml"
            )

            FatigueDetectionsRemote.reye_cascade = (
                cv2.CascadeClassifier(right_eye_path)
            )

            if FatigueDetectionsRemote.reye_cascade.empty():
                raise FileNotFoundError(
                    f"Could not load right-eye cascade: {right_eye_path}"
                )

    def _preprocess_eye(self, eye_frame):
        eye = cv2.cvtColor(
            eye_frame,
            cv2.COLOR_BGR2GRAY
        )
        eye = cv2.resize(eye, (24, 24))
        eye = eye / 255.0
        eye = eye.reshape(24, 24, -1)

        return np.expand_dims(eye, axis=0)

    def _predict_eye(self, eye_frame):
        image = self._preprocess_eye(eye_frame)

        prediction = FatigueDetectionsRemote.model.predict(
            image,
            verbose=0
        )

        return int(np.argmax(prediction, axis=-1)[0])

    def _decode_base64_image(self, image_data):
        try:
            if not image_data or "," not in image_data:
                return None

            _, encoded = image_data.split(",", 1)
            img_bytes = base64.b64decode(encoded)
            np_array = np.frombuffer(img_bytes, dtype=np.uint8)

            return cv2.imdecode(
                np_array,
                cv2.IMREAD_COLOR
            )

        except (ValueError, TypeError):
            return None

    def predict_from_base64(self, image_data):
        frame = self._decode_base64_image(image_data)

        if frame is None:
            return {
                "fatigue": False,
                "drowsiness": 0,
                "left_eye": "Unknown",
                "right_eye": "Unknown",
                "status": "No valid frame"
            }

        gray = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2GRAY
        )

        faces = FatigueDetectionsRemote.face_cascade.detectMultiScale(
            gray,
            minNeighbors=5,
            scaleFactor=1.1,
            minSize=(25, 25)
        )

        if len(faces) == 0:
            return {
                "fatigue": False,
                "drowsiness": 0,
                "left_eye": "No face",
                "right_eye": "No face",
                "status": "No face detected"
            }

        # Detect eyes.
        left_eye = FatigueDetectionsRemote.leye_cascade.detectMultiScale(
            gray
        )

        right_eye = FatigueDetectionsRemote.reye_cascade.detectMultiScale(
            gray
        )

        left_pred = None
        right_pred = None

        # Predict the first detected right eye.
        for (x, y, w, h) in right_eye:
            try:
                eye_frame = frame[y:y + h, x:x + w]
                right_pred = self._predict_eye(eye_frame)
            except (ValueError, cv2.error):
                right_pred = None

            break

        # Predict the first detected left eye.
        for (x, y, w, h) in left_eye:
            try:
                eye_frame = frame[y:y + h, x:x + w]
                left_pred = self._predict_eye(eye_frame)
            except (ValueError, cv2.error):
                left_pred = None

            break

        self.face_count = len(faces)
        self.left_count = len(left_eye)
        self.right_count = len(right_eye)

        self.left_pred = left_pred
        self.right_pred = right_pred

        # Convert predictions into labels.
        left_label = "Unknown"
        right_label = "Unknown"

        if left_pred is not None:
            left_label = "Closed" if left_pred == 0 else "Open"

        if right_pred is not None:
            right_label = "Closed" if right_pred == 0 else "Open"

        # Calculate the percentage of detected eyes classified as closed.
        predictions = [left_pred, right_pred]

        closed_count = sum(
            1 for pred in predictions if pred == 0
        )

        known_count = sum(
            1 for pred in predictions if pred is not None
        )

        drowsiness = (
            round((closed_count / known_count) * 100, 1)
            if known_count
            else 0
        )

        fatigue = (
            left_pred == 0 and right_pred == 0
        )

        # Return the detection result.
        return {
            "fatigue": bool(fatigue),
            "drowsiness": drowsiness,
            "left_eye": left_label,
            "right_eye": right_label,
            "status": (
                "Drowsiness detected"
                if fatigue
                else "Eyes monitored"
            )
        }
