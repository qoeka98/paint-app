# 🎮 티쳐블 머신을 활용한 가위 바위 보 게임 개발 및 배포 과정

## 🚀 프로젝트 개요
**"가위바위보 몬스터 배틀"**은 유저가 사진을 캡처하여 **Teachable Machine**이 이를 분석한 후, AI와 가위 바위 보 게임을 진행하는 **웹 애플리케이션**입니다. 게임이 종료되면 랭킹 시스템을 통해 자신의 순위를 확인할 수 있으며, CSV 파일을 이용해 기록을 저장하고 관리합니다.

✅ **딥러닝을 활용한 실시간 손 모양 인식**  
✅ **스릴 넘치는 몬스터 배틀과 전략적 플레이**  
✅ **개인 랭킹 시스템을 통한 경쟁 요소 추가**  
✅ **웹 기반 인터페이스로 손쉬운 접근 및 플레이**

## 📌 Teachable Machine 학습 과정

### 📌 데이터 수집 및 전처리
- **3개의 클래스(가위, 바위, 보)**를 설정하고 각각 약 **900장의 사진**을 학습 데이터로 사용했습니다.
- 데이터 확보 후, **80 에포크, 배치 크기 16**으로 모델을 학습했습니다.

### 📌 튜닝 및 테스트
- 초기에는 에포크 수를 너무 크게 설정하여 **과적합(overfitting) 문제**가 발생했습니다.
- 이를 해결하기 위해 여러 번의 테스트와 트레이닝을 반복하며 최적의 학습 설정을 찾았습니다.
- 최적화된 모델을 내보낸 후, **Visual Studio Code**를 활용하여 애플리케이션에서 사용할 수 있도록 구성했습니다.

## 🔥 배포 과정

### 📌 Streamlit을 이용한 로컬 테스트
- **Streamlit**을 활용하여 로컬 환경에서 테스트를 진행했습니다.
- `requirements.txt` 파일을 생성하여 외부 환경에서도 실행 가능하도록 설정했습니다.

### 📌 배포 중 발생한 문제 해결
- 로컬에서는 정상적으로 실행되었지만, 배포 과정에서 **웹캠 기능이 정상적으로 작동하지 않는 문제**가 발생했습니다.
- 영상 촬영과 사진 캡처를 동시에 사용할 수 없는 제한 사항이 있어, **사진 캡처 방식**으로 변경했습니다.
- 이후 `requirements.txt` 파일을 수정하고, **GitHub에 푸시 후 재배포**하여 문제를 해결했습니다.

## 🎯 게임 진행 방식 및 랭킹 시스템

### 📌 게임 진행 방식
1. 유저가 카메라를 통해 손 모양을 촬영합니다.
2. **Teachable Machine**이 이미지를 분석하여 유저가 낸 가위/바위/보를 인식합니다.
3. AI가 랜덤하게 가위/바위/보를 선택하여 대결을 진행합니다.
4. 승/패/비김 결과에 따라 **몬스터의 MP(체력)**가 변동됩니다.
5. **5번의 대결**이 끝나면 최종 승리 횟수와 함께 **랭킹 시스템**에 반영됩니다.

### 📌 랭킹 시스템
- **승리 횟수가 많고, 남은 MP가 적을수록 높은 랭킹**을 차지하도록 설정했습니다.
- 같은 닉네임이 존재할 경우, **기존 점수보다 높은 기록만 업데이트**되도록 구현했습니다.
- 랭킹 데이터는 **CSV 파일**에 저장되어 이후에도 관리 및 분석이 용이합니다.

### 📌 유저 커스터마이징 기능
- **유저는 자신만의 닉네임을 설정**할 수 있어, 더욱 개성 있는 플레이가 가능합니다.
- 닉네임을 바탕으로 **다른 유저들과 랭킹을 경쟁**할 수 있습니다.

## 📂 프로젝트 구조
```
📁 가위바위보 몬스터 배틀
├── app.py          # 메인 애플리케이션 (Streamlit 기반)
├── eda.py          # 게임 데이터 관리 (랭킹 시스템)
├── game.py         # 가위바위보 이미지 인식 및 게임 로직
├── home.py         # 홈 화면 UI 구성
├── ml.py           # AI 모델 관련 (추후 개발 예정)
├── ranking.csv     # 사용자 승리 기록 저장 파일
├── requirements.txt # 프로젝트 의존성 파일
└── model/          # Teachable Machine에서 학습된 모델 파일 (keras_model.h5)
```

## 📢 기타 정보
- **사진 출처**: [Kaggle Rock Paper Scissors Dataset](https://www.kaggle.com/datasets/alexandredj/rock-paper-scissors-dataset)
- **블로그 주소**: [https://tbghdus.tistory.com/120](https://tbghdus.tistory.com/120)
- **개발자 이메일**: vhzkflfltm6@gmail.com
- **GitHub 저장소**: [https://github.com/qoeka98/paint-](https://github.com/qoeka98/paint-)



