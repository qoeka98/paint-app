from tempfile import template
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
import cv2
from fastapi.templating import Jinja2Templates

from eda import run_eda

app = FastAPI()

templates = Jinja2Templates(directory="templates")

# 웹캠 활성화
cap = cv2.VideoCapture(0)

def generate_frames():
    """ 웹캠에서 프레임을 읽고 스트리밍 """
    while True:
        success, frame = cap.read()
        if not success:
            break
        _, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.get("/video_feed")
async def video_feed():
    """ 실시간 웹캠 스트리밍 엔드포인트 """
    return StreamingResponse(generate_frames(), media_type="multipart/x-mixed-replace; boundary=frame")


@app.get("/game")
async def game_page(request: Request):
    try:
        content = run_eda()
        return templates.TemplateResponse("page.html", {"request": request, "content": content, "title": "🎮 게임 페이지"})
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
