# ===============================================
# Script : generate_fish_data_table.py
# Objectif : Créer automatiquement une table SQL "fish_data"
#            à partir des images stockées sur MinIO
# Auteur : Mathieu + ChatGPT
# ===============================================

import pymysql
from minio import Minio
from urllib.parse import urljoin

# === 1. Configuration des connexions ===
# ---------------------------------------

# MinIO configuration
MINIO_ENDPOINT = "minio:9000"   # ⚠️ utilise le nom du conteneur dans Docker, pas localhost
MINIO_ACCESS_KEY = "admin-user"
MINIO_SECRET_KEY = "admin-password"
BUCKET_NAME = "dataset-fish"

# MySQL configuration
MYSQL_HOST = "mysql"  # ⚠️ idem, nom du conteneur Docker
MYSQL_USER = "root"
MYSQL_PASSWORD = "root"
MYSQL_DB = "mlops"

# === 2. Connexion à MinIO ===
# ----------------------------
minio_client = Minio(
    MINIO_ENDPOINT,
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=False  # car on est en local sans HTTPS
)

# Vérification du bucket
if not minio_client.bucket_exists(BUCKET_NAME):
    raise ValueError(f"❌ Le bucket '{BUCKET_NAME}' n’existe pas sur MinIO !")

# === 3. Connexion MySQL ===
# --------------------------
conn = pymysql.connect(
    host=MYSQL_HOST,
    user=MYSQL_USER,
    password=MYSQL_PASSWORD,
    database=MYSQL_DB
)
cursor = conn.cursor()

# === 4. Création de la table fish_data ===
# -----------------------------------------
create_table_query = """
CREATE TABLE IF NOT EXISTS fish_data (
    id INT AUTO_INCREMENT PRIMARY KEY,
    species_label VARCHAR(100) NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    url_s3 TEXT NOT NULL,
    insert_date DATETIME DEFAULT CURRENT_TIMESTAMP
);
"""
cursor.execute(create_table_query)
conn.commit()
print("✅ Table 'fish_data' vérifiée ou créée avec succès.")

# === 5. Parcours des objets MinIO ===
# ------------------------------------
objects = minio_client.list_objects(BUCKET_NAME, recursive=True)

insert_query = """
INSERT INTO fish_data (species_label, file_name, url_s3)
VALUES (%s, %s, %s)
"""

added = 0
for obj in objects:
    key = obj.object_name  # Ex: "train/Catfish/img_001.jpg"
    parts = key.split("/")

    # On cherche les fichiers sous le dossier "train/<label>/..."
    if len(parts) < 3 or parts[0].lower() != "train":
        continue  # On ignore les fichiers hors du dossier train/

    label = parts[1]        # ex: "Catfish"
    file_name = parts[-1]   # ex: "img_001.jpg"

    # URL publique (accès via le port 9000)
    url_s3 = urljoin(f"http://localhost:9000/{BUCKET_NAME}/", key)

    cursor.execute(insert_query, (label, file_name, url_s3))
    added += 1

conn.commit()
cursor.close()
conn.close()

print(f"✅ Insertion terminée : {added} images ajoutées dans fish_data.")
