import torch
from torchvision import transforms
from PIL import Image
from minio import Minio
import io, os

MODEL_PATH = "model.pt"
BUCKET = "models"

# Connexion MinIO (localhost)
minio_client = Minio(
    "minio:9000",
    access_key="minioadmin",
    secret_key="minioadmin",
    secure=False
)

# Téléchargement automatique du modèle depuis MinIO
if not os.path.exists(MODEL_PATH):
    minio_client.fget_object(BUCKET, "model.pt", MODEL_PATH)

# Chargement du modèle
model = torch.load(MODEL_PATH, map_location=torch.device("cpu"))
model.eval()

# Classes de poissons
CLASSES = ["Catfish", "Goldfish", "Mudfish", "Mullet", "Snakehead"]

# Transformation pour l’inférence
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                         std=[0.229, 0.224, 0.225])
])

def predict(image: Image.Image):
    tensor = transform(image).unsqueeze(0)
    with torch.no_grad():
        outputs = model(tensor)
        probs = torch.nn.functional.softmax(outputs[0], dim=0)
        pred_idx = probs.argmax().item()
        return CLASSES[pred_idx], probs[pred_idx].item()
