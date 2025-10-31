# 🐟 Fish Classification - MLOps Project

Projet de classification d'images de poissons utilisant **PyTorch ResNet18** avec un pipeline MLOps complet (MinIO + MySQL + Docker) et une interface web interactive.

## 📊 Résultats

- **Classes :** 5 espèces (Catfish, Gold Fish, Mudfish, Mullet, Snakehead)
- **Dataset :** 1306 images (1045 train + 261 test)
- **Modèle :** ResNet18 (transfer learning)
- **Validation Accuracy :** 84.21% (meilleur modèle)
- **Test Accuracy :** ~70-100% selon échantillons
- **API REST :** FastAPI pour prédictions en temps réel
- **Frontend :** React + Vite avec animations aquatiques

## 🚀 Démarrage rapide

### Option A : Tout démarrer en une commande (Recommandé 🎯)

```bash
# Démarrer TOUTE l'application (infra + API + frontend)
docker-compose up -d minio mysql phpmyadmin mlflow fish_api frontend

# Accéder à l'application web
open http://localhost:3000
```

✨ **Le lendemain, rallumer tout :**
```bash
docker-compose up -d
```

### Option B : Démarrage étape par étape

#### 1. Infrastructure de base

```bash
# Infrastructure + interfaces web
docker-compose up -d minio mysql phpmyadmin mlflow
```

#### 2. Pipeline d'entraînement du modèle

```bash
# Lancer le pipeline d'entraînement
docker-compose up --build extraction training
```

Cette commande va automatiquement :
- ✅ Démarrer MinIO et MySQL
- ✅ Attendre que les services soient **healthy** (prêts)
- ✅ Lancer `extraction` : créer la table SQL et extraire les métadonnées depuis MinIO
- ✅ Attendre que extraction soit **terminé avec succès**
- ✅ Lancer `training` : télécharger les images et entraîner le modèle (20 epochs)

#### 3. API et Frontend

```bash
# Démarrer l'API et le Frontend
docker-compose up -d fish_api frontend
```

### 4. Tester le modèle (script Python)

```bash
docker-compose up --build predict
```

⚠️ **Important :** Toujours utiliser `--build` après avoir modifié le code Python pour forcer la reconstruction de l'image Docker.

### 5. Interfaces web

| Service | URL | Identifiants |
|---------|-----|--------------|
| **Frontend React** | http://localhost:3000 | - |
| **API FastAPI** | http://localhost:8000 | - |
| MinIO Console | http://localhost:9001 | `admin-user` / `admin-password` |
| phpMyAdmin | http://localhost:8080 | `root` / `root` |
| MLflow | http://localhost:5001 | - |

## 🏗️ Architecture

```
┌──────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────┐
│  MinIO   │────▶│  Extraction  │────▶│    MySQL     │────▶│   Training   │────▶│  MinIO   │
│ (images) │     │     SQL      │     │ (fish_data)  │     │   (model)    │     │ (model)  │
└──────────┘     └──────────────┘     └──────────────┘     └──────────────┘     └──────────┘
                                               │                                       │
                                               └──────────────────┐                    │
                                                                  ▼                    ▼
                                                            ┌──────────────┐     ┌──────────┐
                                                            │   Predict    │────▶│  Results │
                                                            │   (test)     │     │          │
                                                            └──────────────┘     └──────────┘
                                                                                       │
                                                                                       ▼
                                                            ┌──────────────────────────────┐
                                                            │   FastAPI REST API           │
                                                            │   POST /predict              │
                                                            └──────────────────────────────┘
                                                                       │
                                                                       ▼
                                                            ┌──────────────────────────────┐
                                                            │   React Frontend (Vite)      │
                                                            │   - Upload d'images          │
                                                            │   - Animations aquatiques    │
                                                            │   - Affichage résultats      │
                                                            └──────────────────────────────┘
```

## 📁 Structure du projet

```
.
├── docker-compose.yml           # Orchestration des services
├── Dockerfile                   # Image Python pour les scripts
├── requirements.txt             # Dépendances Python (torch, minio, pymysql, etc.)
├── extraction_creation_sql.py   # Création table + extraction depuis MinIO
├── train_model.py               # Entraînement du modèle ResNet18 (20 epochs)
├── predict.py                   # Prédiction sur images de test
├── app/
│   └── main.py                  # API FastAPI avec endpoint /predict
├── frontend/                    # Application React + Vite
│   ├── src/
│   │   ├── App.jsx              # Composant principal avec upload
│   │   ├── components/          # Composants UI (Bubbles, SwimmingFish, etc.)
│   │   └── assets/
│   │       └── fish-images/     # Images PNG pour le frontend
│   ├── package.json             # Dépendances npm
│   └── vite.config.js           # Configuration Vite avec proxy
├── FishImgDataset/              # Dataset local (backup)
│   ├── train/                   # 1045 images d'entraînement
│   │   ├── Catfish/
│   │   ├── Gold Fish/
│   │   ├── Mudfish/
│   │   ├── Mullet/
│   │   └── Snakehead/
│   └── test/                    # 261 images de test
│       ├── Catfish/
│       ├── Gold Fish/
│       ├── Mudfish/
│       ├── Mullet/
│       └── Snakehead/
└── model_v1_1761836094.pt       # Modèle entraîné (versionné avec Git LFS)
```

## 🔄 Fonctionnement du pipeline

### 1. Service `extraction`
- Se connecte à MinIO (bucket `dataset-fish`)
- Crée la table `fish_data` avec le schéma suivant :
  - `id`, `species_label`, `file_name`, `url_s3`, `split` (train/test), `insert_date`
- Supprime les données existantes (prévention doublons)
- Parcourt les images dans `train/` et `test/`
- Insère les métadonnées dans MySQL avec le champ `split`

### 2. Service `training`  
- **Attend** que `extraction` soit terminé avec succès
- Récupère uniquement les images `WHERE split = 'train'` depuis MySQL
- Télécharge les images depuis MinIO
- Applique un split 80/20 train/validation
- Entraîne un modèle **ResNet18** (transfer learning) pendant **20 epochs**
- Calcule à chaque epoch : train loss, validation loss, validation accuracy
- Sauvegarde le meilleur modèle (meilleure val accuracy)
- Upload le modèle dans MinIO (bucket `models`) avec timestamp : `model_v1_{timestamp}.pt`

### 3. Service `predict`
- Télécharge le modèle entraîné depuis MinIO
- Récupère 10 images aléatoires `WHERE split = 'test'` depuis MySQL
- Fait des prédictions et affiche les résultats avec confiance
- **Pas de data leakage** : teste uniquement sur le test set

### 4. Service `fish_api` (FastAPI)
- API REST pour prédictions en temps réel
- Endpoint `POST /predict` : accepte une image (multipart/form-data)
- Télécharge le modèle depuis MinIO au démarrage
- Retourne la prédiction et le score de confiance en JSON
- CORS activé pour le frontend (port 3000)

### 5. Frontend React + Vite
- Interface web interactive avec thème aquatique
- Upload d'images par glisser-déposer ou sélection
- Animations de bulles et poissons
- Affichage des résultats avec images et confiance
- Easter egg Kraken (20 clics sur le titre)
- Proxy Vite vers l'API (port 8000)

## 🔒 Anti-cheating measures

Le code implémente plusieurs mesures pour éviter le data leakage :

1. **Split train/test dans la base de données** : champ `split` dans `fish_data`
2. **Training sur train uniquement** : `SELECT ... WHERE split = 'train'`
3. **Validation split** : 80% train, 20% validation sur les données d'entraînement
4. **Test sur test uniquement** : `SELECT ... WHERE split = 'test'` dans predict.py
5. **Meilleur modèle basé sur validation accuracy** : évite l'overfitting

## ⚙️ Dépendances automatiques (healthcheck)

Le `docker-compose.yml` gère automatiquement les dépendances :

```yaml
training:
  depends_on:
    minio:
      condition: service_healthy      # MinIO doit être prêt
    mysql:
      condition: service_healthy      # MySQL doit être prêt
    extraction:
      condition: service_completed_successfully  # extraction doit avoir réussi
```

## 🔧 Configuration

### Paramètres d'entraînement (train_model.py)

```python
EPOCHS = 20              # Nombre d'époques
BATCH_SIZE = 16         # Taille des batchs
LEARNING_RATE = 0.001   # Taux d'apprentissage
IMG_SIZE = 224          # Taille des images (ResNet18)
```

### Connexions

**MinIO :**
- Endpoint: `minio:9000`
- Access Key: `admin-user`
- Secret Key: `admin-password`
- Buckets: `dataset-fish`, `models`

**MySQL :**
- Host: `mysql`
- User: `root`
- Password: `root`
- Database: `mlops`
- Table: `fish_data`

## 📈 Performances du modèle

### Training metrics (exemple)
```
Epoch 20/20:
  Train Loss: 0.2847
  Val Loss: 0.5234
  Val Accuracy: 84.21% ⭐ (meilleur modèle)
```

### Test results
- Précision variable selon les échantillons : 70-100%
- Confusions principales : 
  - Mudfish ⟷ Catfish
  - Snakehead ⟷ Catfish
- Bonne confiance sur prédictions correctes (>90%)

## 🐛 Troubleshooting

### Erreur "cryptography package is required"
✅ Résolu : `cryptography` ajouté dans `requirements.txt`

### Message "model_v1.pt téléchargé" au lieu du bon nom
❌ **Problème :** Docker utilise une ancienne image en cache
✅ **Solution :** Toujours utiliser `--build` :
```bash
docker-compose up --build predict
```

### Données dupliquées dans MySQL
✅ Résolu : `DELETE FROM fish_data` avant insertion dans extraction

### Le modèle "triche" sur les données de test
✅ Résolu : 
- Ajout du champ `split` dans la table
- Training sur `split = 'train'` uniquement
- Predict sur `split = 'test'` uniquement

## 🧹 Nettoyage

```bash
# Arrêter tous les conteneurs
docker-compose down

# Supprimer aussi les volumes (⚠️ efface les données)
docker-compose down -v

# Nettoyer les images Docker
docker system prune -a
```

## 📝 Notes techniques

- **Transfer Learning :** Utilisation des poids pré-entraînés IMAGENET1K_V1
- **Optimiseur :** Adam avec LR=0.001
- **Loss :** CrossEntropyLoss
- **Data Augmentation :** RandomHorizontalFlip, Normalize
- **Model Versioning :** Timestamp automatique dans le nom du modèle
- **Checkpoint :** Sauvegarde du meilleur modèle basé sur validation accuracy

## 🎯 Fonctionnalités

- [x] Pipeline MLOps complet (extraction, training, predict)
- [x] Versioning du modèle avec Git LFS
- [x] API REST FastAPI pour prédictions en temps réel
- [x] Frontend React avec interface interactive
- [x] Animations et thème aquatique
- [x] CORS et proxy configurés
- [ ] Intégration MLflow pour tracking des expériences
- [ ] Data augmentation plus avancée
- [ ] Test sur l'ensemble complet du test set
- [ ] Matrice de confusion et métriques détaillées
- [ ] CI/CD avec GitHub Actions

## 🛠️ Technologies utilisées

**Backend & MLOps:**
- Python 3.10
- PyTorch 2.9.0 (ResNet18)
- FastAPI (API REST)
- MinIO (stockage S3-compatible)
- MySQL 8.0 (métadonnées)
- Docker & Docker Compose
- Git LFS (versioning modèle)

**Frontend:**
- React 18.2.0
- Vite 5.0.8
- Axios (HTTP client)
- Tailwind CSS (styling)
