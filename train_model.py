# ===============================================
# Script : train_model.py
# Objectif : Entraîner un modèle CNN pour classifier les poissons
# Auteur : Mathieu + ChatGPT
# ===============================================

import os
import io
from minio import Minio
from PIL import Image
from tqdm import tqdm
import torch
from torch import nn, optim
from torchvision import datasets, transforms, models
from torch.utils.data import DataLoader, random_split
from urllib.parse import urljoin

# ============================================================
# 1️⃣ Configuration
# ============================================================

# MinIO configuration
MINIO_ENDPOINT = "minio:9000"   # le service Docker
MINIO_ACCESS_KEY = "admin-user"
MINIO_SECRET_KEY = "admin-password"
BUCKET_NAME = "dataset-fish"
MODEL_BUCKET = "models"         # bucket où on sauvegarde les modèles

# Dossiers locaux pour le training
DATA_DIR = "data"
TRAIN_DIR = os.path.join(DATA_DIR, "train")

# Paramètres d'entraînement
EPOCHS = 5
BATCH_SIZE = 16
LEARNING_RATE = 0.001
IMG_SIZE = 224

# ============================================================
# 2️⃣ Connexion MinIO
# ============================================================
minio_client = Minio(
    MINIO_ENDPOINT,
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=False
)

# Vérification des buckets
if not minio_client.bucket_exists(BUCKET_NAME):
    raise ValueError(f"Le bucket '{BUCKET_NAME}' n’existe pas sur MinIO.")
if not minio_client.bucket_exists(MODEL_BUCKET):
    minio_client.make_bucket(MODEL_BUCKET)
    print(f"✅ Bucket '{MODEL_BUCKET}' créé pour stocker les modèles.")

# ============================================================
# 3️⃣ Téléchargement des images depuis MinIO
# ============================================================
print("📦 Téléchargement des images depuis MinIO...")

os.makedirs(TRAIN_DIR, exist_ok=True)

# On liste les objets du dossier train/
objects = minio_client.list_objects(BUCKET_NAME, prefix="train/", recursive=True)

for obj in tqdm(objects, desc="Downloading images"):
    key = obj.object_name  # Ex: train/Catfish/img001.jpg
    parts = key.split("/")
    if len(parts) < 3:
        continue
    label = parts[1]  # ex: "Catfish"
    file_name = parts[-1]

    # Crée un dossier local par label
    label_dir = os.path.join(TRAIN_DIR, label)
    os.makedirs(label_dir, exist_ok=True)

    # Chemin complet de sortie
    local_path = os.path.join(label_dir, file_name)

    # Téléchargement du fichier
    minio_client.fget_object(BUCKET_NAME, key, local_path)

print("✅ Téléchargement terminé.")

# ============================================================
# 4️⃣ Préparation des données PyTorch
# ============================================================

transform = transforms.Compose([
    transforms.Resize((IMG_SIZE, IMG_SIZE)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                         std=[0.229, 0.224, 0.225]),
])

dataset = datasets.ImageFolder(root=TRAIN_DIR, transform=transform)

# Split train/val
train_size = int(0.8 * len(dataset))
val_size = len(dataset) - train_size
train_dataset, val_dataset = random_split(dataset, [train_size, val_size])

train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)
val_loader = DataLoader(val_dataset, batch_size=BATCH_SIZE, shuffle=False)

print(f"📊 Dataset prêt : {len(train_dataset)} train / {len(val_dataset)} val images")

# ============================================================
# 5️⃣ Construction du modèle CNN
# ============================================================

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Utilisation d’un modèle pré-entraîné (Transfer Learning)
model = models.resnet18(weights="IMAGENET1K_V1")
num_features = model.fc.in_features
model.fc = nn.Linear(num_features, len(dataset.classes))  # adapte à ton nb d'espèces
model = model.to(device)

criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE)

# ============================================================
# 6️⃣ Entraînement
# ============================================================
print("🚀 Début de l'entraînement...")

for epoch in range(EPOCHS):
    model.train()
    running_loss = 0.0
    for images, labels in tqdm(train_loader, desc=f"Epoch {epoch+1}/{EPOCHS}"):
        images, labels = images.to(device), labels.to(device)
        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()
        running_loss += loss.item()
    print(f"📉 Epoch {epoch+1}/{EPOCHS} - Loss: {running_loss/len(train_loader):.4f}")

print("✅ Entraînement terminé.")

# ============================================================
# 7️⃣ Sauvegarde du modèle
# ============================================================

MODEL_PATH = "model_v1.pt"
torch.save(model.state_dict(), MODEL_PATH)
print(f"💾 Modèle sauvegardé localement sous {MODEL_PATH}")

# ============================================================
# 8️⃣ Upload du modèle vers MinIO
# ============================================================

minio_client.fput_object(MODEL_BUCKET, MODEL_PATH, MODEL_PATH)
print(f"✅ Modèle envoyé sur MinIO : bucket='{MODEL_BUCKET}', objet='{MODEL_PATH}'")

print("🎉 Entraînement terminé avec succès !")
