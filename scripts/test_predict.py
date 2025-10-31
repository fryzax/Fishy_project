import argparse
import requests
import sys
from pathlib import Path


def main():
    p = argparse.ArgumentParser(description="Envoyer une image au endpoint /predict")
    p.add_argument("--image", "-i", required=False, help="Chemin vers l'image à envoyer")
    p.add_argument("--url", "-u", default="http://127.0.0.1:8000/predict", help="URL du endpoint")
    args = p.parse_args()

    img_path = args.image
    if not img_path:
        # tenter de trouver une image de test dans le repo
        test_dir = Path("D:/Fishy_project/FishImgDataset/test")
        if test_dir.exists():
            candidates = list(test_dir.rglob("*.jpg")) + list(test_dir.rglob("*.png"))
        else:
            candidates = []
        
        if not candidates:
            print("❌ Aucune image trouvée automatiquement. Passez --image /chemin/vers/image.jpg")
            sys.exit(1)
        img_path = str(candidates[0])
        print(f"✅ Utilisation de l'image trouvée: {img_path}")

    try:
        with open(img_path, "rb") as f:
            files = {"file": (Path(img_path).name, f, "image/jpeg")}
            resp = requests.post(args.url, files=files, timeout=10)

        print(f"📡 Status HTTP: {resp.status_code}")
        if resp.status_code == 200:
            result = resp.json()
            print(f"🐟 Prédiction: {result['prediction']}")
            print(f"📊 Confiance: {result['confidence']}%")
        else:
            print(f"❌ Erreur: {resp.text}")
    except requests.exceptions.ConnectionError:
        print("❌ Impossible de se connecter au serveur. Vérifiez qu'il tourne sur http://127.0.0.1:8000")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Erreur: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
