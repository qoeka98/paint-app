import tensorflow as tf
import numpy as np
import cv2
import time
import pandas as pd
import os
import streamlit as st
from PIL import Image

def run_game():
    # ✅ Teachable Machine 모델 로드
    model_path = "model/keras_model.h5"
    if not os.path.exists(model_path):
        st.error(f"❌ 모델 파일이 존재하지 않습니다: {model_path}")
        return
    model = tf.keras.models.load_model(model_path)

    # ✅ 클래스 매핑
    class_names = ["가위", "바위", "보"]

    # ✅ 승리 기록 저장 파일
    csv_file = "win_records.csv"
    if not os.path.exists(csv_file):
        pd.DataFrame(columns=["이름", "시간", "승리 횟수", "몬스터 MP"]).to_csv(csv_file, index=False)

    # ✅ 세션 변수 초기화
    if "monster_mp" not in st.session_state:
        st.session_state.monster_mp = 50
    if "initial_mp" not in st.session_state:
        st.session_state.initial_mp = st.session_state.monster_mp
    if "game_running" not in st.session_state:
        st.session_state.game_running = True

    st.subheader("🎮 가위바위보 몬스터 배틀 게임")
    st.info('📸 웹캠을 통해 손 모양을 인식하세요!')

    # ✅ 웹캠 선택 (0: 기본 웹캠, 1: USB 웹캠)
    webcam_index = st.radio("📷 사용할 웹캠 선택", [0, 1], format_func=lambda x: f"웹캠 {x}")

    # ✅ USB 웹캠 활성화
    cap = cv2.VideoCapture(webcam_index)
    if not cap.isOpened():
        st.error("❌ 웹캠을 찾을 수 없습니다. USB 웹캠이 올바르게 연결되었는지 확인하세요.")
        return

    # ✅ Streamlit UI
    image_placeholder = st.empty()
    countdown_placeholder = st.empty()
    result_placeholder = st.empty()
    mp_placeholder = st.empty()
    game_progress_placeholder = st.empty()
    timer_placeholder = st.empty()

    # ✅ 초기 빈 이미지 설정
    start_time = time.time()
    win_count = 0

    while st.session_state.monster_mp > 0:
        elapsed_time = round(time.time() - start_time, 2)
        minutes, seconds = divmod(int(elapsed_time), 60)
        timer_placeholder.write(f"⏳ **경과 시간: {minutes:02}:{seconds:02}**")

        countdown_time = 3  # 3초 후 자동 촬영
        capture_time = time.time() + countdown_time

        # ✅ 3초 후 자동 촬영
        while time.time() < capture_time:
            ret, frame = cap.read()
            if not ret:
                st.error("❌ 웹캠을 찾을 수 없습니다.")
                return

            # ✅ 초록색 네모 박스 추가
            h, w, _ = frame.shape
            box_size = min(h, w) // 2
            x1, y1 = (w - box_size) // 2, (h - box_size) // 2
            x2, y2 = x1 + box_size, y1 + box_size
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

            image_placeholder.image(frame, channels="BGR", use_container_width=True)
            remaining_time = int(capture_time - time.time())
            countdown_placeholder.write(f"📸 **{remaining_time}초 후 촬영!**")

        countdown_placeholder.write("📸 **찰칵!**")

        # ✅ 촬영 후 이미지 처리
        ret, frame = cap.read()
        if not ret:
            st.error("❌ 웹캠을 찾을 수 없습니다.")
            return

        roi = frame[y1:y2, x1:x2]
        img = cv2.cvtColor(roi, cv2.COLOR_BGR2RGB)
        img = cv2.resize(img, (224, 224))
        img = np.array(img, dtype=np.float32) / 255.0
        img = np.expand_dims(img, axis=0)

        # ✅ AI 모델 예측
        prediction = model.predict(img)
        class_index = np.argmax(prediction)
        confidence = np.max(prediction)

        if confidence < 0.7:
            result_placeholder.write("⚠️ 손을 네모 안에 정확하게 올려주세요!")
            continue

        user_choice = class_names[class_index]
        monster_choice = np.random.choice(["가위", "바위", "보"])

        # ✅ 승패 판정
        game_result = "⚖️ 비김"
        if (user_choice == "가위" and monster_choice == "보") or \
           (user_choice == "바위" and monster_choice == "가위") or \
           (user_choice == "보" and monster_choice == "바위"):
            game_result = "✅ 승리"
            st.session_state.monster_mp -= 10
        elif user_choice != monster_choice:
            game_result = "❌ 패배"

        # ✅ 결과 출력
        result_placeholder.markdown(f"""
        <h3 style='text-align: center;'>🖐 내 선택: {user_choice}  VS  👾 몬스터 선택: {monster_choice}</h3>
        <h2 style='text-align: center; color: black;'>결과 ➡️ <strong>{game_result}</strong></h2>
        """, unsafe_allow_html=True)

        # ✅ MP 업데이트
        game_progress_placeholder.write(f"🔹 진행 상황: 몬스터 MP {st.session_state.monster_mp} 남음")
        mp_placeholder.progress(max(st.session_state.monster_mp / st.session_state.initial_mp, 0))

        # ✅ 몬스터 MP가 0이면 게임 종료
        if st.session_state.monster_mp <= 0:
            st.success("🎉 몬스터를 물리쳤습니다! 게임 종료!")
            break

        time.sleep(1)

    cap.release()  # ✅ 웹캠 해제
