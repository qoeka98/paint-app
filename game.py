import tensorflow as tf
import numpy as np
import cv2
import time
import pandas as pd
import os
import streamlit as st
from PIL import Image

def run_game():
    # 모델 경로 및 로드
    model_path = "model/keras_model.h5"
    if not os.path.exists(model_path):
        st.error(f"❌ 모델 파일이 존재하지 않습니다: {model_path}")
        return

    try:
        model = tf.keras.models.load_model(model_path)
    except Exception as e:
        st.error(f"⚠️ 모델 로드 중 오류 발생: {e}")
        return

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
    st.info('웹 카메라 속 초록 상자에 정확히 손 모양을 보여주세요.')

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 게임 재시작"):
            st.session_state.game_running = True
            st.rerun()
    with col2:
        if st.button("🛑 게임 종료"):
            st.session_state.game_running = False
            st.session_state.game_message = "게임이 강제 종료되었습니다!"
            st.stop()

    # 웹캠 활성화
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        st.error("❌ 웹캠을 찾을 수 없습니다. 카메라 권한을 확인해주세요.")
        return

    monster_mp = st.session_state.monster_mp
    image_placeholder = st.empty()
    result_placeholder = st.empty()
    game_progress_placeholder = st.empty()

    start_time = time.time()
    win_count = 0

    while monster_mp > 0 and st.session_state.game_running:
        elapsed_time = round(time.time() - start_time, 2)
        st.write(f"⏳ **경과 시간: {int(elapsed_time // 60)}:{int(elapsed_time % 60):02}**")

        countdown_time = 3
        capture_time = time.time() + countdown_time

        while time.time() < capture_time:
            ret, frame = cap.read()
            if not ret:
                st.error("❌ 웹캠을 찾을 수 없습니다.")
                return
            
            h, w, _ = frame.shape
            box_size = min(h, w) // 2
            x1, y1 = (w - box_size) // 2, (h - box_size) // 2
            x2, y2 = x1 + box_size, y1 + box_size

            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            image_placeholder.image(frame, channels="BGR", use_container_width=True)
            st.write(f"📸 **{int(capture_time - time.time())}초 뒤 촬영!**")

        ret, frame = cap.read()
        if not ret:
            st.error("❌ 웹캠을 찾을 수 없습니다.")
            return

        roi = frame[y1:y2, x1:x2]
        img = cv2.cvtColor(roi, cv2.COLOR_BGR2RGB)
        img = cv2.resize(img, (224, 224))
        img = np.array(img, dtype=np.float32) / 255.0
        img = np.expand_dims(img, axis=0)

        prediction = model.predict(img)
        class_index = np.argmax(prediction)
        confidence = np.max(prediction)

        if confidence < 0.7:
            result_placeholder.write("⚠️ 손을 네모 안에 정확하게 올려주세요!")
            continue

        user_choice = class_names[class_index]
        monster_choice = np.random.choice(["가위", "바위", "보"])

        if (user_choice == "가위" and monster_choice == "보") or \
           (user_choice == "바위" and monster_choice == "가위") or \
           (user_choice == "보" and monster_choice == "바위"):
            game_result = "✅ 승리"
            monster_mp -= 10
            win_count += 1
        elif user_choice == monster_choice:
            game_result = "⚖️ 비김"
        else:
            game_result = "❌ 패배"
            elapsed_time += 3  # 패배 시 추가 시간

        result_placeholder.write(f"🖐 {user_choice} vs 👾 {monster_choice} → **{game_result}**")
        game_progress_placeholder.write(f"🔹 몬스터 MP 남음: {monster_mp}")

        time.sleep(1)

    message_placeholder = st.empty()
    message_placeholder.success("🎉 몬스터를 물리쳤습니다!")
    cap.release()

    # 승리 기록 업데이트
    win_df = pd.read_csv(csv_file)
    new_record = pd.DataFrame({
        "이름": [st.session_state.get("user_name", "Player")],
        "시간": [elapsed_time],
        "승리 횟수": [win_count],
        "몬스터 MP": [st.session_state.initial_mp]
    })
    win_df = pd.concat([win_df, new_record], ignore_index=True)
    win_df.to_csv(csv_file, index=False)

    st.subheader(f"🏆 몬스터 MP {st.session_state.initial_mp} 랭킹")
    ranking_df = win_df[win_df["몬스터 MP"] == st.session_state.initial_mp].sort_values(by="시간").head(5)
    st.table(ranking_df.set_index("이름"))
