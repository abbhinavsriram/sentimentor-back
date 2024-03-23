from flask import Flask, render_template, Response
import cv2
from rmn import RMN  # Assuming RMN is imported from a custom module

app = Flask(__name__)

m = RMN()

def generate_frames():
    cap = cv2.VideoCapture(0)  # Capture video from webcam
    while True:
        ret, frame = cap.read()  # Read frame from webcam
        if not ret:
            break
        results = m.detect_emotion_for_single_frame(frame)  # Detect emotions
        frame_with_results = m.draw(frame, results)  # Draw emotions on the frame
        ret, buffer = cv2.imencode('.jpg', frame_with_results)
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
    cap.release()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(debug=True)