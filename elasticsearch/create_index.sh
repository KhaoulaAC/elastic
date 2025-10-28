#!/bin/bash

# Script pour créer l'index Elasticsearch avec le mapping approprié
# Ce script doit être exécuté après le démarrage d'Elasticsearch

ELASTICSEARCH_URL="http://localhost:9200"
INDEX_PATTERN="firefox-logs"

echo "🔍 Vérification de la connexion à Elasticsearch..."
until curl -s "$ELASTICSEARCH_URL" > /dev/null; do
    echo "⏳ En attente d'Elasticsearch..."
    sleep 5
done

echo "✅ Elasticsearch est prêt!"

# Supprimer l'ancien template s'il existe
echo "🗑️  Suppression de l'ancien template (si existant)..."
curl -X DELETE "$ELASTICSEARCH_URL/_index_template/firefox-logs-template" 2>/dev/null

# Créer le template d'index
echo "📝 Création du template d'index..."
curl -X PUT "$ELASTICSEARCH_URL/_index_template/firefox-logs-template" \
  -H 'Content-Type: application/json' \
  -d @/vercel/sandbox/elasticsearch/mapping.json

echo ""
echo "✅ Template créé avec succès!"

# Vérifier le template
echo "🔍 Vérification du template..."
curl -X GET "$ELASTICSEARCH_URL/_index_template/firefox-logs-template?pretty"

echo ""
echo "✨ Configuration terminée!"
echo "📊 Les index firefox-logs-* utiliseront automatiquement ce mapping"
