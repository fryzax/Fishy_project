# ===============================================
# Script : train_model.py
# Objectif : Entraîner un modèle CNN pour classifier les poissons
#            Les images sont récupérées depuis la table SQL
# Auteur : Mathieu + Kirsten
# ===============================================

import os
import io
import pymysql
from minio import Minio
from PIL import Image
from tqdm import tqdm
import torch
from torch import nn, optim
from torchvision import datasets, transforms, models
from torch.utils.data import DataLoader, random_split
from urllib.parse import urljoin
import mlflow
import mlflow.pytorch

# ============================================================
# 1️⃣ Configuration
# ============================================================

# Détection de l'environnement (local ou Docker)
# Si on tourne en local, on utilise localhost, sinon les noms de services Docker
import socket

def is_running_in_docker():
    """Détecte si le script tourne dans un conteneur Docker"""
    try:
        with open('/proc/1/cgroup', 'r') as f:
            return 'docker' in f.read()
    except:
        return False

IN_DOCKER = is_running_in_docker()

# MinIO configuration
MINIO_ENDPOINT = "minio:9000" if IN_DOCKER else "localhost:9000"
MINIO_ACCESS_KEY = "admin-user"
MINIO_SECRET_KEY = "admin-password"
BUCKET_NAME = "dataset-fish"
MODEL_BUCKET = "models"         # bucket où on sauvegarde les modèles

# MySQL configuration
MYSQL_HOST = "mysql" if IN_DOCKER else "localhost"
MYSQL_USER = "root"
MYSQL_PASSWORD = "root"
MYSQL_DB = "mlops"

# MLflow configuration
MLFLOW_TRACKING_URI = "http://mlflow:5000" if IN_DOCKER else "http://localhost:5001"
MLFLOW_EXPERIMENT_NAME = "fish_classification"

# Dossiers locaux pour le training
DATA_DIR = "data"
TRAIN_DIR = os.path.join(DATA_DIR, "train")

# Paramètres d'entraînement
EPOCHS = 20  # Augmenté pour un meilleur entraînement
BATCH_SIZE = 16
LEARNING_RATE = 0.001
IMG_SIZE = 224

print(f"🖥️  Environnement détecté: {'Docker' if IN_DOCKER else 'Local'}")

# ============================================================
# 2️⃣ Connexion MySQL, MinIO et MLflow
# ============================================================
print("🔌 Connexion à MySQL...")
conn = pymysql.connect(
    host=MYSQL_HOST,
    user=MYSQL_USER,
    password=MYSQL_PASSWORD,
    database=MYSQL_DB
)
cursor = conn.cursor()
print("✅ Connecté à MySQL")

print("🔌 Connexion à MinIO...")
minio_client = Minio(
    MINIO_ENDPOINT,
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=False
)

# Vérification des buckets
if not minio_client.bucket_exists(BUCKET_NAME):
    raise ValueError(f"Le bucket '{BUCKET_NAME}' n'existe pas sur MinIO.")
if not minio_client.bucket_exists(MODEL_BUCKET):
    minio_client.make_bucket(MODEL_BUCKET)
    print(f"✅ Bucket '{MODEL_BUCKET}' créé pour stocker les modèles.")

# Créer le bucket mlflow pour les artifacts MLflow
MLFLOW_BUCKET = "mlflow"
if not minio_client.bucket_exists(MLFLOW_BUCKET):
    minio_client.make_bucket(MLFLOW_BUCKET)
    print(f"✅ Bucket '{MLFLOW_BUCKET}' créé pour les artifacts MLflow.")

print("✅ Connecté à MinIO")

# ============================================================
# Configuration des credentials S3/MinIO pour MLflow
# ============================================================
print("🔌 Configuration des credentials MLflow pour MinIO...")
os.environ["AWS_ACCESS_KEY_ID"] = MINIO_ACCESS_KEY
os.environ["AWS_SECRET_ACCESS_KEY"] = MINIO_SECRET_KEY
os.environ["MLFLOW_S3_ENDPOINT_URL"] = f"http://minio:9000" if IN_DOCKER else "http://localhost:9000"
print("✅ Credentials configurés pour MLflow")

print("🔌 Configuration de MLflow...")
mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
mlflow.set_experiment(MLFLOW_EXPERIMENT_NAME)
print(f"✅ MLflow configuré : {MLFLOW_TRACKING_URI}")

# ============================================================
# 3️⃣ Lecture des images depuis la table SQL
# ============================================================
print("📊 Lecture des données depuis la table fish_data...")

# Récupérer UNIQUEMENT les images de train
cursor.execute("SELECT species_label, file_name, url_s3 FROM fish_data WHERE split = 'train'")
rows = cursor.fetchall()

print(f"✅ {len(rows)} images de training trouvées dans la base de données")

# ============================================================
# 4️⃣ Téléchargement des images depuis MinIO basé sur SQL
# ============================================================
print("📦 Téléchargement des images depuis MinIO (basé sur la table SQL)...")

os.makedirs(TRAIN_DIR, exist_ok=True)

for label, file_name, url_s3 in tqdm(rows, desc="Downloading images"):
    # Reconstituer le chemin dans MinIO : train/label/filename
    key = f"train/{label}/{file_name}"

    # Crée un dossier local par label
    label_dir = os.path.join(TRAIN_DIR, label)
    os.makedirs(label_dir, exist_ok=True)

    # Chemin complet de sortie
    local_path = os.path.join(label_dir, file_name)

    # Ne télécharger que si le fichier n'existe pas déjà
    if not os.path.exists(local_path):
        try:
            minio_client.fget_object(BUCKET_NAME, key, local_path)
        except Exception as e:
            print(f"⚠️  Erreur pour {key}: {e}")

cursor.close()
conn.close()

print("✅ Téléchargement terminé.")

# ============================================================
# 5️⃣ Préparation des données PyTorch
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
# 6️⃣ Construction du modèle CNN
# ============================================================

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Utilisation d'un modèle pré-entraîné (Transfer Learning)
model = models.resnet18(weights="IMAGENET1K_V1")
num_features = model.fc.in_features
model.fc = nn.Linear(num_features, len(dataset.classes))  # adapte à ton nb d'espèces
model = model.to(device)

criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE)

# ============================================================
# 7️⃣ Entraînement avec validation
# ============================================================
print("🚀 Début de l'entraînement...")

best_val_acc = 0.0
best_model_path = "best_model.pt"

# Démarrer une run MLflow
mlflow.start_run()

# Logger les hyperparamètres
mlflow.log_param("epochs", EPOCHS)
mlflow.log_param("batch_size", BATCH_SIZE)
mlflow.log_param("learning_rate", LEARNING_RATE)
mlflow.log_param("img_size", IMG_SIZE)
mlflow.log_param("model_architecture", "resnet18")
mlflow.log_param("num_classes", len(dataset.classes))
mlflow.log_param("train_size", len(train_dataset))
mlflow.log_param("val_size", len(val_dataset))

for epoch in range(EPOCHS):
    # Phase d'entraînement
    model.train()
    running_loss = 0.0
    for images, labels in tqdm(train_loader, desc=f"Epoch {epoch+1}/{EPOCHS} [Train]", leave=False):
        images, labels = images.to(device), labels.to(device)
        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()
        running_loss += loss.item()

    train_loss = running_loss / len(train_loader)

    # Phase de validation
    model.eval()
    val_loss = 0.0
    correct = 0
    total = 0

    with torch.no_grad():
        for images, labels in tqdm(val_loader, desc=f"Epoch {epoch+1}/{EPOCHS} [Val]", leave=False):
            images, labels = images.to(device), labels.to(device)
            outputs = model(images)
            loss = criterion(outputs, labels)
            val_loss += loss.item()

            _, predicted = torch.max(outputs.data, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()

    val_loss = val_loss / len(val_loader)
    val_accuracy = 100 * correct / total

    print(f"📊 Epoch {epoch+1}/{EPOCHS} - Train Loss: {train_loss:.4f} | Val Loss: {val_loss:.4f} | Val Acc: {val_accuracy:.2f}%")

    # Logger les métriques sur MLflow à chaque epoch
    mlflow.log_metric("train_loss", train_loss, step=epoch)
    mlflow.log_metric("val_loss", val_loss, step=epoch)
    mlflow.log_metric("val_accuracy", val_accuracy, step=epoch)

    # Sauvegarder le meilleur modèle
    if val_accuracy > best_val_acc:
        best_val_acc = val_accuracy
        torch.save(model.state_dict(), best_model_path)
        print(f"   ⭐ Nouveau meilleur modèle sauvegardé ! (Val Acc: {val_accuracy:.2f}%)")
        mlflow.log_metric("best_val_accuracy", best_val_acc)

print(f"✅ Entraînement terminé. Meilleure précision validation : {best_val_acc:.2f}%")

# ============================================================
# 8️⃣ Sauvegarde du meilleur modèle
# ============================================================

MODEL_PATH = "model_v1.pt"
# Copier le meilleur modèle vers le nom final
import shutil
import time
shutil.copy(best_model_path, MODEL_PATH)
print(f"💾 Meilleur modèle sauvegardé localement sous {MODEL_PATH} (Val Acc: {best_val_acc:.2f}%)")

# ============================================================
# 9️⃣ Logger le modèle sur MLflow
# ============================================================

print("📤 Enregistrement du modèle sur MLflow...")
try:
    # Logger le modèle PyTorch sur MLflow
    mlflow.pytorch.log_model(
        model,
        "model",
        registered_model_name="fish_classifier"
    )
    print("✅ Modèle enregistré sur MLflow")

    # Logger aussi le fichier .pt comme artifact
    mlflow.log_artifact(MODEL_PATH, "model_file")
    print("✅ Fichier .pt ajouté comme artifact MLflow")

except Exception as e:
    print(f"⚠️  Erreur lors de l'enregistrement sur MLflow : {e}")

# ============================================================
# 🔟 Upload du modèle vers MinIO
# ============================================================

try:
    # Utiliser un nom unique avec timestamp pour éviter les conflits
    timestamp = int(time.time())
    model_name = f"model_v1_{timestamp}.pt"

    # Logger le nom du modèle MinIO sur MLflow
    mlflow.log_param("minio_model_name", model_name)

    # Upload avec un nouveau nom pour éviter les deadlocks
    with open(MODEL_PATH, 'rb') as file_data:
        file_stat = os.stat(MODEL_PATH)
        minio_client.put_object(
            MODEL_BUCKET,
            model_name,
            file_data,
            file_stat.st_size,
        )
    print(f"✅ Modèle envoyé sur MinIO : bucket='{MODEL_BUCKET}', objet='{model_name}'")
except Exception as e:
    print(f"⚠️  Erreur lors de l'upload vers MinIO : {e}")
    print(f"   Le modèle reste disponible localement : {MODEL_PATH}")

# Terminer la run MLflow
mlflow.end_run()

print("🎉 Entraînement terminé avec succès !")
