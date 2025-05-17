# ---------- Frontend ----------
FROM node:24-slim AS frontend

WORKDIR /app/frontend

COPY frontend/package.json ./

RUN npm install

COPY frontend/ ./

EXPOSE 5173

# (optionnel) build si nécessaire
# RUN npm run build

# ---------- Backend ----------
FROM python:3.11-slim AS backend

# Dépendances système
RUN apt-get update && apt-get install -y \
    build-essential \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    libgl1 \
    libcairo2 \
    pkg-config \
    python3-dev \
    libfreetype6-dev \
    libpng-dev \
    libffi-dev \
    libxml2-dev \
    libxslt1-dev \
    libjpeg-dev \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Dossier de travail
WORKDIR /app

# Installer les dépendances Python
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN pip install numpy==1.26.4

# Copier le code backend
COPY backend/ ./backend

# Copier les autres ressources
COPY 3D_models/ ./3D_models/
COPY floorplan_dataset/ ./floorplan_dataset/
COPY textures/ ./textures/
COPY checkpoints/ ./checkpoints/

# Exposer le port backend
EXPOSE 8000

# Commande de démarrage
CMD ["python", "backend/__main__.py"]
