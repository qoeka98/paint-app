import tensorflow as tf
import numpy as np
import pandas as pd
import os
import streamlit as st
from PIL import Image, ImageDraw
import time

def run_game():
    # 모델 로드
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
    st.info('📸 2초 후 자동으로 사진이 촬영됩니다! 손을 초록색 박스 안에 맞춰주세요.')

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

    # 📸 **2초 대기 후 자동 촬영**
    with st.spinner("📸 2초 후 자동으로 사진이 촬영됩니다... 손을 올바르게 배치하세요!"):
        time.sleep(2)

    # 🎥 **카메라 입력 받기**
    image = st.camera_input("📸 손 모양을 촬영하세요!")

    if image is not None:
        # 🖼️ **초록색 네모 테두리 추가**
        img = Image.open(image).convert("RGB")
        draw = ImageDraw.Draw(img)
        img_width, img_height = img.size
        box_size = min(img_width, img_height) // 2
        x1, y1 = (img_width - box_size) // 2, (img_height - box_size) // 2
        x2, y2 = x1 + box_size, y1 + box_size
        draw.rectangle([x1, y1, x2, y2], outline="green", width=5)  # 초록색 네모

        # 🖼️ **이미지 전처리**
        img_cropped = img.crop((x1, y1, x2, y2))  # 초록 네모 안의 부분만 크롭
        img_resized = img_cropped.resize((224, 224))
        img_array = np.array(img_resized, dtype=np.float32) / 255.0
        img_array = np.expand_dims(img_array, axis=0)

        # 🤖 **모델 예측**
        prediction = model.predict(img_array)
        class_index = np.argmax(prediction)
        confidence = np.max(prediction)

        if confidence < 0.7:
            st.warning("⚠️ 손 모양을 정확히 인식하지 못했습니다. 다시 촬영해주세요!")
            return

        # 🏆 **가위바위보 판단**
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
