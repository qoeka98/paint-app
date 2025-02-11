import streamlit as st
import tensorflow as tf
import numpy as np
import os
import cv2
from PIL import Image
import time

def run_game():
    # ✅ 모델 로드
    model_path = "model/keras_model.h5"
    if not os.path.exists(model_path):
        st.error(f"❌ 모델 파일이 존재하지 않습니다: {model_path}")
        return

    model = tf.keras.models.load_model(model_path)
    class_names = ["가위", "바위", "보"]

    # ✅ 세션 변수 초기화
    if "monster_mp" not in st.session_state:
        st.session_state.monster_mp = 50  # 기본값 설정
    if "initial_mp" not in st.session_state:
        st.session_state.initial_mp = st.session_state.monster_mp
    if "game_running" not in st.session_state:
        st.session_state.game_running = True

    st.subheader("🎮 가위바위보 몬스터 배틀 게임")
    st.info("📸 아래 버튼을 눌러 손 모양을 촬영하세요! 몬스터 MP가 0이 될 때까지 계속 도전하세요!")

    # ✅ 몬스터 MP가 0이면 게임 종료 메시지 표시
    if st.session_state.monster_mp <= 0:
        st.success("🎉 몬스터를 물리쳤습니다! 게임 종료!")
        return

    # ✅ 카메라 입력 (사용자가 직접 촬영)
    img_file = st.camera_input("📷 손 모양을 촬영하세요")

    if img_file:
        # ✅ 촬영된 이미지를 OpenCV 형식으로 변환
        img = Image.open(img_file)
        img = img.convert("RGB")
        img = img.resize((224, 224))  # 모델 입력 크기로 조정
        img_array = np.array(img, dtype=np.float32) / 255.0
        img_array = np.expand_dims(img_array, axis=0)

        # ✅ AI 모델 예측
        prediction = model.predict(img_array)
        class_index = np.argmax(prediction)
        confidence = np.max(prediction)

        if confidence >= 0.7:
            user_choice = class_names[class_index]
            monster_choice = np.random.choice(["가위", "바위", "보"])

            # ✅ 결과 판정
            game_result = "⚖️ 비김"
            if (user_choice == "가위" and monster_choice == "보") or \
               (user_choice == "바위" and monster_choice == "가위") or \
               (user_choice == "보" and monster_choice == "바위"):
                game_result = "✅ 승리"
                st.session_state.monster_mp -= 10  # 🔥 승리 시 몬스터 MP 10 감소
            elif user_choice != monster_choice:
                game_result = "❌ 패배"

            # ✅ 결과 출력
            st.subheader(f"🖐 내 선택: {user_choice}  VS  👾 몬스터 선택: {monster_choice}")
            st.markdown(f"### 결과 ➡️ **{game_result}**")

            # ✅ MP 업데이트
            mp_percentage = max(st.session_state.monster_mp / st.session_state.initial_mp, 0)
            st.progress(mp_percentage)

            # ✅ 몬스터 MP가 0이면 게임 종료
            if st.session_state.monster_mp <= 0:
                st.success("🎉 몬스터를 물리쳤습니다! 게임 종료!")
                return

        else:
            st.warning("⚠️ 손을 정확히 보여주세요! 판별 실패.")

    # ✅ 게임이 끝나지 않았으면, 계속 촬영 가능하도록 UI 유지
    st.button("📸 다시 촬영하기")
