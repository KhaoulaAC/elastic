#!/bin/bash

# Script pour importer le dashboard Kibana
# Ce script doit être exécuté après le démarrage de Kibana

KIBANA_URL="http://localhost:5601"
DASHBOARD_FILE="/vercel/sandbox/kibana/dashboard_firefox_builds.ndjson"

echo "🔍 Vérification de la connexion à Kibana..."
until curl -s "$KIBANA_URL/api/status" > /dev/null; do
    echo "⏳ En attente de Kibana..."
    sleep 5
done

echo "✅ Kibana est prêt!"

# Importer le dashboard
echo "📊 Importation du dashboard Firefox Build Monitoring..."
curl -X POST "$KIBANA_URL/api/saved_objects/_import?overwrite=true" \
  -H "kbn-xsrf: true" \
  --form file=@"$DASHBOARD_FILE"

echo ""
echo "✨ Dashboard importé avec succès!"
echo "🌐 Accédez à Kibana: $KIBANA_URL"
echo "📊 Dashboard: Firefox Build Monitoring Dashboard"
