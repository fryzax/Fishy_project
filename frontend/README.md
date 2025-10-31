# 🐟 Fishy Classifier Frontend

Un frontend **magnifique** et **drôle** pour classifier les espèces de poissons ! 🌊✨

## ✨ Features

- 🎨 **Design aquatique immersif** avec dégradé océan
- 🫧 **Bulles animées** qui montent à la surface
- 🐠 **Poissons qui nagent** à travers l'écran
- 📸 **Drag & Drop** d'images super fluide
- 🎯 **Affichage des résultats animé** avec confiance en %
- 🎓 **Fun facts** sur chaque espèce de poisson
- 📱 **Responsive design** pour mobile et desktop
- 🎉 **Animations et effets** partout !

## 🐟 Espèces Reconnues

- **Catfish** 🐱🐟 - Le poisson-chat avec ses barbillons
- **Gold Fish** 🐠 - Le poisson rouge classique
- **Mudfish** 🐟 - Le poisson capable de respirer hors de l'eau
- **Mullet** 🐡 - Le mulet qui saute haut
- **Snakehead** 🐍🐟 - Le poisson-serpent prédateur

## 🚀 Installation

```bash
# Installer les dépendances
npm install

# Lancer le serveur de développement
npm run dev

# Build pour production
npm run build
```

Le frontend sera disponible sur `http://localhost:3000`

## 📂 Structure du Projet

```
frontend/
├── src/
│   ├── components/
│   │   ├── Bubbles.jsx          # Animation des bulles
│   │   ├── SwimmingFish.jsx     # Poissons qui nagent
│   │   ├── ImageUploader.jsx    # Zone de drag & drop
│   │   └── ResultDisplay.jsx    # Affichage des résultats
│   ├── assets/
│   │   └── fish-images/         # 📸 METTEZ VOS PNG ICI !
│   ├── App.jsx                  # Composant principal
│   ├── main.jsx                 # Point d'entrée
│   └── index.css                # Styles globaux
├── public/
│   └── fish-icon.svg            # Favicon
├── index.html
├── package.json
├── vite.config.js
└── tailwind.config.js
```

## 🖼️ Où Mettre les Images de Poisson

Placez vos images PNG dans le dossier :
```
frontend/src/assets/fish-images/
```

Ensuite, importez-les dans les composants comme ceci :
```javascript
import catfishImg from './assets/fish-images/catfish.png';
```

## 🔌 Connexion avec le Backend

Dans `App.jsx`, remplacez le code mock par votre vraie API :

```javascript
// Actuellement (MOCK) :
const mockResult = {
  species: 'Catfish',
  confidence: 0.95
};

// À remplacer par (VRAI) :
const response = await axios.post('/api/predict', formData, {
  headers: {
    'Content-Type': 'multipart/form-data',
  },
});
setResult(response.data);
```

### Format attendu de l'API

```json
{
  "species": "Catfish",
  "confidence": 0.95
}
```

## 🎨 Personnalisation

### Couleurs
Modifiez les couleurs dans `tailwind.config.js` :
```javascript
colors: {
  ocean: {
    500: '#00a8ff', // Couleur principale
    // ...
  }
}
```

### Animations
Ajoutez des animations dans `tailwind.config.js` section `keyframes`

### Fun Facts
Ajoutez des faits marrants dans `ResultDisplay.jsx` :
```javascript
const fishFacts = {
  'Catfish': [
    'Your fun fact here! 🎉'
  ]
};
```

## 🎭 Easter Eggs

- Les poissons emoji nagent de droite à gauche et vice-versa
- Les bulles montent à des vitesses différentes
- Le message change selon la confiance du modèle
- Confetti animation quand un résultat apparaît !

## 🛠️ Technologies Utilisées

- **React 18** - Framework UI
- **Vite** - Build tool ultra rapide
- **Tailwind CSS** - Styling utility-first
- **Axios** - HTTP client pour l'API
- **Fredoka** - Police fun et ronde

## 📝 TODO pour Vous

- [ ] Ajouter vos PNG de poissons dans `src/assets/fish-images/`
- [ ] Connecter le backend en remplaçant le mock dans `App.jsx`
- [ ] Personnaliser les couleurs si besoin
- [ ] Ajouter plus de fun facts !
- [ ] Tester sur mobile

## 🎉 Have Fun!

Le frontend est prêt, il ne reste plus qu'à ajouter vos images et connecter le backend ! 🐠✨

---

Made with 💙 and lots of fish 🐟🐠🐡
