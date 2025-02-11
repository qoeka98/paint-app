import streamlit as st
import tensorflow as tf
import numpy as np
import cv2
import time
from PIL import Image

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
        st.session_state.monster_mp = 50  
    if "initial_mp" not in st.session_state:
        st.session_state.initial_mp = st.session_state.monster_mp
    if "game_running" not in st.session_state:
        st.session_state.game_running = True

    st.subheader("🎮 가위바위보 몬스터 배틀 게임")
    st.info("📸 아래 웹캠에서 네모 박스 안에 손을 위치시키고 촬영하세요!")

    # ✅ OpenCV 웹캠 실행
    cap = cv2.VideoCapture(0)
    frame_placeholder = st.empty()
    capture_button = st.button("📸 촬영")

    if not cap.isOpened():
        st.error("❌ 웹캠을 찾을 수 없습니다.")
        return

    # ✅ 실시간 웹캠 화면 출력 (네모 박스 포함)
    while not capture_button:
        ret, frame = cap.read()
        if not ret:
            st.error("❌ 웹캠을 찾을 수 없습니다.")
            return

        # ✅ 네모 박스 위치 설정 (화면 중앙)
        h, w, _ = frame.shape
        box_size = min(h, w) // 2
        x1, y1 = (w - box_size) // 2, (h - box_size) // 2
        x2, y2 = x1 + box_size, y1 + box_size

        # ✅ 네모 박스 표시
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 3)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # ✅ Streamlit에 실시간 웹캠 프레임 표시
        frame_placeholder.image(frame, channels="RGB", use_column_width=True)

        # ✅ 0.1초 대기
        time.sleep(0.1)

    # ✅ 촬영 버튼이 눌리면 네모 박스 내부 이미지 캡처
    ret, frame = cap.read()
    cap.release()

    if ret:
        roi = frame[y1:y2, x1:x2]  # 네모 박스 내부 영역만 자르기
        roi = cv2.cvtColor(roi, cv2.COLOR_BGR2RGB)

        # ✅ AI 모델 입력 전처리
        img = Image.fromarray(roi)
        img = img.resize((224, 224))
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
                st.session_state.monster_mp -= 10  
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
                st.session_state.game_running = False
        else:
            st.warning("⚠️ 손을 네모 박스 안에 정확히 위치시키고 다시 촬영해주세요.")
    else:
        st.error("❌ 이미지 촬영에 실패했습니다. 다시 시도해주세요.")
