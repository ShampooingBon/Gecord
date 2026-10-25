
#!/bin/bash

set -e

# ==========================================
# Gecord - Préparation du projet iOS
# Pour iPhone et iPad
# Nécessite macOS, Xcode et Kivy-iOS
# ==========================================

APP_NAME="Gecord"

# Dossier du projet : celui où se trouve ce script
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Dossier de sortie du projet Xcode
OUTPUT_DIR="$PROJECT_DIR/${APP_NAME}-ios"

echo "===================================="
echo " Préparation de Gecord pour iOS"
echo "===================================="

# Vérifier que le système est macOS
if [[ "$(uname -s)" != "Darwin" ]]; then
    echo "ERREUR : la compilation iOS nécessite macOS et Xcode."
    exit 1
fi

# Vérifier les outils Apple
if ! command -v xcodebuild >/dev/null 2>&1; then
    echo "ERREUR : Xcode ou ses outils ne sont pas installés."
    exit 1
fi

# Vérifier le fichier principal
if [[ ! -f "$PROJECT_DIR/main.py" ]]; then
    echo "ERREUR : main.py est introuvable dans :"
    echo "$PROJECT_DIR"
    echo "Place le code principal de Gecord dans main.py"
    exit 1
fi

# Vérifier Kivy-iOS
if ! command -v toolchain >/dev/null 2>&1; then
    echo "ERREUR : la commande toolchain est introuvable."
    echo "Installe Kivy-iOS dans ton environnement Python."
    exit 1
fi

# Construire les dépendances Kivy pour iOS
echo "Construction des dépendances Kivy..."
toolchain build kivy

# Créer le projet Xcode s'il n'existe pas
if [[ ! -d "$OUTPUT_DIR" ]]; then
    echo "Création du projet Xcode..."
    toolchain create "$APP_NAME" "$PROJECT_DIR"
else
    echo "Le projet Xcode existe déjà."
    echo "Mise à jour du projet..."
    toolchain update "$OUTPUT_DIR"
fi

echo ""
echo "Préparation terminée."
echo "Projet Xcode : $OUTPUT_DIR"
echo ""
echo "Ouvre le fichier .xcodeproj dans Xcode."
echo "Configure la signature de l'application et teste"
echo "sur un simulateur ou un appareil iOS compatible."
