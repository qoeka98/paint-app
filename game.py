import tensorflow as tf
import numpy as np
import cv2
import time
import pandas as pd
import os
import streamlit as st
from PIL import Image
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase
import av

# ✅ Teachable Machine 모델 로드
model_path = "model/keras_model.h5"
if not os.path.exists(model_path):
    st.error(f"❌ 모델 파일이 존재하지 않습니다: {model_path}")
else:
    model = tf.keras.models.load_model(model_path)

# ✅ 클래스 매핑
class_names = ["가위", "바위", "보"]

# ✅ CSV 파일 존재 여부 확인
csv_file = "win_records.csv"
if not os.path.exists(csv_file) or os.stat(csv_file).st_size == 0:
    pd.DataFrame(columns=["이름", "시간", "승리 횟수", "몬스터 MP"]).to_csv(csv_file, index=False)

# ✅ 세션 변수 초기화
if "monster_mp" not in st.session_state:
    st.session_state.monster_mp = 50  # 기본값 설정
if "initial_mp" not in st.session_state:
    st.session_state.initial_mp = st.session_state.monster_mp

# ✅ Streamlit UI
st.subheader("🎮 게임을 시작합니다!")
st.info('📸 초록색 네모 박스 안에 손을 위치시켜주세요.')

# ✅ WebRTC를 사용한 실시간 웹캠
class VideoTransformer(VideoTransformerBase):
    def __init__(self):
        self.last_captured_time = time.time()
        self.capture_interval = 3  # 3초마다 캡처
        self.frame_to_analyze = None

    def transform(self, frame):
        img = frame.to_ndarray(format="bgr24")
        h, w, _ = img.shape

        # 초록 네모 박스 설정
        box_size = min(h, w) // 2
        x1, y1 = (w - box_size) // 2, (h - box_size) // 2
        x2, y2 = x1 + box_size, y1 + box_size
        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)  # 초록 네모

        # 3초마다 이미지 캡처
        if time.time() - self.last_captured_time > self.capture_interval:
            self.frame_to_analyze = img[y1:y2, x1:x2]  # 박스 안의 부분만 저장
            self.last_captured_time = time.time()

        return av.VideoFrame.from_ndarray(img, format="bgr24")

webrtc_ctx = webrtc_streamer(
    key="game",
    video_transformer_factory=VideoTransformer,
    async_transform=True
)

# ✅ 3초마다 캡처된 프레임을 분석
if webrtc_ctx.video_transformer and webrtc_ctx.video_transformer.frame_to_analyze is not None:
    captured_img = webrtc_ctx.video_transformer.frame_to_analyze
    img = cv2.cvtColor(captured_img, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(img).resize((224, 224))
    img_array = np.array(img, dtype=np.float32) / 255.0
    img_array = np.expand_dims(img_array, axis=0)

    # 🤖 모델 예측
    prediction = model.predict(img_array)
    class_index = np.argmax(prediction)
    confidence = np.max(prediction)

    if confidence >= 0.7:
        user_choice = class_names[class_index]
        monster_choice = np.random.choice(["가위", "바위", "보"])

        game_result = "✅ 승리" if (user_choice, monster_choice) in [("가위", "보"), ("바위", "가위"), ("보", "바위")] else "❌ 패배"
        st.subheader(f"🖐 내 선택: {user_choice}  VS  👾 몬스터 선택: {monster_choice}")
        st.markdown(f"### 결과 ➡️ **{game_result}**")

