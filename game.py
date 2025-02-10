import cv2
import tensorflow as tf
import numpy as np

# ✅ 웹캠 활성화
camera = cv2.VideoCapture(0)

def generate_frames():
    """ 웹캠 스트리밍을 위한 프레임 생성 """
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            _, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

# ✅ AI 모델 로드
model_path = "model/keras_model.h5"
model = tf.keras.models.load_model(model_path)
class_names = ["가위", "바위", "보"]

def predict_move(image):
    """ 가위바위보 예측 """
    img = cv2.resize(image, (224, 224))
    img = np.array(img, dtype=np.float32) / 255.0
    img = np.expand_dims(img, axis=0)
    prediction = model.predict(img)
    class_index = np.argmax(prediction)
    return class_names[class_index]
