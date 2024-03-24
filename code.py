# from flask import Flask, render_template, Response
# import cv2
# import numpy as np
# from keras.models import load_model
# from keras.preprocessing.image import img_to_array
#
# app = Flask(__name__)
#
# classes = ['Closed', 'Open']
# model = load_model("drowsiness_new7.h5")
# face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
# left_eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_lefteye_2splits.xml')
# right_eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_righteye_2splits.xml')
# count = 0
#
# def detect_drowsiness(frame):
#     global count
#     height, width, _ = frame.shape
#     gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
#     faces = face_cascade.detectMultiScale(gray, 1.3, 5)
#
#     drowsiness_text = "Eyes Open"  # Default text
#     for (x, y, w, h) in faces:
#         roi_gray = gray[y:y+h, x:x+w]
#         left_eye = left_eye_cascade.detectMultiScale(roi_gray)
#         right_eye = right_eye_cascade.detectMultiScale(roi_gray)
#         for (x1, y1, w1, h1) in left_eye:
#             eye1 = roi_gray[y1:y1+h1, x1:x1+w1]
#             eye1 = cv2.resize(eye1, (145, 145))
#             eye1_rgb = cv2.cvtColor(eye1, cv2.COLOR_GRAY2RGB)
#             eye1_rgb = eye1_rgb.astype('float') / 255.0
#             eye1_rgb = img_to_array(eye1_rgb)
#             eye1_rgb = np.expand_dims(eye1_rgb, axis=0)
#             pred1 = model.predict(eye1_rgb)
#             status1 = np.argmax(pred1)
#             break
#
#         for (x2, y2, w2, h2) in right_eye:
#             eye2 = roi_gray[y2:y2 + h2, x2:x2 + w2]
#             eye2 = cv2.resize(eye2, (145, 145))
#             eye2_rgb = cv2.cvtColor(eye2, cv2.COLOR_GRAY2RGB)
#             eye2_rgb = eye2_rgb.astype('float') / 255.0
#             eye2_rgb = img_to_array(eye2_rgb)
#             eye2_rgb = np.expand_dims(eye2_rgb, axis=0)
#             pred2 = model.predict(eye2_rgb)
#             status2 = np.argmax(pred2)
#             break
#
#     if status1 == 2 and status2 == 2:
#         count += 1
#         drowsiness_text = "Drowsiness Alert!!!" if count >= 10 else "Eyes Closed"
#     else:
#         count = 0
#
#     return drowsiness_text
#
# def generate_frames():
#     camera = cv2.VideoCapture(0)
#     while True:
#         success, frame = camera.read()
#         if not success:
#             break
#         else:
#             frame_text = detect_drowsiness(frame)
#             cv2.putText(frame, frame_text, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
#             ret, buffer = cv2.imencode('.jpg', frame)
#             if ret:
#                 frame_bytes = buffer.tobytes()
#                 yield (b'--frame\r\n'
#                        b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

import base64
from PIL import Image
import cv2
from io import StringIO
import numpy as np