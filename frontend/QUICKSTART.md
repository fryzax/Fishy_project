# 🚀 Quick Start Guide

## Installation Rapide

```bash
# Se placer dans le dossier frontend
cd frontend

# Installer les dépendances
npm install

# Lancer le serveur de développement
npm run dev
```

Le site sera accessible sur **http://localhost:3000** 🌊

## 🎨 Ce qui a été intégré

### ✅ Images de Poissons Utilisées

- **bubble.png** → Bulles animées qui montent 🫧
- **clown.png** → Poisson clown qui nage 🐠
- **bar.png** → Bar qui traverse l'écran
- **espadon.png** → Espadon rapide
- **requin.png** → Requin menaçant
- **leviator.png** → Leviator légendaire
- **poissonmoche.png** → Utilisé pour Catfish dans les résultats
- **kraken.png** → 🦑 **EASTER EGG SECRET !**

### 🎮 Easter Egg Kraken

Il y a **5% de chance** à chaque upload qu'un KRAKEN apparaisse ! 🌊

Pour le tester plus facilement, changez la ligne dans `App.jsx:37` :
```javascript
if (krakenChance < 0.05) {  // 5% chance
```
en
```javascript
if (krakenChance < 0.50) {  // 50% chance (pour debug)
```

## 🗺️ Mapping des Images

Dans `ResultDisplay.jsx`, les espèces sont mappées comme suit :
```javascript
const fishImages = {
  'Catfish': poissonMocheImg,      // Le poisson moche 😂
  'Gold Fish': clownImg,            // Poisson clown coloré
  'Mudfish': barImg,                // Bar classique
  'Mullet': espadonImg,             // Espadon élégant
  'Snakehead': requinImg,           // Requin dangereux
  'default': leviatorImg            // Leviator si inconnu
};
```

**Si vous voulez changer le mapping**, éditez simplement ces lignes !

## 🎯 Comment Connecter au Backend

Dans `App.jsx`, ligne 24-50, remplacez le MOCK :

```javascript
// ACTUELLEMENT (MOCK)
const mockResult = {
  species: 'Catfish',
  confidence: 0.95
};

// PAR (VRAI)
const response = await axios.post('/api/predict', formData, {
  headers: {
    'Content-Type': 'multipart/form-data',
  },
});
setResult(response.data);
```

## 🎨 Effets Visuels

1. **Bulles** : 20 vraies images de bulles qui montent
2. **Poissons qui nagent** : 5 poissons PNG qui traversent l'écran
3. **Drag & Drop** : Zone interactive avec hover
4. **Confetti** : Animation quand un résultat arrive
5. **Glassmorphism** : Effet verre sur les cartes
6. **Wiggle** : Les poissons bougent légèrement
7. **Kraken** : Easter egg dramatique !

## 🐛 Debug

Si les images ne s'affichent pas :
1. Vérifiez que toutes les images sont bien dans `src/assets/fish-images/`
2. Vérifiez la console du navigateur (F12)
3. Relancez le serveur : `npm run dev`

## 📦 Build pour Production

```bash
npm run build
```

Les fichiers seront dans le dossier `dist/`

---

**Amusez-vous bien ! 🐟🐠🐡🦑**
