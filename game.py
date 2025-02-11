import streamlit as st
import tensorflow as tf
import numpy as np
import os
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase
import av
import cv2
import time
from PIL import Image

def run_game():
    # ✅ 모델 로드 (경로 확인)
    model_path = "model/keras_model.h5"
    if not os.path.exists(model_path):
        st.error(f"❌ 모델 파일이 존재하지 않습니다: {model_path}")
        return
    model = tf.keras.models.load_model(model_path)

    # ✅ 가위바위보 클래스 정의
    class_names = ["가위", "바위", "보"]

    # ✅ 세션 변수 초기화
    if "monster_mp" not in st.session_state:
        st.session_state.monster_mp = 50  
    if "initial_mp" not in st.session_state:
        st.session_state.initial_mp = st.session_state.monster_mp
    if "game_running" not in st.session_state:
        st.session_state.game_running = True
    if "ranking_updated" not in st.session_state:
        st.session_state.ranking_updated = False

    # ✅ 게임 UI 구성
    st.subheader("🎮 가위바위보 몬스터 배틀 게임")
    st.info("📸 웹캠을 켜고 초록색 네모 안에 손을 위치시키세요!")

    # ✅ WebRTC 기반 실시간 웹캠
    class VideoTransformer(VideoTransformerBase):
        def __init__(self):
            self.last_captured_time = time.time()
            self.capture_interval = 3  # ⏳ 3초마다 캡처
            self.frame_to_analyze = None

        def transform(self, frame):
            img = frame.to_ndarray(format="bgr24")
            h, w, _ = img.shape

            # 초록색 네모 박스 그리기
            box_size = min(h, w) // 2
            x1, y1 = (w - box_size) // 2, (h - box_size) // 2
            x2, y2 = x1 + box_size, y1 + box_size
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)

            # 3초마다 이미지 캡처
            if time.time() - self.last_captured_time > self.capture_interval:
                self.frame_to_analyze = img[y1:y2, x1:x2]
                self.last_captured_time = time.time()

            return av.VideoFrame.from_ndarray(img, format="bgr24")

    # ✅ WebRTC 스트리밍 설정
    webrtc_ctx = webrtc_streamer(
        key="game",
        video_transformer_factory=VideoTransformer,
        async_transform=True,
        rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},  # 🔹 STUN 서버 추가
    )

    # ✅ 캡처된 프레임을 분석하여 가위바위보 판정
    if webrtc_ctx.video_transformer and webrtc_ctx.video_transformer.frame_to_analyze is not None:
        captured_img = webrtc_ctx.video_transformer.frame_to_analyze
        img = cv2.cvtColor(captured_img, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(img)
        img = img.resize((224, 224))
        img_array = np.array(img, dtype=np.float32) / 255.0
        img_array = np.expand_dims(img_array, axis=0)

        # ✅ 모델 예측
        prediction = model.predict(img_array)
        class_index = np.argmax(prediction)
        confidence = np.max(prediction)

        if confidence >= 0.7:
            user_choice = class_names[class_index]
            monster_choice = np.random.choice(["가위", "바위", "보"])

            # ✅ 승패 판정 로직
            if (user_choice == "가위" and monster_choice == "보") or \
               (user_choice == "바위" and monster_choice == "가위") or \
               (user_choice == "보" and monster_choice == "바위"):
                game_result = "✅ 승리"
                st.session_state.monster_mp -= 10  # 🔥 승리 시 몬스터 MP 10 감소
            elif user_choice == monster_choice:
                game_result = "⚖️ 비김"
            else:
                game_result = "❌ 패배"

            # ✅ 게임 결과 출력
            st.subheader(f"🖐 내 선택: {user_choice}  VS  👾 몬스터 선택: {monster_choice}")
            st.markdown(f"### 결과 ➡️ **{game_result}**")

            # ✅ 몬스터 MP 상태 업데이트
            st.session_state.monster_mp = max(st.session_state.monster_mp, 0)
            progress_value = max(st.session_state.monster_mp / st.session_state.initial_mp, 0)
            st.progress(progress_value)

            # ✅ 게임 종료 확인
            if st.session_state.monster_mp <= 0:
                st.success("🎉 몬스터를 물리쳤습니다!")
                st.session_state.game_running = False
