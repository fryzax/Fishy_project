from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from PIL import Image
import io
from app.model import predict

app = FastAPI(title="Fish Species Classifier API")

@app.get("/")
def root():
    return {"message": "Bienvenue sur l’API de classification de poissons 🐟"}

@app.post("/predict")
async def classify(file: UploadFile = File(...)):
    image_bytes = await file.read()
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")

    label, confidence = predict(image)

    return JSONResponse({
        "prediction": label,
        "confidence": round(confidence * 100, 2)
    })
