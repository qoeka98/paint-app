import gradio as gr

def run_home():
    title = "🔥 가위바위보 몬스터 배틀 🔥"
    subtitle = "🛡️ 최강의 가위바위보 전사가 되어 몬스터를 쓰러뜨리세요!"
    welcome_msg = "🎮 **환영합니다!** 가위바위보 스킬을 활용하여 강력한 몬스터와 맞서 싸우세요!"
    ranking_msg = "🏆 **누가 더 빠르게 몬스터를 처치할 수 있을까요?** 랭킹을 통해 최강자를 확인하세요!"
    image_path = "image/게임.png"

    return title, subtitle, welcome_msg, ranking_msg, image_path

iface = gr.Interface(
    fn=run_home,
    inputs=[],
    outputs=[
        gr.Markdown(),  # 🔥 타이틀
        gr.Markdown(),  # 🛡️ 서브타이틀
        gr.Markdown(),  # 🎮 환영 메시지
        gr.Markdown(),  # 🏆 랭킹 안내
        gr.Image(),     # 🖼️ 게임 이미지
    ],
    title="가위바위보 몬스터 배틀",
    description="**Gradio 기반으로 실행되는 가위바위보 게임 소개 페이지입니다!**"
)

# 실행
if __name__ == "__main__":
    iface.launch(debug=True)
