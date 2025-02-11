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
    model_path = "model/keras_model.h5"
    if not os.path.exists(model_path):
        st.error(f"❌ 모델 파일이 존재하지 않습니다: {model_path}")
    else:
        model = tf.keras.models.load_model(model_path)

    class_names = ["가위", "바위", "보"]

    if "monster_mp" not in st.session_state:
        st.session_state.monster_mp = 50  
    if "initial_mp" not in st.session_state:
        st.session_state.initial_mp = st.session_state.monster_mp
    if "game_running" not in st.session_state:
        st.session_state.game_running = True
    if "ranking_updated" not in st.session_state:
        st.session_state.ranking_updated = False

    st.subheader("🎮 가위바위보 몬스터 배틀 게임")
    st.info('📸 웹캠을 켜고 초록색 네모 안에 손을 위치시키세요!')

    class VideoTransformer(VideoTransformerBase):
        def __init__(self):
            self.last_captured_time = time.time()
            self.capture_interval = 3
            self.frame_to_analyze = None

        def transform(self, frame):
            img = frame.to_ndarray(format="bgr24")
            h, w, _ = img.shape

            box_size = min(h, w) // 2
            x1, y1 = (w - box_size) // 2, (h - box_size) // 2
            x2, y2 = x1 + box_size, y1 + box_size
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)

            if time.time() - self.last_captured_time > self.capture_interval:
                self.frame_to_analyze = img[y1:y2, x1:x2]
                self.last_captured_time = time.time()

            return av.VideoFrame.from_ndarray(img, format="bgr24")

    webrtc_ctx = webrtc_streamer(
        key="game",
        video_transformer_factory=VideoTransformer,
        async_transform=True
    )

    if webrtc_ctx.video_transformer and webrtc_ctx.video_transformer.frame_to_analyze is not None:
        captured_img = webrtc_ctx.video_transformer.frame_to_analyze
        img = cv2.cvtColor(captured_img, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(img)
        img = img.resize((224, 224))
        img_array = np.array(img, dtype=np.float32) / 255.0
        img_array = np.expand_dims(img_array, axis=0)

        prediction = model.predict(img_array)
        class_index = np.argmax(prediction)
        confidence = np.max(prediction)

        if confidence >= 0.7:
            user_choice = class_names[class_index]
            monster_choice = np.random.choice(["가위", "바위", "보"])
            st.subheader(f"🖐 내 선택: {user_choice}  VS  👾 몬스터 선택: {monster_choice}")
