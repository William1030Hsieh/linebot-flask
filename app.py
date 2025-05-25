
from flask import Flask, request, abort, send_file
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, ImageMessage, TextSendMessage, ImageSendMessage
import os
import cv2
import numpy as np
import tensorflow as tf

app = Flask(__name__)

line_bot_api = LineBotApi('TpWEfFJFfCvB9ZASbD+ho5Qqnx1nI3hXWXfK5/XUz13hZNVf1NX1YoBXvkOpVgTSXVvyziRtXRo5MXRJ91h5n4IMps991+RhECQV44SgNewWoteSAHLU/lGogMQiK1JD98UP+HG9Zbsit40rc13dVgdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('b4f29d84ef99d4145e5ee81397ce5177')



try:
    interpreter = tf.lite.Interpreter(model_path="pill_classifier_model.tflite")
    print("Model loaded successfully.")
except ValueError as e:
    print("Model load failed:", e)

with open('pill_classifier_model.tflite', 'wb') as f:
    f.write(tflite_model)

with open("pill_classifier_model.tflite", "wb") as f:
    f.write(tflite_model)

@app.route("/")
def home():
    return "LINE Bot with TFLite model is running."

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=ImageMessage)
def handle_image(event):
    message_content = line_bot_api.get_message_content(event.message.id)
    image_path = "pills.jpg"
    with open(image_path, 'wb') as f:
        for chunk in message_content.iter_content():
            f.write(chunk)
    result_text, annotated_path = detect_pills(image_path)
    line_bot_api.reply_message(
        event.reply_token,
        [
            TextSendMessage(text=result_text),
            ImageSendMessage(
                original_content_url=request.url_root + "image",
                preview_image_url=request.url_root + "image"
                model = tf.keras.models.load_model("pill_classifier_model.h5")
                model = tf.keras.models.load_model("pill_classifier_model.h5")

                converter = tf.lite.TFLiteConverter.from_saved_model('pill_classifier_model.tflite')
                tflite_model = converter.convert()

                converter = tf.lite.TFLiteConverter.from_keras_model(model)
                tflite_model = converter.convert()
            )
        ]
    )

@app.route("/image")
def send_image():
    return send_file("annotated_pills.jpg", mimetype='image/jpeg')

def detect_pills(image_path):
    image = cv2.imread(image_path)
    output = image.copy()
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (7, 7), 0)
    edged = cv2.Canny(blur, 50, 150)
    edged = cv2.dilate(edged, None, iterations=1)
    edged = cv2.erode(edged, None, iterations=1)

    contours, _ = cv2.findContours(edged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    counts = {label: 0 for label in class_labels}

    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        if w * h < 500:
            continue
        roi = image[y:y+h, x:x+w]
        roi_resized = cv2.resize(roi, (224, 224))
        input_array = np.expand_dims(roi_resized / 255.0, axis=0).astype(np.float32)
        interpreter.set_tensor(input_details[0]['index'], input_array)
        interpreter.invoke()
        output_data = interpreter.get_tensor(output_details[0]['index'])
        class_id = int(np.argmax(output_data))
        label = class_labels[class_id]
        counts[label] += 1
        cv2.rectangle(output, (x, y), (x+w, y+h), (0, 255, 0), 2)
        cv2.putText(output, label, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (36,255,12), 2)

        interpreter = tf.lite.Interpreter(model_path="pill_classifier_model.tflite")
interpreter.allocate_tensors()
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()
class_labels = ['green_capsule', 'red_capsule', 'white_capsule', 'yellow_pill']
    result_text = "\n".join([f"{k}：{v} 顆" for k, v in counts.items() if v > 0])
    cv2.imwrite("annotated_pills.jpg", output)
    return result_text, "annotated_pills.jpg"

if __name__ == "__main__":
     port = int(os.environ.get('PORT', 10000))
     app.run(host='0.0.0.0', port=port)
    #app.run(host="0.0.0.0", port=10000)
