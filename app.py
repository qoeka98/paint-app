import gradio as gr
from eda import run_eda
from home import run_home
from ml import run_ml

def main():
    with gr.Blocks() as demo:
        gr.Markdown("# 📌 메뉴 선택")

        with gr.Tabs():
            with gr.Tab("🏠 홈"):
                run_home()
            with gr.Tab("🎮 게임"):
                run_eda()
            with gr.Tab("📚 앱 개발 과정"):
                run_ml()

    demo.launch(debug=True)

if __name__ == "__main__":
    main()
