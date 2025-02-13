import streamlit as st

def run_ml():
    st.title("🎮 Teachable Machine을 활용한 가위 바위 보 게임 개발 및 배포 과정 🚀")
    
    # 프로젝트 개요
    st.write("")
    st.subheader("📌 1. 프로젝트 개요")
    st.markdown('''
    **"✊✋✌ 가위 바위 보 몬스터 배틀"**은 유저가 사진을 캡처하여 **🤖 Teachable Machine**이 이를 분석한 후,  
    **AI와 가위 바위 보 게임을 진행하는 웹 애플리케이션**입니다.  
    게임이 종료되면 **🏆 랭킹 시스템**을 통해 자신의 순위를 확인할 수 있으며,  
    **📂 CSV 파일**을 이용해 기록을 저장하고 관리합니다.
    ''')
    
    st.write("-----------")
    
    # Teachable Machine 학습 과정
    st.subheader("🤖 2. Teachable Machine 학습 과정")
    st.markdown('''
    ### 🔍 데이터 수집 및 전처리
    - **📸 3개의 클래스(가위, 바위, 보)**를 설정하고 각각 약 **900장**의 사진을 학습 데이터로 사용했습니다.  
    - **🔄 80 에포크, 배치 크기 16**으로 모델을 학습하여 최적화했습니다.
    
    ### 🎯튜닝 및 테스트
    - 초기에는 **📈 에포크 수가 너무 커서 과적합(Overfitting) 발생** ❌  
    - **🔬 테스트 & 트레이닝 반복** → 최적의 학습 설정을 찾아 개선 ✔  
    - 최적화된 모델을 **🖥️ VSC(Visual Studio Code)로 내보내기** 후, 애플리케이션에 활용했습니다.
    ''')

    st.write('------------')

    # 배포 과정
    st.subheader("🚀 3. 배포 과정")
    st.markdown('''
    ### 🏗️ Streamlit을 이용한 로컬 테스트
    - **Streamlit을 활용하여 🖥️ 로컬 환경에서 테스트 진행**
    - `📄 requirements.txt` 파일을 생성하여 **🔄 외부 환경에서도 실행 가능하도록 설정**

    ### ⚠️ 배포 중 발생한 문제 해결
    - **🚫 로컬에서는 잘 실행되었으나, 배포 과정에서 웹캠 기능이 정상 작동하지 않음**
    - **📷 영상 촬영과 사진 캡처를 동시에 사용할 수 없는 문제 발생**
    - 해결책: **📸 사진 캡처 방식으로 변경**
    - 이후 `🔧 requirements.txt` 파일 수정 후 **GitHub에 푸시 → 🚀 재배포 완료**
    ''')

    st.write("------------")

    # 게임 진행 방식 및 랭킹 시스템
    st.subheader("🎮 4. 게임 진행 방식 및 랭킹 시스템")
    st.markdown('''
    ### 🎲 게임 진행 방식
    1️⃣ 유저가 **📷 카메라를 통해 손 모양을 촬영**  
    2️⃣ **🤖 Teachable Machine이 이미지를 분석**하여 유저가 낸 ✊/✋/✌을 인식  
    3️⃣ **🎲 AI가 랜덤하게 ✊/✋/✌을 선택하여 대결 진행**  
    4️⃣ **⚡ 승/패/비김 결과**에 따라 몬스터의 MP(체력)가 변동  
    5️⃣ **🏆 5번의 대결 후, 최종 승리 횟수와 함께 랭킹 시스템에 반영**
    
    ### 📊 랭킹 시스템
    - **🥇 승리 횟수가 많고, ❤️ 남은 MP가 적을수록 높은 랭킹 차지**
    - 같은 닉네임이 존재할 경우 **기존 점수보다 높은 기록만 업데이트**
    - **📂 CSV 파일**에 저장하여 이후에도 기록 유지 & 분석 가능  
    
    ### 🎭 유저 커스터마이징 기능
    - 유저는 **📝 닉네임을 설정**하여 더욱 개성 있는 플레이 가능  
    - **🏅 닉네임 기반 랭킹 경쟁** 가능 (ex. ‘가위왕’, ‘바위전사’ 등)
    ''')

    st.write('---------------')

    # 기타 정보
    st.subheader("📚 5. 기타 정보")
    st.write('''
    📸 **사진 출처**: [Rock Paper Scissors Dataset](https://www.kaggle.com/datasets/alexandredj/rock-paper-scissors-dataset)  
    📝 **블로그 주소**: [https://tbghdus.tistory.com/120](https://tbghdus.tistory.com/120)  
    📧 **개발자 이메일**: vhzkflfltm6@gmail.com  
    🖥️ **GitHub 저장소**: [https://github.com/qoeka98/paint-app](https://github.com/qoeka98/paint-app)  
    ''')

