import base64
import io
import numpy
from pydantic import BaseModel
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
from tflite_runtime.interpreter import Interpreter

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_from_b64(b64_string):    
    face_bytes = bytes(b64_string, 'utf-8')
    face_bytes = face_bytes[face_bytes.find(b'/9'):]
    im = Image.open(io.BytesIO(base64.b64decode(face_bytes)))
    im = im.resize((128,128))
    im=numpy.array(im).astype(numpy.float32)
    im=im/255.0
    im=numpy.expand_dims(im, axis=0)
    return im

class req_image(BaseModel):
    img: str

@app.post('/plant_disease')
async def get_disease(image: req_image):
    b64_image = image.img
    in_image = get_from_b64(b64_string=b64_image)
    model = Interpreter('./model/beta_plant_disease.tflite')
    model.allocate_tensors()
    input_details=model.get_input_details()
    output_details=model.get_output_details()

    model.set_tensor(input_details[0]['index'], in_image)
    model.invoke()

    prediction=model.get_tensor(output_details[0]['index'])
    with open('./model/labels.txt') as lfile:
            for line in lfile.readlines():
                    if prediction.argmax() == int(line.split()[0]):
                            resp={'plant':line.split()[1], 'disease':line.split()[2]}
    
    return resp