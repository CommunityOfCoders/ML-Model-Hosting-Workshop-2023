import sys
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
import mediapipe as mp
import cv2
import base64
from keypoint_classifier import KeyPointClassifier

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

mp_hands = mp.solutions.hands
# https://google.github.io/mediapipe/solutions/hands.html

hands = mp_hands.Hands(static_image_mode=True,
                       max_num_hands=1,
                       min_detection_confidence=0.7,)
keypoint_classifier = KeyPointClassifier(
    model_path='./model/gesture_model.tflite')
desc = {0: 'Scroll Down', 1: 'Scroll Up'}


def get_sign(img):
    img = cv2.flip(img, 1)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img.flags.writeable = False

    results = hands.process(img)
    img.flags.writeable = True
    hand_sign = -1
    landmark_list = []
    if results.multi_hand_landmarks is not None:
        for landmark in results.multi_hand_landmarks[0].landmark:
            landmark_list.append(landmark.x)
            landmark_list.append(landmark.y)
        hand_sign = keypoint_classifier(landmark_list=landmark_list)
        return hand_sign


@app.websocket('/get_gesture')
async def get_gesture(ws: WebSocket):
    await ws.accept()
    while True:
        data = await ws.receive()

        if data['text'] != 'null':
            face_bytes = bytes(str(data), 'utf-8')
            face_bytes = face_bytes[face_bytes.find(b'/9'):]
            face_img = base64.b64decode(face_bytes)

            np_img = np.frombuffer(face_img, np.uint8)
            cv_img = cv2.imdecode(np_img, cv2.IMREAD_COLOR)

            res = get_sign(cv_img)
            # print(res)
        else:
            continue
        if res is None:
            res = -1
        await ws.send_json({'gesture': str(res)})


@app.on_event('shutdown')
def close_objects():
    hands.close()
