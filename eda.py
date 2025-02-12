import streamlit as st
import pandas as pd
import os
import time
from game import run_game  # ✅ 함수 내부에서 import하여 순환 참조 방지
def run_eda():

    # ✅ 승리 기록 저장 파일
    csv_file = "win_records.csv"

    if not os.path.exists(csv_file):
        pd.DataFrame(columns=["이름", "시간", "승리 횟수", "몬스터 MP"]).to_csv(csv_file, index=False)

    win_df = pd.read_csv(csv_file)

    # ✅ 게임 상태 변수 초기화
    if "monster_mp" not in st.session_state:
        st.session_state.monster_mp = 50  
    if "initial_mp" not in st.session_state:
        st.session_state.initial_mp = st.session_state.monster_mp
    if "user_name" not in st.session_state:
        st.session_state.user_name = "Player"
    if "temp_user_name" not in st.session_state:
        st.session_state.temp_user_name = st.session_state.user_name
    if "win_count" not in st.session_state:
        st.session_state.win_count = 0  # 승리 횟수 저장

    # ✅ Streamlit UI 시작
    st.title("🎮 가위바위보 몬스터 배틀")

    sub_menu = st.sidebar.radio("게임 메뉴", ["게임 설정", "게임 시작"])

    if sub_menu == "게임 설정":
        st.subheader('게임방법 설명')
        st.info('''
            📌 가위 바위 보에서 이기면 몬스터의 MP를 깎을 수 있습니다.
            📌 비기면 몬스터와 대치 상태를 유지합니다.
            📌 지면 패널티로 3초 동안 기다려야 합니다.
            📌 5번의 대결이 끝나면 최종 승리 횟수가 기록됩니다.
        ''')

        temp_name = st.text_input("🔹 닉네임을 입력하세요", value=st.session_state.temp_user_name)
        if st.button("닉네임 입력"):
            st.session_state.user_name = temp_name
            st.session_state.temp_user_name = temp_name
            st.success(f"닉네임이 '{temp_name}'(으)로 설정되었습니다!")

        st.session_state.monster_mp = st.radio(
            "🎭 몬스터 MP 선택", [30, 50, 80], index=1, key="monster_mp_setting"
        )
        st.session_state.initial_mp = st.session_state.monster_mp

        # ✅ 몬스터 MP별 랭킹 표시
        st.subheader(f"🏆 몬스터 MP {st.session_state.initial_mp} 랭킹")
        if not win_df.empty:
            mp_ranking = win_df[win_df["몬스터 MP"] == st.session_state.initial_mp].sort_values(by="시간").reset_index(drop=True)
            if not mp_ranking.empty:
                mp_ranking.index += 1
                st.table(mp_ranking.head(5)[["이름", "시간", "승리 횟수"]])
            else:
                st.write("⚠️ 아직 등록된 기록이 없습니다.")
        else:
            st.write("⚠️ 아직 등록된 기록이 없습니다.")

    elif sub_menu == "게임 시작":
        run_game()  # ✅ 게임 실행
