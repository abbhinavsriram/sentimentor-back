import time
from flask import Flask, render_template, Response, jsonify
import cv2
from rmn import RMN  # Assuming RMN is imported from a custom module

app = Flask(__name__)

m = RMN()
results = None

def generate_frames():
    cap = cv2.VideoCapture(0)  # Capture video from webcam
    while True:
        sentiment = "neutral"
        ret, frame = cap.read()  # Read frame from webcam
        if not ret:
            break
        global results
        results = m.detect_emotion_for_single_frame(frame)  # Detect emotions
        if len(results) > 0:
            sentiment = results[0]['emo_label']
        # Draw sentiment on the frame
        frame_with_sentiment = frame.copy()
        cv2.putText(frame_with_sentiment, f"Sentiment: {sentiment}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
        frame_with_results = m.draw(frame_with_sentiment, results)  # Draw emotions on the frame
        ret, buffer = cv2.imencode('.jpg', frame_with_results)
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        # time.sleep(2)
    cap.release()

def get_sentiment(image):
    results = m.detect_emotion_for_single_frame(image)
    print(results)
    image = m.draw(image, results)
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
    image_path = "C:\\Users\\abbhi\\Pictures\\Camera Roll\\WIN_20240323_15_50_40_Pro.jpg"
    return Response(get_sentiment(image_path), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/fetch_values')
def fetch_values():
    global results
    sentiment = "None"
    if results is not None:
        if len(results) > 0:
            sentiment = results[0]['emo_label']
    if sentiment.lower() not in ['neutral', 'happy']:
        sentiment = 'confused'
    else:
        sentiment = 'happy'

    return jsonify({'sentiment': sentiment})

if __name__ == '__main__':
    app.run(debug=True)



    

