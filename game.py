import tensorflow as tf
import numpy as np
import cv2
import time
import pandas as pd
import os
import streamlit as st
from PIL import Image

def run_game():
    # Teachable Machine 모델 로드
    model_path = "model/keras_model.h5"
    model = tf.keras.models.load_model(model_path)

    # 클래스 매핑
    class_names = ["가위", "바위", "보"]

    # 승리 기록 저장 파일
    csv_file = "win_records.csv"

    # 기존 CSV 파일이 없거나, 컬럼이 없으면 초기화
    if not os.path.exists(csv_file):
        pd.DataFrame(columns=["이름", "시간", "승리 횟수", "몬스터 MP"]).to_csv(csv_file, index=False)

    # **세션 변수 초기화 (최초 시작 시 잔상 제거)**
    if "ranking_updated" not in st.session_state:
        st.session_state.ranking_updated = False
    if "ranking_displayed" not in st.session_state:
        st.session_state.ranking_displayed = False
    if "game_message_displayed" not in st.session_state:
        st.session_state.game_message_displayed = False  # 🔹 '몬스터를 물리쳤습니다' 잔상 제거

    # 게임 시작 UI
    st.subheader("🎮 게임을 시작합니다!")
    st.info('웹 카메라 속 초록 상자에 정확히 손모양을 보여주세요')

    # **게임 재시작 & 종료 버튼**
    col_button1, col_button2 = st.columns(2)
    with col_button1:
        if st.button("🔄 게임 재시작"):
            st.session_state.game_running = True
            st.session_state.ranking_updated = False
            st.session_state.ranking_displayed = False
            st.session_state.game_message_displayed = False  # 🔹 '몬스터를 물리쳤습니다' 잔상 제거
            st.rerun()
    with col_button2:
        if st.button("🛑 게임 종료"):
            st.session_state.game_running = False
            st.session_state.game_message = "게임이 강제 종료되었습니다!"
            st.stop()

    cap = cv2.VideoCapture(0)  # 웹캠 활성화
    monster_mp = st.session_state.monster_mp  # 세션 상태에서 가져오기

    # 🎯 **웹캠 & 결과 이미지를 같은 열(Column)으로 배치**
    col1, col2 = st.columns([1, 1])  

    with col1:
        image_placeholder = st.empty()  # 웹캠 영상
        countdown_placeholder = st.empty()  # 카운트다운 표시
    with col2:
        result_image_placeholder = st.empty()  # 결과 이미지

    result_placeholder = st.empty()
    mp_placeholder = st.empty()
    game_progress_placeholder = st.empty()
    timer_placeholder = st.empty()  # 실시간 초 표시
    ranking_placeholder = st.empty()  # 🔹 랭킹 표시 공간 (초기화)
    user_rank_placeholder = st.empty()  # 🔹 내 랭킹 표시 공간
    message_placeholder = st.empty()  # 🔹 '몬스터를 물리쳤습니다' 메시지 제거

    # **🔹 게임 시작 시 잔상 제거**
    ranking_placeholder.empty()
    user_rank_placeholder.empty()
    message_placeholder.empty()  # 🔹 '몬스터를 물리쳤습니다' 메시지 잔상 제거

    # 초기 빈 이미지 설정 (결과 이미지 자리 유지)
    result_image_placeholder.image("image/가위바위보 홈.png", use_container_width=True)

    start_time = time.time()  # 게임 시작 시간
    win_count = 0  # 승리 횟수 기록

    while monster_mp > 0:
        # ⏳ **실시간 경과 시간 표시**
        elapsed_time = round(time.time() - start_time, 2)
        minutes, seconds = divmod(int(elapsed_time), 60)
        timer_placeholder.write(f"⏳ **경과 시간: {minutes:02}:{seconds:02}**")

        # 🎯 **실시간 웹캠 & 카운트다운 표시**
        countdown_time = 3  # 3초 뒤 촬영
        capture_time = time.time() + countdown_time  # 촬영 시점 계산

        while time.time() < capture_time:
            ret, frame = cap.read()
            if not ret:
                st.error("❌ 웹캠을 찾을 수 없습니다.")
                break

            # 웹캠에 네모 박스 표시
            h, w, _ = frame.shape
            box_size = min(h, w) // 2
            x1, y1 = (w - box_size) // 2, (h - box_size) // 2
            x2, y2 = x1 + box_size, y1 + box_size

            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

            # 실시간 웹캠 업데이트 (크기 동일 설정)
            image_placeholder.image(frame, channels="BGR", use_container_width=True)
            
            # 남은 시간 업데이트
            remaining_time = int(capture_time - time.time())
            countdown_placeholder.write(f"📸 **{remaining_time}초 뒤 촬영!**")

        countdown_placeholder.write("📸 **찰칵!**")  # 촬영 순간 강조

        # 📸 **촬영**
        ret, frame = cap.read()
        if not ret:
            st.error("❌ 웹캠을 찾을 수 없습니다.")
            break

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

        # ⚔️ **승패 판정 및 MP 감소**
        game_result = "⚖️ 비김"
        result_image = "image/비김.png"  

        if (user_choice == "가위" and monster_choice == "보") or \
            (user_choice == "바위" and monster_choice == "가위") or \
            (user_choice == "보" and monster_choice == "바위"):
            game_result = "✅ 승리"
            result_image = "image/이겼다.png"  
            monster_mp -= 10  # 🔥 **승리 시 몬스터 MP 10 감소**
            win_count += 1
        elif user_choice != monster_choice:
            game_result = "❌ 패배"
            result_image = "image/졌다.png"  
            start_time += 3  # ⏳ 패배 시 패널티 3초 추가

        # **결과 이미지 업데이트**
        result_image_placeholder.image(result_image, use_container_width=True)
        
        # **MP 업데이트 반영**
        game_progress_placeholder.write(f"🔹 진행 상황: 몬스터 MP {monster_mp} 남음")
        mp_placeholder.progress(monster_mp / st.session_state.initial_mp)

        time.sleep(1)

    # **몬스터를 물리친 메시지 및 승리 이미지 변경**
    message_placeholder.success("🎉 몬스터를 물리쳤습니다!")
    result_image_placeholder.image("image/승리.png", use_container_width=True)

    cap.release()
