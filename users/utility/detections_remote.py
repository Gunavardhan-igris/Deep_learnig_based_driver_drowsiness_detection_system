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
        if FatigueDetectionsRemote.model is None:
            FatigueDetectionsRemote.model = load_model(os.path.join(settings.MEDIA_ROOT, 'models', 'cnncat2.h5'))

        if FatigueDetectionsRemote.face_cascade is None:
            FatigueDetectionsRemote.face_cascade = cv2.CascadeClassifier(
                os.path.join(settings.MEDIA_ROOT, 'haar cascade files', 'haarcascade_frontalface_alt.xml'))

        if FatigueDetectionsRemote.leye_cascade is None:
            FatigueDetectionsRemote.leye_cascade = cv2.CascadeClassifier(
                os.path.join(settings.MEDIA_ROOT, 'haar cascade files', 'haarcascade_lefteye_2splits.xml'))

        if FatigueDetectionsRemote.reye_cascade is None:
            FatigueDetectionsRemote.reye_cascade = cv2.CascadeClassifier(
                os.path.join(settings.MEDIA_ROOT, 'haar cascade files', 'haarcascade_righteye_2splits.xml'))

    def _preprocess_eye(self, eye_frame):
        eye = cv2.cvtColor(eye_frame, cv2.COLOR_BGR2GRAY)
        eye = cv2.resize(eye, (24, 24))
        eye = eye / 255.0
        eye = eye.reshape(24, 24, -1)
        return np.expand_dims(eye, axis=0)

    def _predict_eye(self, eye_frame):
        image = self._preprocess_eye(eye_frame)
        prediction = FatigueDetectionsRemote.model.predict(image, verbose=0)
        return np.argmax(prediction, axis=-1)[0]

    def _decode_base64_image(self, image_data):
        try:
            _, encoded = image_data.split(',', 1)
            img_bytes = base64.b64decode(encoded)
            np_array = np.frombuffer(img_bytes, np.uint8)
            return cv2.imdecode(np_array, cv2.IMREAD_COLOR)
        except Exception:
            return None

    def predict_from_base64(self, image_data):
        frame = self._decode_base64_image(image_data)
        if frame is None:
            return False

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = FatigueDetectionsRemote.face_cascade.detectMultiScale(
            gray, minNeighbors=5, scaleFactor=1.1, minSize=(25, 25)
        )
        if len(faces) == 0:
            return False

        left_eye = FatigueDetectionsRemote.leye_cascade.detectMultiScale(gray)
        right_eye = FatigueDetectionsRemote.reye_cascade.detectMultiScale(gray)

        left_pred = None
        right_pred = None

        # detect first right eye
        for (x, y, w, h) in right_eye:
            try:
                right_pred = self._predict_eye(frame[y:y + h, x:x + w])
            except Exception:
                right_pred = None
            break

        # detect first left eye
        for (x, y, w, h) in left_eye:
            try:
                left_pred = self._predict_eye(frame[y:y + h, x:x + w])
            except Exception:
                left_pred = None
            break

        # store metadata on the instance for debugging
        self.face_count = len(faces)
        self.left_count = len(left_eye)
        self.right_count = len(right_eye)
        self.left_pred = int(left_pred) if left_pred is not None else None
        self.right_pred = int(right_pred) if right_pred is not None else None

        # If both eyes classified as closed (class 0) -> fatigue
        fatigue = (self.left_pred == 0) and (self.right_pred == 0)

        # Save the current frame snapshot used for reporting (static path)
        try:
            out_path = os.path.join(os.getcwd(), 'assets', 'static', 'drowsy_image.jpg')
            cv2.imwrite(out_path, frame)
        except Exception:
            pass

        return bool(fatigue)
