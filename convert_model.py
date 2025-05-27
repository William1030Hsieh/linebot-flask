import os
os.environ['TF_CPP_MIN_LOG_LEVEL']='2'

import tensorflow as tf

# 讀取你訓練好的 .h5 模型
model = tf.keras.models.load_model("pill_classifier_model.h5")

# 轉換成 TFLite 模型
converter = tf.lite.TFLiteConverter.from_keras_model(model)
tflite_model = converter.convert()

# 儲存為 .tflite
with open("pill_classifier_model.tflite", "wb") as f:
    f.write(tflite_model)

print("轉換完成！已建立 pill_classifier_model.tflite")