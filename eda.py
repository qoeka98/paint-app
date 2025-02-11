import streamlit as st
import pandas as pd
import os
import sys

# 🚀 경로 문제 해결 (game.py가 같은 폴더에 없을 경우 대비)
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from game import run_game  

def run_eda():
    # 승리 기록 저장 파일
    csv_file = "win_records.csv"

    # 기존 CSV 파일이 없거나, 컬럼이 없으면 초기화
    if not os.path.exists(csv_file):
        pd.DataFrame(columns=["이름", "시간", "승리 횟수", "몬스터 MP"]).to_csv(csv_file, index=False)

    # 승리 기록 데이터 불러오기
    win_df = pd.read_csv(csv_file)

    # Streamlit 시작
    st.title("🎮 가위바위보 몬스터 배틀")

    # 🔹 **세션 상태 초기화**
    if "monster_mp" not in st.session_state:
        st.session_state.monster_mp = 50  # 기본값 설정
    if "initial_mp" not in st.session_state:
        st.session_state.initial_mp = st.session_state.monster_mp
    if "user_name" not in st.session_state:
        st.session_state.user_name = "Player"
    if "temp_user_name" not in st.session_state:  # 🔹 닉네임 임시 저장 변수 추가
        st.session_state.temp_user_name = st.session_state.user_name

    # 🎭 **게임 설정**
    sub_menu = st.sidebar.radio("게임 메뉴", ["게임 설정", "게임 시작"])

    if sub_menu == "게임 설정":
        st.subheader('게임방법 설명')
        st.info('''가위 바위 보에서 이기면 몬스터의 MP를 갂을 수 있습니다.
                    비기면 몬스터와 대치 상태를 유지합니다.
                    지면 패널티 3초를 받게 됩니다.''')

        st.markdown('''
                    설정을 통해 게임 몬스터의 MP를 조절하여 게임을 즐기세요.
                    누가 더 빨리 몬스터를 처치하는지 랭킹을 통해 확인할 수도 있습니다!
                    ''')
        st.subheader("🎭 게임 설정")

        # 🔹 닉네임 입력
        temp_name = st.text_input("🔹 닉네임을 입력하세요", value=st.session_state.temp_user_name)

        if st.button("닉네임 입력"):
            st.session_state.user_name = temp_name
            st.session_state.temp_user_name = temp_name
            st.success(f"닉네임이 '{temp_name}'(으)로 설정되었습니다!")

        # 몬스터 초기 MP 설정 (radio에 key 추가)
        st.session_state.monster_mp = st.radio(
            "🎭 몬스터 MP 선택", [30, 50, 80], index=1, key="monster_mp_setting"
        )
        st.session_state.initial_mp = st.session_state.monster_mp

        # 🎯 **MP별 랭킹 표시**
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

        # 🎖 **내 랭킹 확인**
        if "이름" in win_df.columns and st.session_state.user_name in win_df["이름"].values:
            user_rank = mp_ranking[mp_ranking["이름"] == st.session_state.user_name].index.min()
            st.write(f"📌 **{st.session_state.user_name}님의 현재 순위: {user_rank + 1}위**")
        else:
            st.write("⚠️ 아직 등록된 랭킹이 없습니다.")

    # 🎮 **게임 시작**
    elif sub_menu == "게임 시작":
        run_game()
