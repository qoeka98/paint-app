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

    # Streamlit UI 설정
    st.subheader("🎮 게임을 시작합니다!")
    st.info("웹캠 또는 이미지 업로드를 통해 가위바위보를 인식합니다.")

    # 웹캠이 정상적으로 실행되는지 확인
    cap = cv2.VideoCapture(0)
    webcam_available = cap.isOpened()  # 웹캠 상태 확인
    cap.release()

    # 웹캠 사용 여부 선택 (웹캠이 감지되지 않으면 자동으로 이미지 업로드 사용)
    use_webcam = False
    if webcam_available:
        use_webcam = st.radio("📷 입력 방식 선택", ["웹캠 사용", "이미지 업로드"]) == "웹캠 사용"
    else:
        st.warning("❌ 웹캠을 사용할 수 없습니다. 이미지를 업로드해주세요.")

    # 이미지 업로드 또는 웹캠 촬영
    uploaded_image = None
    if use_webcam:
        cap = cv2.VideoCapture(0)
        stframe = st.empty()  # 실시간 웹캠 영상 표시용
        
        if cap.isOpened():
            st.info("📸 웹캠이 감지되었습니다. 손을 네모 안에 올려주세요!")

            # 웹캠 피드 보여주기
            while True:
                ret, frame = cap.read()
                if not ret:
                    st.error("❌ 웹캠을 찾을 수 없습니다.")
                    break

                h, w, _ = frame.shape
                box_size = min(h, w) // 2
                x1, y1 = (w - box_size) // 2, (h - box_size) // 2
                x2, y2 = x1 + box_size, y1 + box_size
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

                stframe.image(frame, channels="BGR", use_column_width=True)

                if st.button("📸 촬영하기"):
                    uploaded_image = frame  # 촬영된 이미지 저장
                    break

            cap.release()
            stframe.empty()
        else:
            st.error("❌ 웹캠을 찾을 수 없습니다.")

    else:
        uploaded_image = st.file_uploader("📤 이미지를 업로드하세요", type=["jpg", "png", "jpeg"])

    if uploaded_image is not None:
        # 업로드된 이미지 처리
        if not isinstance(uploaded_image, np.ndarray):  # 웹캠 이미지가 아니라면 PIL 이미지 변환
            image = Image.open(uploaded_image)
            image = np.array(image)
        else:
            image = uploaded_image

        # 이미지 전처리
        img = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        img = cv2.resize(img, (224, 224))
        img = np.array(img, dtype=np.float32) / 255.0
        img = np.expand_dims(img, axis=0)

        # 모델 예측
        prediction = model.predict(img)
        class_index = np.argmax(prediction)
        confidence = np.max(prediction)

        if confidence < 0.7:
            st.warning("⚠️ 손을 네모 안에 정확하게 올려주세요!")
        else:
            user_choice = class_names[class_index]
            monster_choice = np.random.choice(["가위", "바위", "보"])

            # 승패 판정
            game_result = "⚖️ 비김"
            result_image = "image/비김.png"

            if (user_choice == "가위" and monster_choice == "보") or \
                (user_choice == "바위" and monster_choice == "가위") or \
                (user_choice == "보" and monster_choice == "바위"):
                game_result = "✅ 승리"
                result_image = "image/이겼다.png"
            elif user_choice != monster_choice:
                game_result = "❌ 패배"
                result_image = "image/졌다.png"

            # 결과 표시
            st.image(result_image, use_column_width=True)
            st.success(f"🎮 당신의 선택: **{user_choice}** | 몬스터의 선택: **{monster_choice}**")
            st.subheader(f"🏆 결과: {game_result}")
