#!/bin/bash

# Script de démarrage automatique du projet ELK Firefox
# Ce script lance tous les composants dans le bon ordre

set -e

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║     🦊 PROJET ELK - MONITORING DES BUILDS FIREFOX 🦊          ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Couleurs pour l'affichage
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Fonction pour afficher les étapes
step() {
    echo -e "${BLUE}[ÉTAPE]${NC} $1"
}

success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

error() {
    echo -e "${RED}[✗]${NC} $1"
}

# Vérifier que Docker est installé
if ! command -v docker &> /dev/null; then
    error "Docker n'est pas installé. Veuillez l'installer d'abord."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    error "Docker Compose n'est pas installé. Veuillez l'installer d'abord."
    exit 1
fi

success "Docker et Docker Compose sont installés"
echo ""

# Étape 1 : Démarrer la stack ELK
step "1/6 - Démarrage de la stack ELK (Elasticsearch, Logstash, Kibana, Filebeat)"
echo "      Cela peut prendre 1-2 minutes..."
docker-compose up -d

if [ $? -eq 0 ]; then
    success "Stack ELK démarrée avec succès"
else
    error "Erreur lors du démarrage de la stack ELK"
    exit 1
fi
echo ""

# Étape 2 : Attendre qu'Elasticsearch soit prêt
step "2/6 - Attente du démarrage d'Elasticsearch..."
ELASTICSEARCH_URL="http://localhost:9200"
MAX_WAIT=60
WAIT_COUNT=0

while ! curl -s "$ELASTICSEARCH_URL" > /dev/null; do
    if [ $WAIT_COUNT -ge $MAX_WAIT ]; then
        error "Timeout : Elasticsearch n'a pas démarré dans les temps"
        exit 1
    fi
    echo -n "."
    sleep 2
    WAIT_COUNT=$((WAIT_COUNT + 2))
done
echo ""
success "Elasticsearch est prêt"
echo ""

# Étape 3 : Créer le mapping Elasticsearch
step "3/6 - Création du mapping Elasticsearch"
./elasticsearch/create_index.sh > /dev/null 2>&1

if [ $? -eq 0 ]; then
    success "Mapping créé avec succès"
else
    warning "Le mapping existe peut-être déjà"
fi
echo ""

# Étape 4 : Attendre que Kibana soit prêt
step "4/6 - Attente du démarrage de Kibana..."
KIBANA_URL="http://localhost:5601"
MAX_WAIT=120
WAIT_COUNT=0

while ! curl -s "$KIBANA_URL/api/status" > /dev/null; do
    if [ $WAIT_COUNT -ge $MAX_WAIT ]; then
        error "Timeout : Kibana n'a pas démarré dans les temps"
        exit 1
    fi
    echo -n "."
    sleep 3
    WAIT_COUNT=$((WAIT_COUNT + 3))
done
echo ""
success "Kibana est prêt"
echo ""

# Étape 5 : Importer le dashboard Kibana
step "5/6 - Importation du dashboard Kibana"
sleep 5  # Attendre un peu plus pour que Kibana soit complètement prêt
./kibana/import_dashboard.sh > /dev/null 2>&1

if [ $? -eq 0 ]; then
    success "Dashboard importé avec succès"
else
    warning "Le dashboard existe peut-être déjà ou Kibana n'est pas encore prêt"
    warning "Vous pouvez l'importer manuellement plus tard avec : ./kibana/import_dashboard.sh"
fi
echo ""

# Étape 6 : Informations finales
step "6/6 - Configuration terminée"
echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                    ✨ PROJET PRÊT ✨                           ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "📊 Services disponibles :"
echo "   • Elasticsearch : http://localhost:9200"
echo "   • Kibana        : http://localhost:5601"
echo "   • Logstash API  : http://localhost:9600"
echo ""
echo "🚀 Prochaines étapes :"
echo ""
echo "   1. Lancer la simulation d'ingestion temps réel :"
echo "      ${GREEN}python3 scripts/simulate_realtime_logs.py --delay 1 --batch-size 10${NC}"
echo ""
echo "   2. Accéder à Kibana :"
echo "      ${GREEN}http://localhost:5601${NC}"
echo "      Puis : Dashboard → Firefox Build Monitoring Dashboard"
echo ""
echo "   3. Lancer la détection d'anomalies (après ingestion de données) :"
echo "      ${GREEN}pip install -r ml/requirements.txt${NC}"
echo "      ${GREEN}python3 ml/anomaly_detection.py${NC}"
echo ""
echo "📖 Documentation complète : README.md"
echo "📖 Guide rapide : GUIDE_UTILISATION.md"
echo ""
echo "🛠️  Commandes utiles :"
echo "   • Voir les logs       : ${GREEN}docker-compose logs -f${NC}"
echo "   • Arrêter le projet   : ${GREEN}docker-compose down${NC}"
echo "   • Redémarrer          : ${GREEN}docker-compose restart${NC}"
echo ""
echo "Bonne chance pour votre soutenance ! 🎓"
echo ""
