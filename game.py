import streamlit as st
import os
import numpy as np
import tensorflow as tf
import random
from PIL import Image
import time
import pandas as pd

# ✅ 저장된 데이터 파일 설정
CAPTURED_DIR = "./captured_images/"
CSV_FILE = "win_records.csv"

# ✅ 저장된 게임 결과 폴더가 없으면 생성
if not os.path.exists(CAPTURED_DIR):
    os.makedirs(CAPTURED_DIR)

# ✅ AI 모델 로드 (Teachable Machine 학습 모델)
MODEL_PATH = "model/keras_model.h5"
model = tf.keras.models.load_model(MODEL_PATH, compile=False)
model.compile(optimizer=tf.keras.optimizers.Adam(), loss="categorical_crossentropy", metrics=["accuracy"])

# ✅ 클래스 매핑 (가위/바위/보)
class_names = ["가위", "바위", "보"]

# ✅ 승리 기록 저장 파일이 없으면 생성
if not os.path.exists(CSV_FILE):
    pd.DataFrame(columns=["이름", "승리 횟수", "소요 시간", "몬스터 MP 감소"]).to_csv(CSV_FILE, index=False)

def save_uploaded_file(uploaded_file, file_name):
    """📸 촬영된 이미지를 저장"""
    file_path = os.path.join(CAPTURED_DIR, file_name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return file_path

def process_uploaded_image(image_path):
    """유저가 선택한 사진을 AI가 분석하여 가위바위보 결과 반환"""
    if image_path in st.session_state.used_photos:
        return "⚠️ 이미 사용된 사진입니다!"

    # ✅ 이미지 전처리
    image = Image.open(image_path).convert("RGB")
    image = image.resize((224, 224))
    image = np.array(image, dtype=np.float32) / 255.0
    image = np.expand_dims(image, axis=0)

    # ✅ 모델 예측 수행
    prediction = model.predict(image)
    class_index = np.argmax(prediction)
    confidence = np.max(prediction)

    if confidence < 0.7:
        return "⚠️ 인식이 정확하지 않습니다. 다시 선택하세요!"

    # ✅ AI vs 유저 가위바위보 진행
    user_choice = class_names[class_index]  
    monster_choice = random.choice(["가위", "바위", "보"])  

    if (user_choice == "가위" and monster_choice == "보") or \
       (user_choice == "바위" and monster_choice == "가위") or \
       (user_choice == "보" and monster_choice == "바위"):
        result = "✅ 승리"
        st.session_state.win_count += 1  
        st.session_state.monster_mp -= 10  
        if st.session_state.monster_mp <= 0:
            st.session_state.end_time = time.time()
    elif user_choice != monster_choice:
        result = "❌ 패배"
        time.sleep(3)  

    st.session_state.used_photos.add(image_path)  
    return f"🖐 내 선택: {user_choice}  VS  👾 AI 선택: {monster_choice} ➡️ {result}"

def run_game():
    """🎮 가위바위보 게임 실행"""
    if "captured_photos" not in st.session_state:
        st.session_state.captured_photos = []
    if "used_photos" not in st.session_state:
        st.session_state.used_photos = set()
    if "remaining_plays" not in st.session_state:
        st.session_state.remaining_plays = 5
    if "win_count" not in st.session_state:
        st.session_state.win_count = 0
    if "monster_mp" not in st.session_state:
        st.session_state.monster_mp = 50
    if "start_time" not in st.session_state:
        st.session_state.start_time = time.time()
    if "end_time" not in st.session_state:
        st.session_state.end_time = None
    if "user_name" not in st.session_state:
        st.session_state.user_name = st.text_input("이름을 입력하세요", "Player")

    st.title("🎮 가위바위보 촬영 게임")

    if len(st.session_state.captured_photos) < 5:
        st.subheader(f"📸 남은 촬영 횟수: {5 - len(st.session_state.captured_photos)}/5")
        captured_photo = st.camera_input("손 모양을 촬영하세요!")
        if captured_photo:
            file_name = f"photo_{len(st.session_state.captured_photos) + 1}.jpg"
            image_path = save_uploaded_file(captured_photo, file_name)
            st.session_state.captured_photos.append(image_path)
            st.success(f"✅ {file_name} 촬영 완료!")

    if len(st.session_state.captured_photos) == 5 and st.session_state.remaining_plays > 0:
        st.subheader("🎯 촬영 완료! 아래에서 사진을 선택하여 게임을 시작하세요.")

        cols = st.columns(5)
        selected_image = None

        for i, image_path in enumerate(st.session_state.captured_photos):
            with cols[i]:  
                st.image(image_path, caption=f"사진 {i+1}", use_container_width=True)
                if st.button(f"이 사진으로 플레이 {i+1}", key=f"play_{i}"):
                    if image_path in st.session_state.used_photos:
                        st.warning("⚠️ 이미 사용된 사진입니다!")
                    else:
                        selected_image = image_path

        if selected_image:
            result_text = process_uploaded_image(selected_image)
            st.write("📢 결과:", result_text)
            st.session_state.remaining_plays -= 1

    if st.session_state.remaining_plays == 0 or st.session_state.monster_mp <= 0:
        elapsed_time = round(time.time() - st.session_state.start_time, 2)
        st.success(f"🎉 게임 종료! 승리 횟수: {st.session_state.win_count}회, 소요 시간: {elapsed_time}초, MP 감소: {50 - st.session_state.monster_mp}")

        # ✅ 최종 결과 저장
        new_record = pd.DataFrame([{
            "이름": st.session_state.user_name,
            "승리 횟수": st.session_state.win_count,
            "소요 시간": elapsed_time,
            "몬스터 MP 감소": 50 - st.session_state.monster_mp
        }])

        records = pd.read_csv(CSV_FILE)
        records = pd.concat([records, new_record], ignore_index=True)
        records.to_csv(CSV_FILE, index=False)

    if st.button("🔄 다시 도전하기"):
        reset_game()

def reset_game():
    st.session_state.clear()
    for file in os.listdir(CAPTURED_DIR):
        os.remove(os.path.join(CAPTURED_DIR, file))
    st.rerun()
