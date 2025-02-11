import gradio as gr
import tensorflow as tf
import numpy as np
import pandas as pd
import cv2
import time
import os
from PIL import Image

# ✅ TensorFlow 경고 메시지 숨기기
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"

# ✅ 모델 로드 (Teachable Machine에서 훈련된 모델)
model_path = "keras_model.h5"  
if not os.path.exists(model_path):
    raise FileNotFoundError(f"🚨 모델 파일이 없습니다: {model_path}")

model = tf.keras.models.load_model(model_path, compile=False)
model.compile(optimizer=tf.keras.optimizers.Adam(), loss="categorical_crossentropy", metrics=["accuracy"])

# ✅ 가위, 바위, 보 클래스 매핑
class_names = ["가위", "바위", "보"]

# ✅ 랭킹 저장용 CSV 파일
rank_file = "ranking.csv"
if not os.path.exists(rank_file):
    pd.DataFrame(columns=["이름", "시간", "승리 횟수"]).to_csv(rank_file, index=False)

# ✅ 전역 변수 (타이머 초기화)
last_capture_time = time.time()

def process_game(image, username, start_time):
    """실시간 웹캠 자동 캡처 후 AI 모델로 판별"""
    global last_capture_time
    
    # ✅ 일정 간격(3초)마다 자동 캡처
    if time.time() - last_capture_time < 3:
        return "⏳ 자동 캡처 중...", None

    last_capture_time = time.time()  # 캡처 시간 업데이트

    if image is None:
        return "❌ 웹캠을 인식할 수 없습니다!", None

    # ✅ 이미지 전처리 (224x224로 변환 후 정규화)
    image = Image.fromarray(image)
    image = image.resize((224, 224))
    image = np.array(image, dtype=np.float32) / 255.0
    image = np.expand_dims(image, axis=0)

    # ✅ 모델 예측 수행
    prediction = model.predict(image)
    class_index = np.argmax(prediction)
    confidence = np.max(prediction)

    if confidence < 0.7:
        return "⚠️ 손을 정확히 네모 박스 안에 넣어주세요!", None

    # ✅ AI vs 몬스터 가위바위보
    user_choice = class_names[class_index]
    monster_choice = np.random.choice(["가위", "바위", "보"])
    result = "⚖️ 비김"
    result_image_path = "./image/비김.png"

    if (user_choice == "가위" and monster_choice == "보") or \
       (user_choice == "바위" and monster_choice == "가위") or \
       (user_choice == "보" and monster_choice == "바위"):
        result = "✅ 승리"
        result_image_path = "./image/이겼다.png"
    elif user_choice != monster_choice:
        result = "❌ 패배"
        result_image_path = "./image/졌다.png"

    return f"🖐 내 선택: {user_choice}  VS  👾 몬스터 선택: {monster_choice} ➡️ {result}", Image.open(result_image_path)

def run_game():
    """Gradio UI 설정"""
    with gr.Blocks() as game_ui:
        gr.Markdown("## 🎮 실시간 웹캠 자동 캡처 가위바위보 게임")
        gr.Markdown("웹캠에서 자동으로 손을 인식하고 3초마다 가위, 바위, 보를 판별합니다!")

        with gr.Row():
            webcam_feed = gr.Image(type="numpy", label="📸 웹캠 실시간 스트리밍", streaming=True)
            result_image = gr.Image(label="🎯 게임 결과", interactive=False)

        result_text = gr.Textbox(label="📢 결과", interactive=False)
        username = gr.Textbox(label="📝 닉네임 입력", value="Player")
        start_time = gr.Textbox(value=str(time.time()), visible=False)

        # ✅ 웹캠이 실시간으로 업데이트될 때마다 자동 캡처 실행
        webcam_feed.change(process_game, inputs=[webcam_feed, username, start_time], outputs=[result_text, result_image])

    return game_ui

# ✅ 실행
if __name__ == "__main__":
    run_game().launch(debug=True)
