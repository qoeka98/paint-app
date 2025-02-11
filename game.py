import tensorflow as tf
import numpy as np
import time
import pandas as pd
import os
import streamlit as st
from PIL import Image
import cv2
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase

def run_game():
    # 모델 로드
    model_path = "model/keras_model.h5"
    model = tf.keras.models.load_model(model_path)

    # 클래스 매핑
    class_names = ["가위", "바위", "보"]

    # 승리 기록 저장 파일
    csv_file = "win_records.csv"
    if not os.path.exists(csv_file):
        pd.DataFrame(columns=["이름", "시간", "승리 횟수", "몬스터 MP"]).to_csv(csv_file, index=False)

    # 게임 UI
    st.title("🎮 가위바위보 몬스터 배틀")
    st.subheader("📷 웹캠을 활성화하고 손을 네모 안에 맞춰 가위, 바위, 보를 선택하세요!")

    # **게임 재시작 & 종료 버튼**
    col_button1, col_button2 = st.columns(2)
    with col_button1:
        if st.button("🔄 게임 재시작"):
            st.session_state.monster_mp = 50
            st.rerun()
    with col_button2:
        if st.button("🛑 게임 종료"):
            st.stop()

    # Streamlit WebRTC를 활용한 웹캠 스트리밍
    class VideoTransformer(VideoTransformerBase):
        def transform(self, frame):
            img = frame.to_ndarray(format="bgr24")
            h, w, _ = img.shape
            box_size = min(h, w) // 2
            x1, y1 = (w - box_size) // 2, (h - box_size) // 2
            x2, y2 = x1 + box_size, y1 + box_size

            # 네모 박스 그리기
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
            return img

    webrtc_ctx = webrtc_streamer(
        key="game_stream",
        video_transformer_factory=VideoTransformer,
        async_transform=True,
        rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}
    )

    # 결과 표시 영역
    result_placeholder = st.empty()

    if webrtc_ctx.video_receiver and webrtc_ctx.video_receiver.last_frame is not None:
        st.write("📸 웹캠이 활성화되었습니다!")

        frame = webrtc_ctx.video_receiver.last_frame.to_ndarray(format="bgr24")
        h, w, _ = frame.shape
        box_size = min(h, w) // 2
        x1, y1 = (w - box_size) // 2, (h - box_size) // 2
        x2, y2 = x1 + box_size, y1 + box_size

        roi = frame[y1:y2, x1:x2]
        img = cv2.cvtColor(roi, cv2.COLOR_BGR2RGB)
        img = cv2.resize(img, (224, 224))
        img = img / 255.0
        img = np.expand_dims(img, axis=0)

        prediction = model.predict(img)
        class_index = np.argmax(prediction)
        confidence = np.max(prediction)

        if confidence < 0.7:
            st.warning("⚠️ 손을 네모 안에 정확히 올려주세요!")
        else:
            user_choice = class_names[class_index]
            monster_choice = np.random.choice(["가위", "바위", "보"])
            game_result = "⚖️ 비김"
            result_image = "image/비김.png"

            if (user_choice == "가위" and monster_choice == "보") or \
               (user_choice == "바위" and monster_choice == "가위") or \
               (user_choice == "보" and monster_choice == "바위"):
                game_result = "✅ 승리"
                result_image = "image/이겼다.png"
            elif user_choice != monster_choice:
                game_result = "❌ 패배"
                result_image = "image/졌다.png"

            result_placeholder.image(result_image, use_column_width=True)
            st.write(f"🖐 내 선택: {user_choice}  VS  👾 몬스터 선택: {monster_choice}")
            st.write(f"결과: {game_result}")
