#!/bin/bash

# URL de la page contenant les données (par exemple Investing.com pour Eurostoxx 50)
URL="https://www.investing.com/indices/eu-stoxx50"

# Récupération du prix
html=$(curl -s -A "Mozilla/5.0" "$URL")
echo "HTML récupéré : $html"  # Message de débogage

price=$(echo "$html" | grep -oP '(?<="last":)[0-9]+(\.[0-9]+)?' | head -n 1)

# Vérification et ajout des données dans le fichier CSV
if [ -z "$price" ]; then
    echo "Erreur : Impossible de récupérer le prix."
else
    echo "$(date), Eurostoxx 50, $price" >> eurostoxx50_data.csv
    echo "Prix ajouté au fichier CSV."
fi
