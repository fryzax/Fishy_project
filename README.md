# 🐟 Fish Classification - MLOps Project

Projet de classification d'images de poissons utilisant **PyTorch ResNet18** avec un pipeline MLOps complet (MinIO + MySQL + Docker).

## 📊 Résultats

- **Classes :** 5 espèces (Catfish, Gold Fish, Mudfish, Mullet, Snakehead)
- **Dataset :** 1306 images (1045 train + 261 test)
- **Modèle :** ResNet18 (transfer learning)
- **Validation Accuracy :** 84.21% (meilleur modèle)
- **Test Accuracy :** ~70-100% selon échantillons

## 🚀 Démarrage rapide

### 1. Démarrer l'infrastructure et lancer le pipeline complet

```bash
# Infrastructure + interfaces web
docker-compose up -d minio mysql phpmyadmin mlflow

# Puis lancer le pipeline d'entraînement
docker-compose up --build extraction training
```

Cette commande va automatiquement :
- ✅ Démarrer MinIO et MySQL
- ✅ Attendre que les services soient **healthy** (prêts)
- ✅ Lancer `extraction` : créer la table SQL et extraire les métadonnées depuis MinIO
- ✅ Attendre que extraction soit **terminé avec succès**
- ✅ Lancer `training` : télécharger les images et entraîner le modèle (20 epochs)

### 2. Tester le modèle entraîné

```bash
# Important : toujours rebuilder après modifications de code
docker-compose up --build predict
```

### 3. Commandes individuelles

```bash
# Uniquement l'extraction SQL
docker-compose up --build extraction

# Uniquement le training (nécessite que extraction ait été lancé avant)
docker-compose up --build training

# Lancer une prédiction avec rebuild
docker-compose up --build predict
```

⚠️ **Important :** Toujours utiliser `--build` après avoir modifié le code Python pour forcer la reconstruction de l'image Docker.

### 4. Interfaces web

| Service | URL | Identifiants |
|---------|-----|--------------|
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
└── FishImgDataset/              # Dataset local (backup)
    ├── train/                   # 1045 images d'entraînement
    │   ├── Catfish/
    │   ├── Gold Fish/
    │   ├── Mudfish/
    │   ├── Mullet/
    │   └── Snakehead/
    └── test/                    # 261 images de test
        ├── Catfish/
        ├── Gold Fish/
        ├── Mudfish/
        ├── Mullet/
        └── Snakehead/
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

## 🎯 Prochaines améliorations

- [ ] Intégration MLflow pour tracking des expériences
- [ ] API REST pour prédictions en temps réel
- [ ] Data augmentation plus avancée
- [ ] Test sur l'ensemble complet du test set (pas seulement 10 images)
- [ ] Matrice de confusion et métriques détaillées
- [ ] CI/CD avec GitHub Actions
