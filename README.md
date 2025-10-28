# 🦊 Projet ELK - Monitoring des Builds Firefox

## 📋 Description du Projet

Ce projet implémente une solution complète de monitoring et d'analyse des logs de build Firefox en utilisant la stack ELK (Elasticsearch, Logstash, Kibana) avec Filebeat. Il permet l'ingestion en temps réel, l'indexation, la visualisation et la détection d'anomalies dans les logs de build.

### 🎯 Objectifs

1. **Indexation temps réel** : Ingestion automatisée des logs de build Firefox
2. **Mapping Elasticsearch** : Structure de données optimisée pour l'analyse
3. **Visualisation** : Dashboard Kibana pour le suivi des performances
4. **Machine Learning** : Détection automatique des anomalies dans les builds

---

## 🏗️ Architecture

```
┌─────────────────┐
│  Logs Firefox   │
│   (1837 files)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│    Filebeat     │ ◄── Lecture des fichiers logs
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│    Logstash     │ ◄── Parsing et transformation
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Elasticsearch   │ ◄── Indexation et stockage
└────────┬────────┘
         │
         ├──────────────────┐
         ▼                  ▼
┌─────────────────┐  ┌──────────────┐
│     Kibana      │  │  ML Module   │
│   (Dashboard)   │  │  (Anomalies) │
└─────────────────┘  └──────────────┘
```

---

## 📁 Structure du Projet

```
/vercel/sandbox/
├── docker-compose.yml           # Configuration Docker Compose
├── README.md                    # Cette documentation
│
├── logs/                        # Logs sources (1837 fichiers)
│   ├── log-2018-06-08/
│   ├── log-2018-06-09/
│   └── log-2018-06-10/
│
├── logs-realtime/               # Logs pour simulation temps réel
│
├── filebeat/
│   └── filebeat.yml            # Configuration Filebeat
│
├── logstash/
│   ├── logstash.conf           # Pipeline Logstash (parsing)
│   └── logstash.yml            # Configuration Logstash
│
├── elasticsearch/
│   ├── mapping.json            # Mapping des index
│   └── create_index.sh         # Script de création d'index
│
├── kibana/
│   ├── dashboard_firefox_builds.ndjson  # Dashboard exporté
│   └── import_dashboard.sh     # Script d'import du dashboard
│
├── ml/
│   ├── anomaly_detection.py    # Module de détection d'anomalies
│   └── requirements.txt        # Dépendances Python
│
└── scripts/
    └── simulate_realtime_logs.py  # Simulation ingestion temps réel
```

---

## 🚀 Installation et Démarrage

### Prérequis

- Docker et Docker Compose installés
- Python 3.7+ (pour les scripts ML)
- Au moins 4 GB de RAM disponible

### Étape 1 : Démarrer la Stack ELK

```bash
# Démarrer tous les services
docker-compose up -d

# Vérifier que tous les conteneurs sont démarrés
docker-compose ps

# Suivre les logs
docker-compose logs -f
```

**Services disponibles :**
- Elasticsearch : http://localhost:9200
- Kibana : http://localhost:5601
- Logstash : http://localhost:9600

### Étape 2 : Créer le Mapping Elasticsearch

```bash
# Attendre qu'Elasticsearch soit prêt (environ 30 secondes)
./elasticsearch/create_index.sh
```

Ce script crée un template d'index avec le mapping approprié pour tous les champs des logs Firefox.

### Étape 3 : Simuler l'Ingestion Temps Réel

```bash
# Lancer la simulation (copie progressive des logs)
python3 scripts/simulate_realtime_logs.py --delay 2 --batch-size 5

# Options disponibles :
# --delay : Délai en secondes entre chaque batch (défaut: 2)
# --batch-size : Nombre de fichiers par batch (défaut: 5)
# --clean : Nettoyer le répertoire cible avant de commencer
```

**Note :** Ce script copie progressivement les 1837 fichiers logs du dossier `logs/` vers `logs-realtime/` pour simuler une arrivée en temps réel. Filebeat surveille le dossier `logs-realtime/` et envoie les nouvelles lignes à Logstash.

### Étape 4 : Importer le Dashboard Kibana

```bash
# Attendre que Kibana soit prêt (environ 1 minute)
./kibana/import_dashboard.sh
```

Accédez ensuite à Kibana : http://localhost:5601

### Étape 5 : Lancer la Détection d'Anomalies

```bash
# Installer les dépendances Python
pip install -r ml/requirements.txt

# Lancer la détection d'anomalies
python3 ml/anomaly_detection.py

# Options disponibles :
# --es-host : URL d'Elasticsearch (défaut: http://localhost:9200)
# --index : Pattern d'index à analyser (défaut: firefox-logs-*)
# --no-save : Ne pas sauvegarder les anomalies dans ES
```

---

## 📊 Dashboard Kibana

Le dashboard **Firefox Build Monitoring** comprend 5 visualisations principales :

### 1. 🥧 Build Status Distribution
- **Type :** Pie Chart (Donut)
- **Métrique :** Distribution des résultats de build (success, failure, etc.)
- **Utilité :** Vue d'ensemble rapide du taux de succès

### 2. 📈 Build Duration Over Time
- **Type :** Line Chart
- **Métrique :** Durée moyenne des étapes de build au fil du temps
- **Utilité :** Identifier les tendances de performance

### 3. 📊 Top Build Platforms
- **Type :** Horizontal Bar Chart
- **Métrique :** Nombre de builds par plateforme
- **Utilité :** Voir quelles plateformes sont les plus actives

### 4. 🌊 Error Rate Timeline
- **Type :** Area Chart
- **Métrique :** Évolution des erreurs vs succès dans le temps
- **Utilité :** Détecter les pics d'erreurs

### 5. 🥧 Log Level Distribution
- **Type :** Pie Chart
- **Métrique :** Distribution des niveaux de log (INFO, WARNING, ERROR)
- **Utilité :** Comprendre la gravité des événements

---

## 🤖 Détection d'Anomalies avec Machine Learning

### Algorithme : Isolation Forest

Le module utilise l'algorithme **Isolation Forest** de scikit-learn pour détecter les anomalies dans les builds.

#### Caractéristiques analysées :
1. **step_elapsed_secs** : Durée d'exécution des étapes
2. **results_code** : Code de résultat du build
3. **exit_code** : Code de sortie du programme

#### Fonctionnement :
1. Récupération des données depuis Elasticsearch
2. Normalisation des features avec StandardScaler
3. Entraînement du modèle Isolation Forest
4. Détection des anomalies (contamination = 10%)
5. Calcul des scores d'anomalie
6. Sauvegarde dans l'index `firefox-anomalies`

#### Résultats :
- Liste des anomalies détectées
- Score d'anomalie pour chaque événement
- Analyse par plateforme et type de résultat
- Top 10 des anomalies les plus sévères

---

## 🔧 Configuration Détaillée

### Mapping Elasticsearch

Le mapping définit la structure des données indexées :

**Champs principaux :**
- `@timestamp` : Date/heure de l'événement
- `step_name` : Nom de l'étape de build
- `step_elapsed_secs` : Durée de l'étape (integer)
- `results_code` : Code de résultat (integer)
- `exit_code` : Code de sortie (integer)
- `buildername` : Nom du builder
- `platform` : Plateforme de build
- `loglevel` : Niveau de log (keyword)
- `tags` : Tags d'enrichissement

### Pipeline Logstash

Le fichier `logstash.conf` définit le pipeline de traitement :

1. **Input** : Réception depuis Filebeat (port 5044)
2. **Filter** :
   - Extraction de la date du nom de fichier
   - Parsing GROK des différents formats de logs
   - Construction du timestamp
   - Normalisation et conversions de types
   - Enrichissement avec tags
3. **Output** : Envoi vers Elasticsearch (index `firefox-logs-YYYY.MM.dd`)

### Filebeat

Configuration pour surveiller les logs :
- **Chemin surveillé** : `/logs/**/*.txt`
- **Type de log** : `firefox_build`
- **Output** : Logstash (port 5044)

---

## 📈 Indicateurs de Performance (KPI)

Le projet permet de suivre ces KPI :

1. **Taux de succès des builds** : % de builds réussis
2. **Durée moyenne des builds** : Temps moyen d'exécution
3. **Taux d'erreur** : % de builds en échec
4. **Plateformes les plus actives** : Distribution par OS
5. **Anomalies détectées** : Nombre et sévérité

---

## 🧪 Tests et Validation

### Vérifier l'ingestion des données

```bash
# Compter les documents indexés
curl -X GET "localhost:9200/firefox-logs-*/_count?pretty"

# Voir un exemple de document
curl -X GET "localhost:9200/firefox-logs-*/_search?size=1&pretty"
```

### Vérifier le dashboard

1. Accéder à Kibana : http://localhost:5601
2. Aller dans **Dashboard** → **Firefox Build Monitoring Dashboard**
3. Vérifier que les visualisations affichent des données

### Vérifier les anomalies

```bash
# Compter les anomalies détectées
curl -X GET "localhost:9200/firefox-anomalies/_count?pretty"

# Voir les anomalies les plus sévères
curl -X GET "localhost:9200/firefox-anomalies/_search?pretty" \
  -H 'Content-Type: application/json' \
  -d '{"size": 10, "sort": [{"anomaly_score": {"order": "asc"}}]}'
```

---

## 🛠️ Dépannage

### Problème : Elasticsearch ne démarre pas

```bash
# Vérifier les logs
docker-compose logs elasticsearch

# Solution : Augmenter la mémoire virtuelle
sudo sysctl -w vm.max_map_count=262144
```

### Problème : Aucune donnée dans Kibana

```bash
# Vérifier que Filebeat envoie des données
docker-compose logs filebeat

# Vérifier que Logstash reçoit des données
docker-compose logs logstash

# Vérifier les index Elasticsearch
curl -X GET "localhost:9200/_cat/indices?v"
```

### Problème : Le script Python ne trouve pas Elasticsearch

```bash
# Vérifier qu'Elasticsearch est accessible
curl -X GET "localhost:9200"

# Installer les dépendances Python
pip install -r ml/requirements.txt
```

---

## 📚 Ressources et Références

- [Documentation Elasticsearch](https://www.elastic.co/guide/en/elasticsearch/reference/7.16/index.html)
- [Documentation Logstash](https://www.elastic.co/guide/en/logstash/7.16/index.html)
- [Documentation Kibana](https://www.elastic.co/guide/en/kibana/7.16/index.html)
- [Documentation Filebeat](https://www.elastic.co/guide/en/beats/filebeat/7.16/index.html)
- [Isolation Forest Algorithm](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.IsolationForest.html)

---

## 🎓 Points Clés pour la Soutenance

### 1. Architecture et Choix Techniques
- **Stack ELK** : Solution open-source robuste et scalable
- **Filebeat** : Agent léger pour la collecte de logs
- **Logstash** : Pipeline flexible pour le parsing et l'enrichissement
- **Elasticsearch** : Moteur de recherche et d'analyse distribué
- **Kibana** : Interface de visualisation intuitive

### 2. Ingestion Temps Réel
- Script Python pour simuler l'arrivée progressive des logs
- Filebeat surveille le dossier et envoie les nouvelles lignes
- Logstash parse et enrichit les données en temps réel
- Elasticsearch indexe immédiatement

### 3. Mapping et Optimisation
- Mapping explicite pour tous les champs
- Types de données appropriés (integer, keyword, text)
- Index pattern avec rotation quotidienne
- Optimisation pour les requêtes d'agrégation

### 4. Visualisation et Monitoring
- Dashboard complet avec 5 visualisations
- KPI essentiels pour le monitoring des builds
- Filtres temporels et par plateforme
- Export/Import facile du dashboard

### 5. Machine Learning et Anomalies
- Algorithme Isolation Forest (non supervisé)
- Détection automatique des comportements anormaux
- Score d'anomalie pour prioriser les investigations
- Sauvegarde dans un index dédié pour analyse

### 6. Scalabilité et Production
- Architecture containerisée avec Docker
- Configuration facilement modifiable
- Possibilité d'ajouter des nœuds Elasticsearch
- Monitoring via l'API Logstash

---

## 👥 Auteur

Projet réalisé dans le cadre du cours de Monitoring et Infrastructure

---

## 📝 Licence

Ce projet est à usage éducatif.

---

## 🎯 Prochaines Étapes (Améliorations Possibles)

1. **Alerting** : Configurer des alertes Kibana pour les anomalies critiques
2. **ML avancé** : Utiliser Elasticsearch ML pour la détection d'anomalies native
3. **Sécurité** : Ajouter l'authentification et le chiffrement TLS
4. **Performance** : Optimiser les index avec ILM (Index Lifecycle Management)
5. **Monitoring** : Ajouter Metricbeat pour surveiller la stack ELK elle-même
6. **Corrélation** : Analyser les corrélations entre plateformes et types d'erreurs
