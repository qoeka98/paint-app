import os
import sys
import cv2
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse
from eda import run_eda
from home import run_home
from ml import run_ml

app = FastAPI()

# 📌 현재 경로 추가 (모듈 임포트 충돌 방지)
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 🔹 `templates` 폴더가 없으면 자동 생성
if not os.path.exists("templates"):
    os.makedirs("templates")

# 🔹 `static` 폴더가 없으면 자동 생성
if not os.path.exists("static"):
    os.makedirs("static")

# 🔹 Jinja2 템플릿 사용 설정
templates = Jinja2Templates(directory="templates")

# 🔹 정적 파일 제공 (CSS, JS 등)
app.mount("/static", StaticFiles(directory="static"), name="static")

# ✅ 웹캠 스트리밍을 위한 OpenCV 초기화
camera = cv2.VideoCapture(0)  # 기본 웹캠 사용

# ✅ 웹캠 스트리밍을 위한 프레임 생성 함수
def generate_frames():
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            _, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

# ✅ 웹캠 스트리밍 API
@app.get("/video_feed")
def video_feed():
    return StreamingResponse(generate_frames(), media_type="multipart/x-mixed-replace; boundary=frame")

# 🔸 루트 경로
@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# 🔸 홈 페이지 (🏠)
@app.get("/home")
async def home_page(request: Request):
    try:
        content = run_home()  # run_home() 함수 실행 후 content 반환
        return templates.TemplateResponse("page.html", {"request": request, "content": content, "title": "🏠 홈 페이지"})
    except Exception as e:
        return {"error": str(e)}

# 🔸 게임 페이지 (🎮)
@app.get("/game")
async def game_page(request: Request):
    try:
        content = run_eda()  # EDA 실행 후 반환된 결과를 content로 사용
        return templates.TemplateResponse("page.html", {"request": request, "content": content, "title": "🎮 게임 페이지"})
    except Exception as e:
        return {"error": str(e)}

# 🔸 앱 개발 과정 페이지
@app.get("/app_dev")
async def app_dev_page(request: Request):
    try:
        content = run_ml()  # run_ml() 함수 실행 후 content 반환
        return templates.TemplateResponse("page.html", {"request": request, "content": content, "title": "앱 개발 과정"})
    except Exception as e:
        return {"error": str(e)}

# 🔸 FastAPI 실행 (uvicorn)
if __name__ == "__main__":
    import uvicorn
    print("📢 FastAPI 서버 실행 중...")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
