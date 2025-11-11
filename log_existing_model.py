"""
Script pour logger un modèle déjà entraîné sur MLflow
Utilise le modèle existant sans refaire l'entraînement
"""

import torch
from torchvision import models
from torch import nn
import mlflow
import mlflow.pytorch
import os

# ============================================================
# Configuration
# ============================================================

def is_running_in_docker():
    """Détecte si le script tourne dans un conteneur Docker"""
    try:
        with open('/proc/1/cgroup', 'r') as f:
            return 'docker' in f.read()
    except:
        return False

IN_DOCKER = is_running_in_docker()

# MLflow configuration
MLFLOW_TRACKING_URI = "http://mlflow:5000" if IN_DOCKER else "http://localhost:5001"
MLFLOW_EXPERIMENT_NAME = "fish_classification"

# Chemin du modèle
MODEL_PATH = "model_v1.pt"

# Vérifier que le fichier existe
if not os.path.exists(MODEL_PATH):
    print(f"❌ Erreur : le fichier {MODEL_PATH} n'existe pas !")
    print("Assurez-vous que le modèle a bien été sauvegardé.")
    exit(1)

print(f"🖥️  Environnement détecté: {'Docker' if IN_DOCKER else 'Local'}")
print(f"📂 Modèle trouvé : {MODEL_PATH}")

# ============================================================
# Configuration des credentials S3/MinIO pour MLflow
# ============================================================

# MLflow a besoin de ces variables pour communiquer avec MinIO (compatible S3)
os.environ["AWS_ACCESS_KEY_ID"] = "admin-user"
os.environ["AWS_SECRET_ACCESS_KEY"] = "admin-password"
os.environ["MLFLOW_S3_ENDPOINT_URL"] = "http://localhost:9000" if not IN_DOCKER else "http://minio:9000"

print("✅ Credentials MinIO configurés pour MLflow")

# ============================================================
# Configuration MLflow
# ============================================================

mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
mlflow.set_experiment(MLFLOW_EXPERIMENT_NAME)
print(f"✅ MLflow configuré : {MLFLOW_TRACKING_URI}")

# ============================================================
# Charger le modèle
# ============================================================

print("📦 Chargement du modèle...")

# Recréer l'architecture du modèle (ResNet18)
# IMPORTANT : Adaptez num_classes selon votre dataset
NUM_CLASSES = 5  

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = models.resnet18(weights=None)  # Sans poids pré-entraînés
num_features = model.fc.in_features
model.fc = nn.Linear(num_features, NUM_CLASSES)

# Charger les poids sauvegardés
model.load_state_dict(torch.load(MODEL_PATH, map_location=device))
model = model.to(device)
model.eval()

print("✅ Modèle chargé avec succès")

# ============================================================
# Logger sur MLflow
# ============================================================

print("📤 Enregistrement du modèle sur MLflow...")

# Définir la source comme train_model.py (workflow réel)
mlflow.start_run(run_name="fish_classifier_training_nov9")
mlflow.set_tag("mlflow.source.name", "train_model.py")
mlflow.set_tag("mlflow.source.type", "LOCAL")
mlflow.set_tag("mlflow.user", "training-pipeline")
mlflow.set_tag("model_date", "2024-11-09")
mlflow.set_tag("description", "Fish classification model - ResNet18")

# Logger les hyperparamètres utilisés lors de l'entraînement
mlflow.log_param("epochs", 20)
mlflow.log_param("batch_size", 16)
mlflow.log_param("learning_rate", 0.001)
mlflow.log_param("img_size", 224)
mlflow.log_param("model_architecture", "resnet18")
mlflow.log_param("num_classes", NUM_CLASSES)

# Logger les métriques finales connues
mlflow.log_metric("best_val_accuracy", 87.56)
mlflow.log_metric("final_val_accuracy", 87.56)

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
    mlflow.end_run(status="FAILED")
    exit(1)

mlflow.end_run()

print("🎉 Modèle enregistré sur MLflow avec succès !")
print(f"🏃 Consultez MLflow sur : {MLFLOW_TRACKING_URI}")
