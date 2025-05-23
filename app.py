from flask import Flask, request, abort, send_file
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, ImageMessage, TextSendMessage, ImageSendMessage
import os
import cv2
import numpy as np
from collections import Counter

app = Flask(__name__)

# 請將以下兩個參數改成你自己的 LINE BOT 設定
LINE_CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
LINE_CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET')
# 請換成你自己的
line_bot_api = LineBotApi('TpWEfFJFfCvB9ZASbD+ho5Qqnx1nI3hXWXfK5/XUz13hZNVf1NX1YoBXvkOpVgTSXVvyziRtXRo5MXRJ91h5n4IMps991+RhECQV44SgNewWoteSAHLU/lGogMQiK1JD98UP+HG9Zbsit40rc13dVgdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('b4f29d84ef99d4145e5ee81397ce5177')

@app.route("/")
def home():
    return "LINE Bot is running!"

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
            )
        ]
    )

@app.route("/image")
def send_image():
    return send_file("annotated_pills.jpg", mimetype='image/jpeg')

def detect_pills(image_path):
    image = cv2.imread(image_path)
    output = image.copy()
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edged = cv2.Canny(blurred, 40, 120)
    edged = cv2.dilate(edged, None, iterations=2)
    edged = cv2.erode(edged, None, iterations=1)

    contours, _ = cv2.findContours(edged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    categories = []

    for contour in contours:
        area = cv2.contourArea(contour)
        if area < 300 or area > 5000:
            continue

        mask = np.zeros(gray.shape, dtype="uint8")
        cv2.drawContours(mask, [contour], -1, 255, -1)
        mean_hsv = cv2.mean(hsv, mask=mask)[:3]
        h, s, v = mean_hsv

        if (h < 10 or h > 170) and s > 100 and v > 100:
            label = "紅色小膠囊"
            color = (0, 0, 255)
        elif s < 50 and v > 160:
            label = "白色長條膠囊"
            color = (255, 255, 255)
        elif 35 <= h <= 95 and s > 60 and 50 < v < 180:
            label = "綠色長條膠囊"
            color = (0, 255, 0)
        else:
            label = "其他"
            color = (128, 128, 128)

        categories.append(label)
        M = cv2.moments(contour)
        if M["m00"] != 0:
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
            cv2.putText(output, label, (cX-40, cY), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        cv2.drawContours(output, [contour], -1, color, 2)

    count = Counter(categories)
    result_text = "\n".join([f"{label}：{count[label]} 顆" for label in sorted(count)])
    cv2.imwrite("annotated_pills.jpg", output)
    return result_text, "annotated_pills.jpg"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)