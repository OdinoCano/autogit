#!/usr/bin/env python3
import os
import json
import subprocess
import sys
from datetime import datetime, time
from pathlib import Path

def load_config(config_path):
    with open(config_path, 'r') as f:
        return json.load(f)

def is_work_hours(config):
    now = datetime.now()
    if now.strftime("%A") not in config.get('work_days', []):
        return False
    
    current_time = now.time()
    for schedule in config.get('schedule', []):
        scheduled_time = time(*map(int, schedule.split(':')))
        # Check if current time is within 30 minutes of scheduled time
        time_diff = abs((datetime.combine(datetime.today(), scheduled_time) - 
                        datetime.combine(datetime.today(), current_time)).total_seconds() / 60)
        if time_diff <= 30:  # 30-minute window
            return True
    return False

def git_pull(project_path, remote, remote_branch, local_branch):
    """
    Hace fetch del remoto y merge de remote_branch hacia local_branch.
    Ejemplo: git fetch Luis && git checkout main && git merge Luis/mongo
    """
    try:
        print(f"\n{'='*50}")
        print(f"Procesando: {project_path}")
        print(f"  Remote: {remote}")
        print(f"  Rama remota: {remote}/{remote_branch}")
        print(f"  Rama local: {local_branch}")
        print('='*50)
        
        os.chdir(project_path)
        
        # Fetch del remoto
        print(f"Fetching {remote}...")
        subprocess.run(['git', 'fetch', remote], check=True)
        
        # Checkout a la rama local
        print(f"Cambiando a rama local: {local_branch}...")
        subprocess.run(['git', 'checkout', local_branch], check=True)
        
        # Merge de la rama remota
        print(f"Haciendo merge de {remote}/{remote_branch} -> {local_branch}...")
        result = subprocess.run(
            ['git', 'merge', f'{remote}/{remote_branch}'],
            capture_output=True, text=True
        )
        print(result.stdout)
        if result.stderr:
            print(f"Advertencia: {result.stderr}")
            
        print("✓ Completado")
                
    except Exception as e:
        print(f"✗ Error procesando {project_path}: {str(e)}")

def main():
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                             'git_automation_config.json')
    
    if not os.path.exists(config_path):
        print(f"Config file not found: {config_path}")
        sys.exit(1)
        
    config = load_config(config_path)
    
    # If run with --force, skip work hours check
    if '--force' not in sys.argv and not is_work_hours(config):
        print("Not within work hours or scheduled time. Use --force to run anyway.")
        sys.exit(0)
        
    print(f"Starting Git automation at {datetime.now()}")
    
    for project, settings in config['projects'].items():
        path = settings.get('path')
        if not path or not os.path.exists(path):
            print(f"Saltando {project}: El path no existe - {path}")
            continue
        
        # Soporta formato con "syncs" (múltiples) o formato simple (uno solo)
        if 'syncs' in settings:
            # Múltiples sincronizaciones
            for sync in settings['syncs']:
                git_pull(
                    path,
                    sync.get('remote', 'origin'),
                    sync.get('remote_branch', 'main'),
                    sync.get('local_branch', 'main')
                )
        else:
            # Formato simple (una sola sincronización)
            git_pull(
                path,
                settings.get('remote', 'origin'),
                settings.get('remote_branch', 'main'),
                settings.get('local_branch', 'main')
            )
    
    print("\nGit automation completed.")

if __name__ == "__main__":
    main()
