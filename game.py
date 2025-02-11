import tensorflow as tf
import numpy as np
import cv2
import time
import pandas as pd
import os
import gradio as gr
from PIL import Image

# TensorFlow 경고 메시지 비활성화
tf.get_logger().setLevel("ERROR")

# 모델 로드 (경고 메시지 해결)
model_path = "model/keras_model.h5"

try:
    model = tf.keras.models.load_model(model_path, compile=False)  # 🔹 compile=False 설정
    model.compile(optimizer=tf.keras.optimizers.Adam(), loss="categorical_crossentropy", metrics=["accuracy"])  # 🔹 수동 컴파일
except Exception as e:
    print(f"🚨 모델 로딩 오류: {e}")
    exit()

# 클래스 매핑
class_names = ["가위", "바위", "보"]

# 몬스터 초기 HP 설정
INITIAL_MONSTER_MP = 50

def process_game(image, monster_mp):
    """
    이미지를 받아 가위바위보 판정을 하고, 몬스터 MP를 감소시키는 함수
    """
    if image is None:
        return "❌ 이미지를 업로드하거나 웹캠을 사용하세요!", "image/가위바위보 홈.png", monster_mp, f"몬스터 HP: {monster_mp}"

    # 이미지 전처리
    img = image.convert("RGB")
    img = img.resize((224, 224))
    img = np.array(img, dtype=np.float32) / 255.0
    img = np.expand_dims(img, axis=0)

    # 모델 예측
    prediction = model.predict(img)
    class_index = np.argmax(prediction)
    confidence = np.max(prediction)

    if confidence < 0.7:
        return "⚠️ 손을 정확히 올려주세요!", "image/가위바위보 홈.png", monster_mp, f"몬스터 HP: {monster_mp}"

    user_choice = class_names[class_index]
    monster_choice = np.random.choice(["가위", "바위", "보"])

    # 승패 판정
    game_result = "⚖️ 비김"
    result_image = "image/비김.png"

    if (user_choice == "가위" and monster_choice == "보") or \
       (user_choice == "바위" and monster_choice == "가위") or \
       (user_choice == "보" and monster_choice == "바위"):
        game_result = "✅ 승리"
        result_image = "image/이겼다.png"
        monster_mp -= 10  # 몬스터 MP 감소
    elif user_choice != monster_choice:
        game_result = "❌ 패배"
        result_image = "image/졌다.png"

    # 게임 종료 조건
    if monster_mp <= 0:
        return "🎉 몬스터를 물리쳤습니다!", "image/승리.png", 0, f"몬스터 HP: 0 (게임 종료)"

    return f"🖐 내 선택: {user_choice}  VS  👾 몬스터 선택: {monster_choice} ➡️ {game_result}", \
           result_image, monster_mp, f"몬스터 HP: {monster_mp}"

def reset_game():
    """
    게임 초기화 함수
    """
    return f"몬스터 HP: {INITIAL_MONSTER_MP}", "image/가위바위보 홈.png", INITIAL_MONSTER_MP, ""

# Gradio 인터페이스
with gr.Blocks() as demo:
    gr.Markdown("## 🎮 가위바위보 게임 (AI vs Player)")
    gr.Markdown("웹캠이나 사진을 업로드하여 가위바위보를 플레이하세요!")

    with gr.Row():
        image_input = gr.Image(image_mode="webcam", type="pil", interactive=True, label="📸 웹캠을 사용하세요!")


        result_image = gr.Image(value="image/가위바위보 홈.png", label="🎯 게임 결과", interactive=False)

    result_text = gr.Textbox(label="📢 결과", interactive=False)
    monster_hp_text = gr.Textbox(value=f"몬스터 HP: {INITIAL_MONSTER_MP}", interactive=False)

    with gr.Row():
        play_button = gr.Button("📸 촬영 및 판정")
        reset_button = gr.Button("🔄 게임 재시작")

    play_button.click(process_game, inputs=[image_input, monster_hp_text], outputs=[result_text, result_image, monster_hp_text, monster_hp_text])
    reset_button.click(reset_game, outputs=[result_text, result_image, monster_hp_text, monster_hp_text])

# 실행
demo.launch(debug=True) 
