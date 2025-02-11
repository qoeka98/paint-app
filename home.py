import gradio as gr

def run_home():
    with gr.Blocks() as home_ui:
        gr.Markdown("## 가위바위보 몬스터 배틀")
        gr.Markdown("Gradio 기반으로 실행되는 가위바위보 게임 소개 페이지입니다!")
        gr.Image(value="./image/게임.png", label="게임 이미지")

    return home_ui
