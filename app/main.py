from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse, Response
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
import io
import time
from model import predict
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST

app = FastAPI(title="🐟 Fish Species Classifier API")

# Métriques Prometheus
PREDICTIONS_TOTAL = Counter(
    'fish_predictions_total',
    'Total number of predictions made',
    ['predicted_class']
)
PREDICTION_DURATION = Histogram(
    'fish_prediction_duration_seconds',
    'Time spent processing prediction',
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
)
PREDICTION_CONFIDENCE = Gauge(
    'fish_prediction_confidence',
    'Confidence of the last prediction',
    ['predicted_class']
)
ERRORS_TOTAL = Counter(
    'fish_prediction_errors_total',
    'Total number of prediction errors'
)

# Configuration CORS pour permettre les requêtes depuis le frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://10.40.0.20:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Bienvenue sur l'API de classification de poissons 🐠"}

@app.get("/metrics")
def metrics():
    """Endpoint pour exposer les métriques Prometheus"""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.post("/predict")
async def classify(file: UploadFile = File(...)):
    start_time = time.time()
    try:
        # Lecture de l'image envoyée
        image_bytes = await file.read()
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")

        # Prédiction
        label, confidence = predict(image)

        # Enregistrement des métriques
        duration = time.time() - start_time
        PREDICTIONS_TOTAL.labels(predicted_class=label).inc()
        PREDICTION_DURATION.observe(duration)
        PREDICTION_CONFIDENCE.labels(predicted_class=label).set(confidence)

        return JSONResponse({
            "prediction": label,
            "confidence": round(confidence * 100, 2)
        })

    except Exception as e:
        ERRORS_TOTAL.inc()
        raise HTTPException(status_code=500, detail=f"Erreur lors de la prédiction : {str(e)}")
