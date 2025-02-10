from fastapi import FastAPI
from fastapi.responses import HTMLResponse, StreamingResponse
import uvicorn
import cv2
from eda import get_eda_page
from home import get_home_page
from ml import get_ml_page
from game import generate_frames

app = FastAPI()

# ✅ 웹캠 스트리밍 API
@app.get("/video_feed")
def video_feed():
    return StreamingResponse(generate_frames(), media_type="multipart/x-mixed-replace; boundary=frame")

# 🔹 **홈 화면 API**
@app.get("/", response_class=HTMLResponse)
def home():
    return get_home_page()

# 🔹 **게임 화면 API**
@app.get("/game", response_class=HTMLResponse)
def game():
    return get_eda_page()

# 🔹 **앱 개발 과정 API**
@app.get("/ml", response_class=HTMLResponse)
def ml():
    return get_ml_page()

# ✅ FastAPI 실행
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
