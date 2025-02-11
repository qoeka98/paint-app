import tensorflow as tf
import numpy as np
import pandas as pd
import os
import streamlit as st
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase
import av
import cv2
import time
from PIL import Image

# 모델 로드
model_path = "model/keras_model.h5"
if not os.path.exists(model_path):
    st.error(f"❌ 모델 파일이 존재하지 않습니다: {model_path}")
else:
    model = tf.keras.models.load_model(model_path)

# 클래스 매핑
class_names = ["가위", "바위", "보"]

# CSV 파일 존재 여부 확인
csv_file = "win_records.csv"
if not os.path.exists(csv_file) or os.stat(csv_file).st_size == 0:
    pd.DataFrame(columns=["이름", "시간", "승리 횟수", "몬스터 MP"]).to_csv(csv_file, index=False)

# **세션 변수 초기화**
if "monster_mp" not in st.session_state:
    st.session_state.monster_mp = 50  # 기본값 설정
if "initial_mp" not in st.session_state:
    st.session_state.initial_mp = st.session_state.monster_mp
if "game_running" not in st.session_state:
    st.session_state.game_running = True
if "ranking_updated" not in st.session_state:
    st.session_state.ranking_updated = False

# UI 구성
st.subheader("🎮 가위바위보 몬스터 배틀 게임")
st.info('📸 웹캠을 켜고 초록색 네모 안에 손을 위치시키세요!')

col1, col2 = st.columns(2)
with col1:
    if st.button("🔄 게임 재시작"):
        st.session_state.game_running = True
        st.session_state.monster_mp = st.session_state.initial_mp  # MP 초기화
        st.rerun()
with col2:
    if st.button("🛑 게임 종료"):
        st.session_state.game_running = False
        st.session_state.game_message = "게임이 강제 종료되었습니다!"
        st.stop()


# 🎥 **WebRTC 기반 실시간 웹캠 스트리밍**
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

# **3초마다 캡처된 프레임을 분석**
if webrtc_ctx.video_transformer and webrtc_ctx.video_transformer.frame_to_analyze is not None:
    captured_img = webrtc_ctx.video_transformer.frame_to_analyze

    # **이미지 전처리**
    img = cv2.cvtColor(captured_img, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(img)
    img = img.resize((224, 224))
    img_array = np.array(img, dtype=np.float32) / 255.0
    img_array = np.expand_dims(img_array, axis=0)

    # 🤖 **모델 예측**
    prediction = model.predict(img_array)
    class_index = np.argmax(prediction)
    confidence = np.max(prediction)

    if confidence >= 0.7:
        user_choice = class_names[class_index]
        monster_choice = np.random.choice(["가위", "바위", "보"])

        monster_mp = st.session_state.monster_mp
        game_result = "⚖️ 비김"
        result_image = "image/비김.png"

        if (user_choice == "가위" and monster_choice == "보") or \
           (user_choice == "바위" and monster_choice == "가위") or \
           (user_choice == "보" and monster_choice == "바위"):
            game_result = "✅ 승리"
            result_image = "image/이겼다.png"
            monster_mp -= 10  # 🔥 **승리 시 몬스터 MP 10 감소**
        elif user_choice != monster_choice:
            game_result = "❌ 패배"
            result_image = "image/졌다.png"

        # **MP가 0 이하가 되지 않도록 방지**
        monster_mp = max(monster_mp, 0)
        st.session_state.monster_mp = monster_mp

        # **결과 출력**
        st.subheader(f"🖐 내 선택: {user_choice}  VS  👾 몬스터 선택: {monster_choice}")
        st.image(result_image, use_container_width=True)
        st.markdown(f"### 결과 ➡️ **{game_result}**")

        # **MP 진행률 바 업데이트**
        progress_value = max(monster_mp / st.session_state.initial_mp, 0)  # 0 이하 방지
        st.progress(progress_value)

        # **게임 종료 체크**
        if monster_mp <= 0:
            st.success("🎉 몬스터를 물리쳤습니다!")
            st.session_state.game_running = False

            # 🏆 승리 기록 업데이트
            win_df = pd.read_csv(csv_file)
            new_record = pd.DataFrame({
                "이름": [st.session_state.get("user_name", "Player")],
                "시간": [st.session_state.initial_mp - monster_mp],
                "승리 횟수": [1],
                "몬스터 MP": [st.session_state.initial_mp]
            })
            win_df = pd.concat([win_df, new_record], ignore_index=True)
            win_df.to_csv(csv_file, index=False)

            # 🏆 랭킹 표시
            st.subheader(f"🏆 몬스터 MP {st.session_state.initial_mp} 랭킹")
            ranking_df = win_df[win_df["몬스터 MP"] == st.session_state.initial_mp].sort_values(by="시간").head(5)
            st.table(ranking_df.set_index("이름"))
