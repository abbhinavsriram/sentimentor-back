import time
from flask import Flask, render_template, Response, jsonify
import cv2
from keras.models import load_model
from rmn import RMN  # Assuming RMN is imported from a custom module
from io import BytesIO
import base64
from PIL import Image
from keras.preprocessing.image import img_to_array
import numpy as np

app = Flask(__name__)

m = RMN()
finalSentiment = 'neutral'
finalConfidence = 0
isDrowsy = False


def readb64(base64_string):
    sbuf = BytesIO()
    sbuf.write(base64.b64decode(base64_string))
    pimg = Image.open(sbuf)
    return cv2.cvtColor(np.array(pimg), cv2.COLOR_RGB2BGR)


@app.route('/sentiment')
def generate_frames(imageString=None):
    global finalSentiment, finalConfidence, isDrowsy
    sentiments = [0] * 7
    # image = readb64(imageString)
    image = cv2.imread("photo.jpg")
    results = m.detect_emotion_for_single_frame(image)
    if len(results) > 0:
        sentiments[0] = results[0]['proba_list'][0]['angry'] + 0.2
        sentiments[1] = results[0]['proba_list'][1]['disgust'] + 0.2
        sentiments[2] = results[0]['proba_list'][2]['fear'] + 0.3
        sentiments[3] = results[0]['proba_list'][3]['happy']
        sentiments[4] = results[0]['proba_list'][4]['sad'] + 0.1
        sentiments[5] = results[0]['proba_list'][5]['surprise'] + 0.4
        sentiments[6] = results[0]['proba_list'][6]['neutral'] - 0.4
    max_confidence = max(sentiments)
    max_confidence_idx = sentiments.index(max_confidence)
    if max_confidence_idx == 0:
        finalSentiment = "angry"
    elif max_confidence_idx == 1:
        finalSentiment = "disgust"
    elif max_confidence_idx == 2:
        finalSentiment = "fear"
    elif max_confidence_idx == 3:
        finalSentiment = "happy"
    elif max_confidence_idx == 4:
        finalSentiment = "sad"
    elif max_confidence_idx == 5:
        finalSentiment = "surprise"
    elif max_confidence_idx == 6:
        finalSentiment = "neutral"

    if finalSentiment.lower() not in ['neutral', 'happy']:
        finalSentiment = 'confused'
    else:
        finalSentiment = 'content'
    finalConfidence = max_confidence

    model = load_model("drowsiness_model/drowsiness_new7.h5")
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    left_eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_lefteye_2splits.xml')
    right_eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_righteye_2splits.xml')
    height, width, _ = image.shape
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    status1, status2 = 1, 1
    for (x, y, w, h) in faces:
        roi_gray = gray[y:y + h, x:x + w]
        left_eye = left_eye_cascade.detectMultiScale(roi_gray)
        right_eye = right_eye_cascade.detectMultiScale(roi_gray)
        for (x1, y1, w1, h1) in left_eye:
            eye1 = roi_gray[y1:y1 + h1, x1:x1 + w1]
            eye1 = cv2.resize(eye1, (145, 145))
            eye1_rgb = cv2.cvtColor(eye1, cv2.COLOR_GRAY2RGB)
            eye1_rgb = eye1_rgb.astype('float') / 255.0
            eye1_rgb = img_to_array(eye1_rgb)
            eye1_rgb = np.expand_dims(eye1_rgb, axis=0)
            pred1 = model.predict(eye1_rgb)
            status1 = np.argmax(pred1)
            break
        for (x2, y2, w2, h2) in right_eye:
            eye2 = roi_gray[y2:y2 + h2, x2:x2 + w2]
            eye2 = cv2.resize(eye2, (145, 145))
            eye2_rgb = cv2.cvtColor(eye2, cv2.COLOR_GRAY2RGB)
            eye2_rgb = eye2_rgb.astype('float') / 255.0
            eye2_rgb = img_to_array(eye2_rgb)
            eye2_rgb = np.expand_dims(eye2_rgb, axis=0)
            pred2 = model.predict(eye2_rgb)
            status2 = np.argmax(pred2)
            break
    isDrowsy = 1 if (status1 == 2 and status2 == 2) else 0

    data = {'sentiment': finalSentiment, 'confidence': finalConfidence, 'isDrowsy': isDrowsy}
    return jsonify(data)


@app.route('/fetch_values')
def fetch_values():
    global finalSentiment
    global finalConfidence
    if finalSentiment is None:
        return jsonify({'sentiment': 'neutral', 'confidence': 0})
    if finalSentiment.lower() not in ['neutral', 'happy']:
        sentiment = 'confused'
    else:
        sentiment = 'content'

    return jsonify({'sentiment': sentiment, 'confidence': finalConfidence})


def get_sentiment(image):
    results = m.detect_emotion_for_single_frame(image)
    print(results[0])
    sentiment = "None"
    if results is not None:
        if len(results) > 0:
            sentiment = results[0]['emo_label']
    if sentiment.lower() not in ['neutral', 'happy']:
        sentiment = 'confused'
    else:
        sentiment = 'content'
    return sentiment


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/video_feed')
def video_feed():
    # image_path = "./archive/sad/image0000028.jpg"
    # return Response(get_sentiment(image_path), mimetype='multipart/x-mixed-replace; boundary=frame')
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    app.run()
