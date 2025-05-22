from flask import Flask, request, abort
import requests
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from linebot.models import ImageMessage
import os

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
    result_text = detect_pills(image_path)

    # 回傳結果給使用者
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=result_text)
    )

def detect_pills(image_path):
    # 這是示意函式，實際請連接你的模型處理邏輯
    return "藍色膠囊 2 顆，白色錠劑 3 顆"


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