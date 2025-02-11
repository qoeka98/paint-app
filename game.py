import streamlit as st
import tensorflow as tf
import numpy as np
import os
import cv2
import time
from PIL import Image
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase
import av

# ✅ 모델 로드
model_path = "model/keras_model.h5"
if not os.path.exists(model_path):
    st.error(f"❌ 모델 파일이 존재하지 않습니다: {model_path}")
    st.stop()

model = tf.keras.models.load_model(model_path)
class_names = ["가위", "바위", "보"]

# ✅ 카메라 선택 기능 추가 (USB 웹캠 지원)
st.sidebar.title("📷 카메라 설정")
camera_option = st.sidebar.radio("카메라 선택", ["🔗 내장 웹캠 (WebRTC)", "🔌 USB 웹캠 (OpenCV)"])

# ✅ 세션 변수 초기화
if "monster_mp" not in st.session_state:
    st.session_state.monster_mp = 50  
if "initial_mp" not in st.session_state:
    st.session_state.initial_mp = st.session_state.monster_mp
if "game_running" not in st.session_state:
    st.session_state.game_running = True

st.subheader("🎮 가위바위보 몬스터 배틀 게임")
st.info("📸 웹캠을 켜고 초록색 네모 안에 손을 위치시키세요!")

# ✅ 1. 🔗 **WebRTC 기반 스트리밍 (기본 웹캠 사용)**
if camera_option == "🔗 내장 웹캠 (WebRTC)":
    class VideoTransformer(VideoTransformerBase):
        def __init__(self):
            self.last_captured_time = time.time()
            self.capture_interval = 3  # 3초마다 캡처
            self.frame_to_analyze = None

        def transform(self, frame):
            img = frame.to_ndarray(format="bgr24")
            h, w, _ = img.shape

            # ✅ 네모 박스 설정 (화면 중앙)
            box_size = min(h, w) // 2
            x1, y1 = (w - box_size) // 2, (h - box_size) // 2
            x2, y2 = x1 + box_size, y1 + box_size
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)  # 초록 네모

            # ✅ 3초마다 이미지 캡처
            if time.time() - self.last_captured_time > self.capture_interval:
                self.frame_to_analyze = img[y1:y2, x1:x2]  # 네모 박스 내부만 저장
                self.last_captured_time = time.time()

            return av.VideoFrame.from_ndarray(img, format="bgr24")

    webrtc_ctx = webrtc_streamer(
        key="game",
        video_transformer_factory=VideoTransformer,
        async_transform=True
    )

    # ✅ WebRTC에서 3초마다 캡처된 프레임을 사용하여 예측
    if webrtc_ctx.video_transformer and webrtc_ctx.video_transformer.frame_to_analyze is not None:
        captured_img = webrtc_ctx.video_transformer.frame_to_analyze

        # ✅ 이미지 전처리
        img = cv2.cvtColor(captured_img, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(img)
        img = img.resize((224, 224))
        img_array = np.array(img, dtype=np.float32) / 255.0
        img_array = np.expand_dims(img_array, axis=0)

# ✅ 2. 🔌 **OpenCV를 이용한 USB 웹캠 연결**
elif camera_option == "🔌 USB 웹캠 (OpenCV)":
    usb_camera_index = st.sidebar.number_input("📷 USB 웹캠 인덱스 설정 (기본값: 0)", min_value=0, step=1, value=0)

    cap = cv2.VideoCapture(usb_camera_index)  # USB 웹캠 연결

    if not cap.isOpened():
        st.error("❌ USB 웹캠을 찾을 수 없습니다. 올바른 인덱스를 입력하세요!")
        st.stop()

    stframe = st.empty()

    # ✅ 실시간 웹캠 표시 & 네모 박스
    while True:
        ret, frame = cap.read()
        if not ret:
            st.error("❌ USB 웹캠에서 영상을 가져올 수 없습니다.")
            break

        # ✅ 네모 박스 추가
        h, w, _ = frame.shape
        box_size = min(h, w) // 2
        x1, y1 = (w - box_size) // 2, (h - box_size) // 2
        x2, y2 = x1 + box_size, y1 + box_size
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

        stframe.image(frame, channels="BGR")

        # ✅ 3초 후 촬영
        time.sleep(3)
        roi = frame[y1:y2, x1:x2]

        # ✅ 이미지 전처리
        img = cv2.cvtColor(roi, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(img)
        img = img.resize((224, 224))
        img_array = np.array(img, dtype=np.float32) / 255.0
        img_array = np.expand_dims(img_array, axis=0)

        break  # 3초 후 1회만 실행

    cap.release()

# ✅ 3. 🤖 **AI 모델 예측**
prediction = model.predict(img_array)
class_index = np.argmax(prediction)
confidence = np.max(prediction)

if confidence >= 0.7:
    user_choice = class_names[class_index]
    monster_choice = np.random.choice(["가위", "바위", "보"])

    game_result = "⚖️ 비김"
    if (user_choice == "가위" and monster_choice == "보") or \
       (user_choice == "바위" and monster_choice == "가위") or \
       (user_choice == "보" and monster_choice == "바위"):
        game_result = "✅ 승리"
        st.session_state.monster_mp -= 10  
    elif user_choice != monster_choice:
        game_result = "❌ 패배"

    # ✅ 결과 출력
    st.subheader(f"🖐 내 선택: {user_choice}  VS  👾 몬스터 선택: {monster_choice}")
    st.markdown(f"### 결과 ➡️ **{game_result}**")

    # ✅ MP 진행률 바 업데이트
    progress_value = max(st.session_state.monster_mp / st.session_state.initial_mp, 0)
    st.progress(progress_value)

    # ✅ 몬스터 MP가 0이면 게임 종료
    if st.session_state.monster_mp <= 0:
        st.success("🎉 몬스터를 물리쳤습니다! 게임 종료!")
        st.session_state.game_running = False
