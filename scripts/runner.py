import os
import sys
import argparse
import importlib.util
from pathlib import Path
import subprocess

def list_available_scripts():
    """Liste tous les scripts Python disponibles dans le dossier scripts et ses sous-dossiers"""
    scripts_dir = Path(__file__).parent
    available_scripts = []
    
    for script_path in scripts_dir.glob('**/*.py'):
        # Ignorer ce script runner et les fichiers __init__.py
        if script_path.name in ['runner.py', '__init__.py'] or script_path.name.startswith('_'):
            continue
            
        # Calculer le chemin relatif à partir du dossier scripts
        rel_path = script_path.relative_to(scripts_dir)
        script_id = str(rel_path).replace('\\', '/').replace('.py', '')
        available_scripts.append((script_id, script_path))
        
    return available_scripts

def run_script(script_id, args=None):
    """Exécute un script spécifique avec les arguments fournis"""
    scripts_dir = Path(__file__).parent
    available_scripts = list_available_scripts()
    
    # Trouver le chemin du script demandé
    script_path = None
    for id, path in available_scripts:
        if id == script_id:
            script_path = path
            break
            
    if not script_path:
        print(f"Erreur: Script '{script_id}' non trouvé.")
        print("Scripts disponibles:")
        for id, _ in available_scripts:
            print(f"  - {id}")
        return 1
    
    # Récupérer le répertoire du script pour l'utiliser comme working directory
    script_dir = script_path.parent
    
    # Préparer les arguments
    cmd_args = [sys.executable, script_path.name]
    if args:
        cmd_args.extend(args)
        
    # Exécuter le script dans son propre répertoire pour que les logs soient créés là
    print(f"Exécution du script: {script_id}")
    print(f"Répertoire de travail: {script_dir}")
    print(f"Commande: {' '.join(cmd_args)}")
    
    # Utiliser le répertoire du script comme working directory
    return subprocess.call(cmd_args, cwd=str(script_dir))

def main():
    parser = argparse.ArgumentParser(description="Exécute des scripts Python du projet")
    parser.add_argument("script", nargs="?", help="Identifiant du script à exécuter (omettez pour voir la liste)")
    parser.add_argument("args", nargs=argparse.REMAINDER, help="Arguments à passer au script")
    
    args = parser.parse_args()
    
    available_scripts = list_available_scripts()
    
    # Si aucun script n'est spécifié, afficher la liste des scripts disponibles
    if not args.script:
        print("Scripts disponibles:")
        for script_id, _ in available_scripts:
            print(f"  - {script_id}")
        return 0
        
    # Exécuter le script demandé
    return run_script(args.script, args.args)

if __name__ == "__main__":
    sys.exit(main())