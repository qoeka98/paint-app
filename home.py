import streamlit as st

def run_home():
    # 게임 타이틀
    st.title("🔥 가위바위보 몬스터 배틀 🔥")
    st.subheader("🛡️ 최강의 가위바위보 전사가 되어 몬스터를 쓰러뜨리세요!")

    # 게임 소개 메시지
    st.success("🎮 **환영합니다!** 가위바위보 스킬을 활용하여 강력한 몬스터와 맞서 싸우세요!")
    st.info("🏆 **누가 더 빠르게 몬스터를 처치할 수 있을까요?** 랭킹을 통해 최강자를 확인하세요!")

    # 게임 이미지 표시
    st.image('image/게임.png')

 
