# 📖 Guide d'Utilisation Rapide - Projet ELK Firefox

## 🚀 Démarrage Rapide (5 minutes)

### Étape 1 : Démarrer la Stack ELK
```bash
cd /vercel/sandbox
docker-compose up -d
```

Attendez environ 1-2 minutes que tous les services démarrent.

### Étape 2 : Créer le Mapping
```bash
./elasticsearch/create_index.sh
```

### Étape 3 : Simuler l'Ingestion Temps Réel
```bash
python3 scripts/simulate_realtime_logs.py --delay 1 --batch-size 10
```

**Note :** Laissez ce script tourner en arrière-plan. Il va copier progressivement les 1837 fichiers logs.

### Étape 4 : Accéder à Kibana
Ouvrez votre navigateur : http://localhost:5601

1. Allez dans **Management** → **Stack Management** → **Index Patterns**
2. Créez un index pattern : `firefox-logs-*`
3. Sélectionnez `@timestamp` comme champ de temps
4. Cliquez sur **Create index pattern**

### Étape 5 : Importer le Dashboard
```bash
./kibana/import_dashboard.sh
```

Ou manuellement dans Kibana :
1. **Management** → **Stack Management** → **Saved Objects**
2. Cliquez sur **Import**
3. Sélectionnez le fichier `kibana/dashboard_firefox_builds.ndjson`
4. Cliquez sur **Import**

### Étape 6 : Voir le Dashboard
1. Allez dans **Dashboard**
2. Ouvrez **Firefox Build Monitoring Dashboard**
3. Ajustez la période de temps (en haut à droite) : **Last 7 days**

### Étape 7 : Lancer la Détection d'Anomalies
```bash
# Installer les dépendances (une seule fois)
pip install -r ml/requirements.txt

# Lancer la détection
python3 ml/anomaly_detection.py
```

---

## 🎯 Commandes Utiles

### Vérifier l'État des Services
```bash
# Voir tous les conteneurs
docker-compose ps

# Voir les logs d'un service
docker-compose logs -f elasticsearch
docker-compose logs -f logstash
docker-compose logs -f kibana
docker-compose logs -f filebeat
```

### Vérifier les Données dans Elasticsearch
```bash
# Compter les documents
curl -X GET "localhost:9200/firefox-logs-*/_count?pretty"

# Voir les index
curl -X GET "localhost:9200/_cat/indices?v"

# Rechercher des documents
curl -X GET "localhost:9200/firefox-logs-*/_search?size=5&pretty"
```

### Arrêter et Redémarrer
```bash
# Arrêter tous les services
docker-compose down

# Redémarrer
docker-compose up -d

# Supprimer les données et tout réinitialiser
docker-compose down -v
```

---

## 🔍 Requêtes Elasticsearch Utiles

### Rechercher les Builds en Échec
```bash
curl -X GET "localhost:9200/firefox-logs-*/_search?pretty" \
  -H 'Content-Type: application/json' \
  -d '{
    "query": {
      "match": {
        "results_text": "failure"
      }
    },
    "size": 10
  }'
```

### Statistiques sur les Durées de Build
```bash
curl -X GET "localhost:9200/firefox-logs-*/_search?pretty" \
  -H 'Content-Type: application/json' \
  -d '{
    "size": 0,
    "aggs": {
      "avg_duration": {
        "avg": {
          "field": "step_elapsed_secs"
        }
      },
      "max_duration": {
        "max": {
          "field": "step_elapsed_secs"
        }
      }
    }
  }'
```

### Builds par Plateforme
```bash
curl -X GET "localhost:9200/firefox-logs-*/_search?pretty" \
  -H 'Content-Type: application/json' \
  -d '{
    "size": 0,
    "aggs": {
      "platforms": {
        "terms": {
          "field": "platform",
          "size": 10
        }
      }
    }
  }'
```

---

## 📊 Visualisations Kibana

### Créer une Visualisation Personnalisée

1. Allez dans **Visualize Library**
2. Cliquez sur **Create visualization**
3. Choisissez le type (Pie, Bar, Line, etc.)
4. Sélectionnez l'index pattern `firefox-logs-*`
5. Configurez les métriques et buckets
6. Sauvegardez

### Exemples de Visualisations

#### 1. Nombre de Builds par Heure
- Type : **Vertical Bar**
- Metrics : Count
- Buckets : Date Histogram sur `@timestamp` (interval: 1h)

#### 2. Taux de Succès
- Type : **Metric**
- Metrics : Count
- Filters : `results_text:success`

#### 3. Durée Moyenne par Plateforme
- Type : **Horizontal Bar**
- Metrics : Average of `step_elapsed_secs`
- Buckets : Terms on `platform`

---

## 🤖 Détection d'Anomalies - Options Avancées

### Ajuster la Sensibilité
Modifiez le paramètre `contamination` dans `ml/anomaly_detection.py` :
```python
self.model = IsolationForest(
    contamination=0.05,  # 5% au lieu de 10%
    random_state=42,
    n_estimators=100
)
```

### Analyser Plus de Données
```bash
python3 ml/anomaly_detection.py --es-host http://localhost:9200 --index "firefox-logs-*"
```

### Ne Pas Sauvegarder les Anomalies
```bash
python3 ml/anomaly_detection.py --no-save
```

---

## 🎓 Pour la Soutenance

### Démonstration Recommandée

1. **Introduction (2 min)**
   - Présenter l'architecture ELK
   - Expliquer le contexte (logs Firefox)

2. **Ingestion Temps Réel (3 min)**
   - Montrer le script de simulation
   - Expliquer le rôle de Filebeat et Logstash
   - Montrer les logs en temps réel dans Kibana Discover

3. **Dashboard et Visualisations (5 min)**
   - Présenter le dashboard complet
   - Expliquer chaque visualisation
   - Montrer les KPI importants
   - Démontrer les filtres et interactions

4. **Machine Learning (5 min)**
   - Lancer le script de détection d'anomalies
   - Expliquer l'algorithme Isolation Forest
   - Montrer les résultats dans le terminal
   - Afficher les anomalies dans Kibana

5. **Questions Techniques (5 min)**
   - Mapping Elasticsearch
   - Pipeline Logstash (GROK patterns)
   - Scalabilité de la solution

### Questions Fréquentes

**Q: Pourquoi Isolation Forest ?**
R: Algorithme non supervisé, efficace pour détecter les outliers dans des données multidimensionnelles, ne nécessite pas de données labellisées.

**Q: Comment gérer plus de données ?**
R: Ajouter des nœuds Elasticsearch, utiliser ILM pour archiver les vieux index, optimiser les shards.

**Q: Pourquoi Logstash et pas directement Filebeat → Elasticsearch ?**
R: Logstash permet un parsing complexe avec GROK, enrichissement des données, transformations avancées.

**Q: Comment détecter d'autres types d'anomalies ?**
R: Ajouter plus de features (bytes_downloaded, transfer_rate), utiliser d'autres algorithmes (DBSCAN, One-Class SVM), intégrer Elasticsearch ML.

---

## 🐛 Problèmes Courants

### Elasticsearch : "max virtual memory areas too low"
```bash
sudo sysctl -w vm.max_map_count=262144
```

### Filebeat : "Exiting: error loading config file: config file permissions"
Le fichier `filebeat.yml` doit avoir les bonnes permissions. C'est déjà géré avec `strict.perms: false`.

### Kibana : "No data"
1. Vérifiez que le script de simulation tourne
2. Vérifiez que Filebeat envoie des données : `docker-compose logs filebeat`
3. Vérifiez que Logstash reçoit des données : `docker-compose logs logstash`
4. Vérifiez les index : `curl localhost:9200/_cat/indices?v`

### Python : "ModuleNotFoundError"
```bash
pip install -r ml/requirements.txt
```

---

## 📞 Support

Pour toute question ou problème, vérifiez :
1. Les logs Docker : `docker-compose logs`
2. L'état des services : `docker-compose ps`
3. La connectivité : `curl localhost:9200` et `curl localhost:5601`

---

Bon courage pour votre soutenance ! 🎉
