#!/bin/bash

# Aller dans le répertoire du script (important pour cron)
cd "$(dirname "$0")"

# URL de la page contenant les données
URL="https://www.investing.com/indices/eu-stoxx50"

# User-Agent pour éviter les blocages
html=$(curl -s -A "Mozilla/5.0" "$URL")

# Extraction du prix
price=$(echo "$html" | grep -oP '(?<="last":)[0-9]+(\.[0-9]+)?' | head -n 1)

# Fichier CSV de destination
CSV_FILE="eurostoxx50_data.csv"

# Format de date lisible
current_time=$(date '+%Y-%m-%d %H:%M:%S')

# Ajout ou erreur
if [ -z "$price" ]; then
    echo "$current_time ❌ ERREUR : Impossible de récupérer le prix." >> scraper.log
else
    echo "$current_time, Eurostoxx 50, $price" >> "$CSV_FILE"
    echo "$current_time ✅ Prix ajouté au fichier CSV : $price" >> scraper.log
fi
