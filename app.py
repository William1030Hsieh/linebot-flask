from flask import Flask, request, abort
import requests
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from linebot.models import ImageMessage
import os
from collections import Counter
import cv2
import numpy as np
opencv- python

app = Flask(__name__)

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
    except Exception as e:
        print("Error:", e)
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=ImageMessage)
def handle_image(event):
    message_content = line_bot_api.get_message_content(event.message.id)

    # 儲存照片檔案
    image_path = "pills.jpg"
    with open(image_path, "wb") as f:
        for chunk in message_content.iter_content():
            f.write(chunk)

    # 呼叫模型分析（目前回傳假資料，你日後可替換成模型推論）
    result = detect_pills(image_path)

    # 回傳結果給使用者
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=result)
    )

def detect_pills(image_path):
    image = cv2.imread(image_path)
    output = image.copy()
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (11, 11), 0)
    edged = cv2.Canny(blurred, 30, 150)
    edged = cv2.dilate(edged, None, iterations=2)
    edged = cv2.erode(edged, None, iterations=1)
    contours, _ = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    pill_info = []

    for contour in contours:
        area = cv2.contourArea(contour)
        if area < 100:
            continue

        (x, y), radius = cv2.minEnclosingCircle(contour)
        shape = "圓形" if 0.9 <= radius/np.sqrt(area/np.pi) <= 1.1 else "橢圓/長條"

        mask = np.zeros(gray.shape, dtype="uint8")
        cv2.drawContours(mask, [contour], -1, 255, -1)
        mean_color = cv2.mean(image, mask=mask)[:3]
        b, g, r = mean_color
        color = "白色"
        if r > 150 and g < 100 and b < 100:
            color = "紅色"
        elif b > 150 and r < 100:
            color = "藍色"
        elif r > 200 and g > 200 and b > 200:
            color = "白色"
        elif g > 150 and r < 100:
            color = "綠色"

        pill_info.append((color, shape))

    count = Counter(pill_info)
    result_lines = [f"{color}{shape}：{cnt} 顆" for (color, shape), cnt in count.items()]
    return "\n".join(result_lines) if result_lines else "未偵測到藥物"


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_text = event.message.text

    # 模擬呼叫外部API
    #response = requests.post("https://httpbin.org/post", json={"text": user_text})
    #reply_text = f"你說的是：{user_text}"

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=f"你說的是:{user_text}")
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)