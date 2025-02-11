import pandas as pd
import os
import gradio as gr
from game import run_game  # 게임 실행 함수

def run_eda():
    csv_file = "win_records.csv"
    if not os.path.exists(csv_file):
        pd.DataFrame(columns=["이름", "시간", "승리 횟수", "몬스터 MP"]).to_csv(csv_file, index=False)
    return pd.read_csv(csv_file)

def update_ranking(name, mp):
    win_df = run_eda()
    filtered_df = win_df[win_df["몬스터 MP"] == mp].sort_values(by="시간").reset_index(drop=True)
    if not filtered_df.empty:
        rank_info = filtered_df.head(5).to_string(index=False)
        return f"🏆 몬스터 MP {mp} 랭킹\n{rank_info}"
    return "⚠️ 아직 등록된 기록이 없습니다."

def game_interface():
    win_df = run_eda()
    user_name = "Player"
    monster_mp_options = [30, 50, 80]

    with gr.Blocks() as demo:
        gr.Markdown("# 🎮 가위바위보 몬스터 배틀")
        gr.Markdown("## 게임 설정")
        gr.Markdown("⚠️ 주의! 중복된 닉네임을 사용할 경우 순위가 변동될 수 있습니다. 자신만의 개성 넘치는 닉네임을 설정하세요!")

        user_name_input = gr.Textbox(value=user_name, label="🔹 닉네임 입력")
        monster_mp_choice = gr.Radio(monster_mp_options, label="🎭 몬스터 MP 선택", value=50)
        save_button = gr.Button("닉네임 및 MP 설정 저장")
        ranking_display = gr.Textbox(label="🏆 랭킹 정보", interactive=False)

        # 랭킹 업데이트 버튼 이벤트
        save_button.click(update_ranking, inputs=[user_name_input, monster_mp_choice], outputs=ranking_display)

        gr.Markdown("## 🎮 게임 시작")
        start_button = gr.Button("게임 시작")

        # 🎮 게임 실행 버튼 (게임을 실행하고 결과를 출력)
        game_output = gr.Textbox(label="게임 결과", interactive=False)
        
        def start_game():
            result = run_game()  # 🛠 run_game() 함수에서 문자열을 반환하도록 수정 필요
            return result

        start_button.click(start_game, outputs=game_output)

    demo.launch(debug=True)

# 🚀 실행
if __name__ == "__main__":
    game_interface()
