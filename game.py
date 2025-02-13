import streamlit as st
import time
import numpy as np
import pandas as pd
import os
import tensorflow as tf
from PIL import Image

# ✅ 환경 변수 설정 (TensorFlow CPU 최적화)
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"

# ✅ 모델 로드 (티쳐블 머신 모델)
model_path = "model/keras_model.h5"
if os.path.exists(model_path):
    try:
        model = tf.keras.models.load_model(model_path, compile=False)
        print("✅ 모델 로드 성공!")
    except Exception as e:
        print(f"🚨 모델 로드 실패: {e}")
        model = None
else:
    print(f"경고: 모델 파일 {model_path} 이(가) 존재하지 않습니다. 기본 무작위 예측을 사용합니다.")
    model = None

# Teachable Machine을 이용한 이미지 인식 함수
def process_uploaded_image(image_path):
    try:
        image = Image.open(image_path).convert("RGB")
        image = image.resize((224, 224))
        image = np.array(image, dtype=np.float32) / 255.0
        image = np.expand_dims(image, axis=0)
        if model is not None:
            prediction = model.predict(image)
            class_index = np.argmax(prediction)
        else:
            class_index = np.random.randint(0, 3)
    except Exception as e:
        st.error(f"모델 예측 에러: {e}")
        class_index = np.random.randint(0, 3)
    class_names = ["가위", "바위", "보"]
    return class_names[class_index]

def save_uploaded_file(uploaded_file, file_name):
    os.makedirs("uploads", exist_ok=True)  # uploads 폴더 생성
    file_path = os.path.join("uploads", file_name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return file_path

def reset_game():
    for key in ["captured_photos", "results", "remaining_plays", "win_count", "monster_mp", "last_result"]:
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()

def run_game():
    st.title("📸 가위바위보 사진 게임")
    if st.button("🔄 게임 재시작"):
        reset_game()
    
    # 세션 스테이트 초기화
    if "captured_photos" not in st.session_state:
        st.session_state.captured_photos = []
    if "results" not in st.session_state:
        st.session_state.results = {}  # key: image_path, value: 결과 dict
    if "remaining_plays" not in st.session_state:
        st.session_state.remaining_plays = 5
    if "win_count" not in st.session_state:
        st.session_state.win_count = 0
    if "monster_mp" not in st.session_state:
        st.session_state.monster_mp = 50
    if "user_name" not in st.session_state:
        st.session_state.user_name = "player"
    if "last_result" not in st.session_state:
        st.session_state.last_result = ""
    
    # 진행 상태: 촬영된 사진의 수만 텍스트로 표시 (progress bar 제거)
    st.subheader(f"📸 현재 촬영된 사진: {len(st.session_state.captured_photos)}/5")
    st.info("닉네임이 중복될 수 있습니다. 중복되면 결과에 반영되지 않을 수 있으니 자신만의 유니크한 닉네임을 설정하세요!")
    temp_name = st.text_input("🔹 닉네임을 입력하세요", value=st.session_state.temp_user_name)
        
    if st.button("입력후 좌측 게임 시작으로 이동하세요"):
            st.session_state.user_name = temp_name
            st.session_state.temp_user_name = temp_name
            st.success(f"닉네임이 '{temp_name}'(으)로 설정되었습니다!")
    st.info('사진 촬영을 통해 가위 바위 보 스킬 5장을 획득합시다!')
    st.info('Take Photo를 통해사진을찍고 Clear Photo를 눌러 초기화시키고 다시 Take Photo를 이용해 사진을 찍으면됩니다 ' )
    
    captured_photo = st.camera_input("Take Photo & Clear Photo를 통해 손 모양을 촬영하세요", key="camera_input")
    if captured_photo:
        if len(st.session_state.captured_photos) < 5:
            file_name = f"photo_{int(time.time())}.jpg"
            image_path = save_uploaded_file(captured_photo, file_name)
            st.session_state.captured_photos.append(image_path)
            st.success(f"✅ {file_name} 촬영 완료! ({len(st.session_state.captured_photos)}/5)")
        else:
            st.warning("📸 이미 5장의 사진을 촬영하였습니다!!")
    
    selected_image = None
    if len(st.session_state.captured_photos) == 5:
        st.subheader("🎯 촬영 완료! 아래에서 사진을 선택하여 게임을 진행하세요.")
        cols = st.columns(5)
        for i, image_path in enumerate(st.session_state.captured_photos):
            with cols[i]:
                st.image(image_path, caption=f"사진 {i+1}", use_container_width=True)
                # 버튼을 이미지가 이미 처리된 경우 disabled=True로 표시
                if image_path in st.session_state.results:
                    st.button(f"이미 사용됨", key=f"play_{i}", disabled=True)
                else:
                    if st.button(f"이 사진으로 플레이 {i+1}", key=f"play_{i}"):
                        user_choice = process_uploaded_image(image_path)
                        monster_choice = np.random.choice(["가위", "바위", "보"])
                        
                        game_result = "⚖️ 비김"
                        result_image = "image/비김.png"
                        if (user_choice == "가위" and monster_choice == "보") or \
                           (user_choice == "바위" and monster_choice == "가위") or \
                           (user_choice == "보" and monster_choice == "바위"):
                            game_result = "✅ 승리"
                            result_image = "image/이겼다.png"
                            st.session_state.win_count += 1
                            st.session_state.monster_mp -= st.session_state.monster_mp // 5
                        elif user_choice != monster_choice:
                            game_result = "❌ 패배"
                            result_image = "image/졌다.png"
                            st.session_state.monster_mp += 3
                            st.session_state.remaining_plays -= 1
                        st.session_state.results[image_path] = {
                            "user_choice": user_choice,
                            "monster_choice": monster_choice,
                            "game_result": game_result,
                            "result_image": result_image,
                            "monster_mp_after": st.session_state.monster_mp
                        }
                        selected_image = image_path
    
    if selected_image and (selected_image in st.session_state.results):
        res = st.session_state.results[selected_image]
        st.subheader(f"🖐 내 선택: {res['user_choice']}  VS  👾 몬스터 선택: {res['monster_choice']}  ({res['game_result']})")
        st.subheader(f"🔹 진행 상황: 몬스터 MP {res['monster_mp_after']} 남음")
        
        cols = st.columns(2)
        with cols[0]:
            st.image(selected_image, caption="선택한 이미지", use_container_width=True)
        with cols[1]:
            st.image(res["result_image"], caption="결과 이미지", use_container_width=True)
    
    # 5장의 사진 모두 처리되면 승리 이미지와 현재 랭킹, 랭킹 테이블만 출력
    if len(st.session_state.results) == 5:
        st.write("---")
        
        st.write("")
        st.title('🎊 게임 종료! 🎉"')
        st.write("")
        st.image("image/승리.png", use_container_width=True)
        
        csv_file = "ranking.csv"
        if os.path.exists(csv_file):
            win_df = pd.read_csv(csv_file)
        else:
            win_df = pd.DataFrame(columns=["닉네임", "승리 횟수", "남은 MP"])
        
        # 기존에 동일 닉네임의 기록이 있으면, 새 기록이 승리 횟수가 많고 남은 MP가 적을 때만 업데이트
        existing_entry = win_df[win_df["닉네임"] == st.session_state.user_name]
        if not existing_entry.empty:
            best_rank = existing_entry.iloc[0]
            if (st.session_state.win_count > best_rank["승리 횟수"]) and (st.session_state.monster_mp < best_rank["남은 MP"]):
                # 기존 기록을 제거하고 업데이트
                win_df = win_df[win_df["닉네임"] != st.session_state.user_name]
                updated = True
            else:
                updated = False
        else:
            updated = True
        
        if updated:
            new_record = pd.DataFrame([{
                "닉네임": st.session_state.user_name,
                "승리 횟수": st.session_state.win_count,
                "남은 MP": st.session_state.monster_mp
            }])
            win_df = pd.concat([win_df, new_record], ignore_index=True)
            win_df = win_df.sort_values(by=["승리 횟수", "남은 MP"], ascending=[False, True])
            win_df.to_csv(csv_file, index=False)
            st.write("🏆 랭킹이 업데이트되었습니다!")
        
            
        
        win_df = win_df.sort_values(by=["승리 횟수", "남은 MP"], ascending=[False, True])
        rank = win_df[win_df["닉네임"] == st.session_state.user_name].index[0] + 1
        st.info("🏆 기존의 점수보다 낮으면 랭킹에 반영되지 않습니다.")
        st.info(f"🏅 {st.session_state.user_name} 님의 현재 랭킹은 {rank}위 입니다.")
        st.subheader("🏆 랭킹")
        st.table(win_df.head())

