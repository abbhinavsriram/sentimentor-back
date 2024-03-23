import time
from flask import Flask, render_template, Response, jsonify
import cv2
from rmn import RMN  # Assuming RMN is imported from a custom module

app = Flask(__name__)

m = RMN()
finalSentiment = 'neutral'
finalConfidence = 0
isDrowsy = False


@app.route('/sentiment')
def generate_frames():
    cap = cv2.VideoCapture(0)  # Capture video from webcam
    start_time = time.time()  # Record the start time
    while True:
        if time.time() - start_time >= 5:
            break

        sentiment = "neutral"
        sentiments = [0] * 7
        ret, frame = cap.read()  # Read frame from webcam
        if not ret:
            break

        results = m.detect_emotion_for_single_frame(frame)  # Detect emotions
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

        finalConfidence = max_confidence

        # Sleep for a short interval to prevent excessive CPU usage
        time.sleep(0.1)

    # # print(sentiment)
    # # Draw sentiment on the frame
    # frame_with_sentiment = frame.copy()
    # cv2.putText(frame_with_sentiment, f"Sentiment: {sentiment}", (10, 30),
    #             cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
    # frame_with_results = m.draw(frame_with_sentiment, results)  # Draw emotions on the frame
    # ret, buffer = cv2.imencode('.jpg', frame_with_results)
    # frame_bytes = buffer.tobytes()
    # yield (b'--frame\r\n'
    #        b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
    # time.sleep(2)
    # # yield jsonify({'sentiment': finalSentiment, 'confidence': finalConfidence})
    cap.release()

    if finalSentiment.lower() not in ['neutral', 'happy']:
        finalSentiment = 'confused'
    else:
        finalSentiment = 'content'

    # Return the data in JSON format after 5 seconds
    data = {'sentiment': finalSentiment, 'confidence': finalConfidence}
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
