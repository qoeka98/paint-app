import streamlit as st
from PIL import Image
import numpy as np
import tensorflow as tf

# 모델 로드
model_path = "model/keras_model.h5"
model = tf.keras.models.load_model(model_path)
class_names = ["가위", "바위", "보"]

st.title("🎮 가위바위보 인식 게임")

# Streamlit 기본 카메라 입력 사용
image = st.camera_input("📸 손 모양을 촬영하세요!")

if image is not None:
    # PIL 이미지를 OpenCV 형식으로 변환
    img = Image.open(image)
    img = img.resize((224, 224))  # 모델 입력 크기로 조정
    img = np.array(img, dtype=np.float32) / 255.0
    img = np.expand_dims(img, axis=0)

    # 모델 예측
    prediction = model.predict(img)
    class_index = np.argmax(prediction)
    confidence = np.max(prediction)

    if confidence < 0.7:
        st.warning("⚠️ 손 모양을 정확히 인식하지 못했습니다. 다시 시도해주세요!")
    else:
        user_choice = class_names[class_index]
        st.success(f"🎉 인식된 손 모양: {user_choice}")
