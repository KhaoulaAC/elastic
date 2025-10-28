#!/usr/bin/env python3
"""
Script de simulation d'ingestion temps réel des logs Firefox
Ce script copie progressivement les fichiers logs pour simuler leur arrivée en temps réel
"""

import os
import time
import shutil
import argparse
from pathlib import Path
from datetime import datetime

class LogSimulator:
    def __init__(self, source_dir, target_dir, delay=2, batch_size=5):
        """
        Initialise le simulateur de logs
        
        Args:
            source_dir: Répertoire source contenant tous les logs
            target_dir: Répertoire cible où les logs seront copiés progressivement
            delay: Délai en secondes entre chaque batch
            batch_size: Nombre de fichiers à copier par batch
        """
        self.source_dir = Path(source_dir)
        self.target_dir = Path(target_dir)
        self.delay = delay
        self.batch_size = batch_size
        
        # Créer le répertoire cible s'il n'existe pas
        self.target_dir.mkdir(parents=True, exist_ok=True)
        
    def get_all_log_files(self):
        """Récupère tous les fichiers logs triés par date"""
        log_files = []
        
        # Parcourir tous les sous-dossiers log-YYYY-MM-DD
        for log_dir in sorted(self.source_dir.glob("log-*")):
            if log_dir.is_dir():
                # Récupérer tous les fichiers .txt dans ce dossier
                for log_file in sorted(log_dir.glob("*.txt")):
                    log_files.append(log_file)
        
        return log_files
    
    def simulate(self):
        """Lance la simulation d'ingestion temps réel"""
        log_files = self.get_all_log_files()
        total_files = len(log_files)
        
        print(f"📊 Simulation d'ingestion temps réel")
        print(f"📁 Source: {self.source_dir}")
        print(f"📂 Cible: {self.target_dir}")
        print(f"📝 Total de fichiers: {total_files}")
        print(f"⏱️  Délai entre batches: {self.delay}s")
        print(f"📦 Taille des batches: {self.batch_size} fichiers")
        print(f"{'='*60}\n")
        
        copied_count = 0
        
        for i in range(0, total_files, self.batch_size):
            batch = log_files[i:i + self.batch_size]
            
            for log_file in batch:
                # Créer la structure de dossiers dans la cible
                relative_path = log_file.relative_to(self.source_dir)
                target_file = self.target_dir / relative_path
                target_file.parent.mkdir(parents=True, exist_ok=True)
                
                # Copier le fichier
                shutil.copy2(log_file, target_file)
                copied_count += 1
                
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"[{timestamp}] ✅ Copié ({copied_count}/{total_files}): {relative_path}")
            
            # Afficher la progression
            progress = (copied_count / total_files) * 100
            print(f"📈 Progression: {progress:.1f}% ({copied_count}/{total_files})\n")
            
            # Attendre avant le prochain batch (sauf pour le dernier)
            if i + self.batch_size < total_files:
                time.sleep(self.delay)
        
        print(f"\n{'='*60}")
        print(f"✨ Simulation terminée!")
        print(f"📊 {copied_count} fichiers copiés avec succès")
    
    def clean_target(self):
        """Nettoie le répertoire cible"""
        if self.target_dir.exists():
            shutil.rmtree(self.target_dir)
            print(f"🗑️  Répertoire cible nettoyé: {self.target_dir}")
        self.target_dir.mkdir(parents=True, exist_ok=True)


def main():
    parser = argparse.ArgumentParser(
        description="Simule l'ingestion temps réel des logs Firefox"
    )
    parser.add_argument(
        "--source",
        default="/vercel/sandbox/logs",
        help="Répertoire source contenant les logs (défaut: /vercel/sandbox/logs)"
    )
    parser.add_argument(
        "--target",
        default="/vercel/sandbox/logs-realtime",
        help="Répertoire cible pour la simulation (défaut: /vercel/sandbox/logs-realtime)"
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=2.0,
        help="Délai en secondes entre chaque batch (défaut: 2.0)"
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=5,
        help="Nombre de fichiers par batch (défaut: 5)"
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Nettoyer le répertoire cible avant de commencer"
    )
    
    args = parser.parse_args()
    
    simulator = LogSimulator(
        source_dir=args.source,
        target_dir=args.target,
        delay=args.delay,
        batch_size=args.batch_size
    )
    
    if args.clean:
        simulator.clean_target()
    
    try:
        simulator.simulate()
    except KeyboardInterrupt:
        print("\n\n⚠️  Simulation interrompue par l'utilisateur")
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        raise


if __name__ == "__main__":
    main()
