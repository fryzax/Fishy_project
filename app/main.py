from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from PIL import Image
import io
from model import predict

app = FastAPI(title="🐟 Fish Species Classifier API")

@app.get("/")
def root():
    return {"message": "Bienvenue sur l’API de classification de poissons 🐠"}

@app.post("/predict")
async def classify(file: UploadFile = File(...)):
    try:
        # Lecture de l’image envoyée
        image_bytes = await file.read()
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")

        # Prédiction
        label, confidence = predict(image)

        return JSONResponse({
            "prediction": label,
            "confidence": round(confidence * 100, 2)
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la prédiction : {str(e)}")
