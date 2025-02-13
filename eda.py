import streamlit as st
import pandas as pd
import os
from game import run_game  # ✅ 함수 내부에서 import하여 순환 참조 방지

def run_eda():
    # ✅ 승리 기록 저장 파일
    csv_file = "ranking.csv"
    
    if not os.path.exists(csv_file):
        pd.DataFrame(columns=["닉네임", "승리 횟수", "남은 MP"]).to_csv(csv_file, index=False)
    
    win_df = pd.read_csv(csv_file)
    
    # ✅ 게임 상태 변수 초기화
    state_defaults = {
        "monster_mp": 50,
        "initial_mp": 50,
        "user_name": "Player",
        "temp_user_name": "Player",
        "win_count": 0
    }
    
    for key, value in state_defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value
    
    # ✅ Streamlit UI 시작
    st.title("🎮 가위바위보 몬스터 배틀")
    
    sub_menu = st.sidebar.radio("게임 메뉴", ["게임 설명", "게임 시작"])
    
    if sub_menu == "게임 설명":
        st.subheader("게임방법 설명")
        st.info(
            """
            📌 가위 바위 보 사진촬영으로 자신의 스킬을 5개를 획득합니다다

            📌 가위 바위 보에서 이기면 몬스터의 MP를 깎을 수 있습니다.

            📌 비기면 몬스터와 대치 상태를 유지합니다.

            📌 지면 패널티로 몬스터의 MP가 회복됩니다. 

            📌 5번의 대결이 끝나면 최종 승리 횟수가 기록됩니다.
            """
        )
        st.info("닉네임이 중복될 수 있습니다. 중복되면 결과에 반영되지 않을 수 있으니 자신만의 유니크한 닉네임을 설정하세요!")
        temp_name = st.text_input("🔹 닉네임을 입력하세요", value=st.session_state.temp_user_name)
        
        if st.button("입력후 게임 시작으로 이동하세요"):
            st.session_state.user_name = temp_name
            st.session_state.temp_user_name = temp_name
            st.success(f"닉네임이 '{temp_name}'(으)로 설정되었습니다!")
        
        # 기본 랭킹만 표시 (몬스터 MP 선택 제거)
        st.subheader("🏆 게임 랭킹을 확인 해보세요")
        st.info('누가 누가 많이 몬스터의 MP를 갂고 승률이 높을까?!🏆')
        if not win_df.empty:
            # 전체 기록을 승리 횟수 내림차순으로 정렬하여 상위 5개 기록 표시
            win_df_sorted = win_df.sort_values(by=["승리 횟수"], ascending=False).reset_index(drop=True)
            win_df_sorted.index += 1  # 순위 표시
            st.table(win_df_sorted.head(5)[["닉네임", "승리 횟수", "남은 MP"]])
        else:
            st.write("⚠️ 아직 등록된 기록이 없습니다.")
    
    elif sub_menu == "게임 시작":
        run_game()  # ✅ 게임 실행


