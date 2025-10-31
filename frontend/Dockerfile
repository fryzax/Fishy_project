# Frontend Dockerfile pour React + Vite
FROM node:20-alpine

WORKDIR /app

# Copier les fichiers de dépendances
COPY package*.json ./

# Installer les dépendances
RUN npm install

# Copier tout le code source
COPY . .

# Exposer le port Vite
EXPOSE 3000

# Démarrer le serveur de développement Vite
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
