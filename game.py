import tensorflow as tf
import numpy as np
import time
import pandas as pd
import os
import streamlit as st
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase
from PIL import Image
import cv2

# Teachable Machine 모델 로드
model_path = "model/keras_model.h5"
model = tf.keras.models.load_model(model_path)

# 클래스 매핑
class_names = ["가위", "바위", "보"]

# 승리 기록 저장 파일
csv_file = "win_records.csv"
if not os.path.exists(csv_file):
    pd.DataFrame(columns=["이름", "시간", "승리 횟수", "몬스터 MP"]).to_csv(csv_file, index=False)

# Streamlit 앱 UI
st.subheader("🎮 가위바위보 게임을 시작합니다!")
st.info('웹캠을 활성화하고 네모 안에 손을 정확히 올려주세요!')

# **게임 재시작 & 종료 버튼**
col_button1, col_button2 = st.columns(2)
with col_button1:
    if st.button("🔄 게임 재시작"):
        st.rerun()
with col_button2:
    if st.button("🛑 게임 종료"):
        st.stop()

# 몬스터 MP 설정
if "monster_mp" not in st.session_state:
    st.session_state.monster_mp = 50

monster_mp = st.session_state.monster_mp
start_time = time.time()
win_count = 0

# Streamlit WebRTC 비디오 스트림 설정
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

webrtc_ctx = webrtc_streamer(key="example", video_transformer_factory=VideoTransformer)

if webrtc_ctx.video_transformer:
    st.write("📸 웹캠이 활성화되었습니다!")

    if st.button("🔍 이미지 캡처 및 분석"):
        if webrtc_ctx.video_transformer:
            frame = webrtc_ctx.video_transformer.transform(webrtc_ctx.video_receiver.last_frame)
            roi = frame[y1:y2, x1:x2]
            img = cv2.cvtColor(roi, cv2.COLOR_BGR2RGB)
            img = cv2.resize(img, (224, 224))
            img = np.array(img, dtype=np.float32) / 255.0
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
                    monster_mp -= 10
                    win_count += 1
                elif user_choice != monster_choice:
                    game_result = "❌ 패배"
                    result_image = "image/졌다.png"
                    start_time += 3  # 패배 시 패널티 3초 추가

                # 결과 출력
                st.image(result_image, use_column_width=True)
                st.write(f"🖐 내 선택: {user_choice}  VS  👾 몬스터 선택: {monster_choice}")
                st.write(f"결과: {game_result}")
                st.write(f"🔹 몬스터 MP 남음: {monster_mp}")
                st.progress(monster_mp / 50)

                if monster_mp <= 0:
                    st.success("🎉 몬스터를 물리쳤습니다!")
                    st.image("image/승리.png", use_column_width=True)