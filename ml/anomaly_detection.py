#!/usr/bin/env python3
"""
Module de détection d'anomalies pour les logs Firefox Build
Utilise plusieurs techniques de Machine Learning pour détecter les anomalies
"""

import json
import argparse
from datetime import datetime
from elasticsearch import Elasticsearch
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import numpy as np
import pandas as pd
import warnings
warnings.filterwarnings('ignore')


class FirefoxBuildAnomalyDetector:
    """Détecteur d'anomalies pour les builds Firefox"""
    
    def __init__(self, es_host="http://localhost:9200", index_pattern="firefox-logs-*"):
        """
        Initialise le détecteur d'anomalies
        
        Args:
            es_host: URL d'Elasticsearch
            index_pattern: Pattern d'index à analyser
        """
        self.es = Elasticsearch([es_host])
        self.index_pattern = index_pattern
        self.scaler = StandardScaler()
        self.model = IsolationForest(
            contamination=0.1,  # 10% d'anomalies attendues
            random_state=42,
            n_estimators=100
        )
        
    def fetch_build_data(self, size=10000):
        """
        Récupère les données de build depuis Elasticsearch
        
        Args:
            size: Nombre maximum de documents à récupérer
            
        Returns:
            DataFrame pandas avec les données
        """
        print(f"📊 Récupération des données depuis {self.index_pattern}...")
        
        query = {
            "size": size,
            "query": {
                "bool": {
                    "must": [
                        {"exists": {"field": "step_elapsed_secs"}},
                        {"exists": {"field": "results_code"}}
                    ]
                }
            },
            "sort": [{"@timestamp": {"order": "desc"}}]
        }
        
        try:
            response = self.es.search(index=self.index_pattern, body=query)
            hits = response['hits']['hits']
            
            if not hits:
                print("⚠️  Aucune donnée trouvée!")
                return pd.DataFrame()
            
            # Extraire les données pertinentes
            data = []
            for hit in hits:
                source = hit['_source']
                data.append({
                    'timestamp': source.get('@timestamp'),
                    'step_elapsed_secs': source.get('step_elapsed_secs', 0),
                    'results_code': source.get('results_code', 0),
                    'exit_code': source.get('exit_code', 0),
                    'buildername': source.get('buildername', 'unknown'),
                    'platform': source.get('platform', 'unknown'),
                    'step_name': source.get('step_name', 'unknown'),
                    'results_text': source.get('results_text', 'unknown')
                })
            
            df = pd.DataFrame(data)
            print(f"✅ {len(df)} enregistrements récupérés")
            return df
            
        except Exception as e:
            print(f"❌ Erreur lors de la récupération des données: {e}")
            return pd.DataFrame()
    
    def prepare_features(self, df):
        """
        Prépare les features pour le modèle ML
        
        Args:
            df: DataFrame avec les données brutes
            
        Returns:
            Array numpy avec les features normalisées
        """
        if df.empty:
            return np.array([])
        
        print("🔧 Préparation des features...")
        
        # Sélectionner les features numériques
        features = df[['step_elapsed_secs', 'results_code', 'exit_code']].copy()
        
        # Remplacer les valeurs manquantes
        features = features.fillna(0)
        
        # Normaliser les features
        features_scaled = self.scaler.fit_transform(features)
        
        print(f"✅ Features préparées: {features_scaled.shape}")
        return features_scaled
    
    def detect_anomalies(self, df):
        """
        Détecte les anomalies dans les données
        
        Args:
            df: DataFrame avec les données
            
        Returns:
            DataFrame avec les anomalies détectées
        """
        if df.empty:
            print("⚠️  Pas de données à analyser")
            return pd.DataFrame()
        
        print("🤖 Entraînement du modèle Isolation Forest...")
        
        # Préparer les features
        features = self.prepare_features(df)
        
        if len(features) == 0:
            print("⚠️  Pas de features disponibles")
            return pd.DataFrame()
        
        # Entraîner le modèle
        self.model.fit(features)
        
        # Prédire les anomalies (-1 = anomalie, 1 = normal)
        predictions = self.model.predict(features)
        
        # Calculer les scores d'anomalie
        anomaly_scores = self.model.score_samples(features)
        
        # Ajouter les résultats au DataFrame
        df['is_anomaly'] = predictions == -1
        df['anomaly_score'] = anomaly_scores
        
        # Filtrer les anomalies
        anomalies = df[df['is_anomaly']].copy()
        anomalies = anomalies.sort_values('anomaly_score')
        
        print(f"🔍 {len(anomalies)} anomalies détectées sur {len(df)} enregistrements ({len(anomalies)/len(df)*100:.1f}%)")
        
        return anomalies
    
    def analyze_anomalies(self, anomalies):
        """
        Analyse les anomalies détectées
        
        Args:
            anomalies: DataFrame avec les anomalies
        """
        if anomalies.empty:
            print("✅ Aucune anomalie détectée!")
            return
        
        print("\n" + "="*80)
        print("📊 ANALYSE DES ANOMALIES DÉTECTÉES")
        print("="*80)
        
        # Statistiques générales
        print(f"\n📈 Statistiques générales:")
        print(f"   - Nombre total d'anomalies: {len(anomalies)}")
        print(f"   - Score d'anomalie moyen: {anomalies['anomaly_score'].mean():.4f}")
        print(f"   - Score d'anomalie min: {anomalies['anomaly_score'].min():.4f}")
        
        # Anomalies par plateforme
        print(f"\n🖥️  Anomalies par plateforme:")
        platform_counts = anomalies['platform'].value_counts()
        for platform, count in platform_counts.head(5).items():
            print(f"   - {platform}: {count}")
        
        # Anomalies par type de résultat
        print(f"\n📋 Anomalies par résultat:")
        result_counts = anomalies['results_text'].value_counts()
        for result, count in result_counts.items():
            print(f"   - {result}: {count}")
        
        # Top 10 des anomalies les plus sévères
        print(f"\n🚨 Top 10 des anomalies les plus sévères:")
        top_anomalies = anomalies.nsmallest(10, 'anomaly_score')
        for idx, row in top_anomalies.iterrows():
            print(f"\n   [{idx+1}] Score: {row['anomaly_score']:.4f}")
            print(f"       - Timestamp: {row['timestamp']}")
            print(f"       - Platform: {row['platform']}")
            print(f"       - Step: {row['step_name'][:50]}...")
            print(f"       - Duration: {row['step_elapsed_secs']}s")
            print(f"       - Result: {row['results_text']}")
            print(f"       - Exit Code: {row['exit_code']}")
    
    def save_anomalies_to_es(self, anomalies, target_index="firefox-anomalies"):
        """
        Sauvegarde les anomalies dans un index Elasticsearch dédié
        
        Args:
            anomalies: DataFrame avec les anomalies
            target_index: Nom de l'index cible
        """
        if anomalies.empty:
            print("⚠️  Pas d'anomalies à sauvegarder")
            return
        
        print(f"\n💾 Sauvegarde des anomalies dans l'index '{target_index}'...")
        
        saved_count = 0
        for idx, row in anomalies.iterrows():
            doc = {
                '@timestamp': row['timestamp'],
                'anomaly_score': float(row['anomaly_score']),
                'step_elapsed_secs': int(row['step_elapsed_secs']),
                'results_code': int(row['results_code']),
                'exit_code': int(row['exit_code']),
                'buildername': row['buildername'],
                'platform': row['platform'],
                'step_name': row['step_name'],
                'results_text': row['results_text'],
                'detection_timestamp': datetime.now().isoformat()
            }
            
            try:
                self.es.index(index=target_index, body=doc)
                saved_count += 1
            except Exception as e:
                print(f"⚠️  Erreur lors de la sauvegarde: {e}")
        
        print(f"✅ {saved_count} anomalies sauvegardées dans '{target_index}'")
    
    def run_detection(self, save_to_es=True):
        """
        Exécute le processus complet de détection d'anomalies
        
        Args:
            save_to_es: Si True, sauvegarde les anomalies dans Elasticsearch
        """
        print("\n" + "="*80)
        print("🚀 DÉTECTION D'ANOMALIES - FIREFOX BUILD LOGS")
        print("="*80 + "\n")
        
        # Récupérer les données
        df = self.fetch_build_data()
        
        if df.empty:
            print("❌ Impossible de continuer sans données")
            return
        
        # Détecter les anomalies
        anomalies = self.detect_anomalies(df)
        
        # Analyser les anomalies
        self.analyze_anomalies(anomalies)
        
        # Sauvegarder dans Elasticsearch
        if save_to_es and not anomalies.empty:
            self.save_anomalies_to_es(anomalies)
        
        print("\n" + "="*80)
        print("✨ DÉTECTION TERMINÉE")
        print("="*80 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="Détection d'anomalies dans les logs Firefox Build"
    )
    parser.add_argument(
        "--es-host",
        default="http://localhost:9200",
        help="URL d'Elasticsearch (défaut: http://localhost:9200)"
    )
    parser.add_argument(
        "--index",
        default="firefox-logs-*",
        help="Pattern d'index à analyser (défaut: firefox-logs-*)"
    )
    parser.add_argument(
        "--no-save",
        action="store_true",
        help="Ne pas sauvegarder les anomalies dans Elasticsearch"
    )
    
    args = parser.parse_args()
    
    # Créer le détecteur et lancer l'analyse
    detector = FirefoxBuildAnomalyDetector(
        es_host=args.es_host,
        index_pattern=args.index
    )
    
    try:
        detector.run_detection(save_to_es=not args.no_save)
    except KeyboardInterrupt:
        print("\n\n⚠️  Détection interrompue par l'utilisateur")
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        raise


if __name__ == "__main__":
    main()
