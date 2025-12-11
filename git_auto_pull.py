#!/usr/bin/env python3
import os
import json
import subprocess
import sys
import platform
from datetime import datetime, time
from pathlib import Path
from enum import Enum

class NotificationType(Enum):
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    INFO = "info"

def send_notification(title, message, notification_type=NotificationType.INFO):
    """
    Envía una notificación del sistema operativo.
    Soporta Linux (notify-send), macOS (osascript) y Windows (toast).
    """
    system = platform.system()
    
    # Mapeo de iconos según el tipo de notificación
    icon_map = {
        NotificationType.SUCCESS: "dialog-positive",
        NotificationType.WARNING: "dialog-warning",
        NotificationType.ERROR: "dialog-error",
        NotificationType.INFO: "dialog-information"
    }
    
    # Mapeo de urgencia para notify-send
    urgency_map = {
        NotificationType.SUCCESS: "normal",
        NotificationType.WARNING: "normal",
        NotificationType.ERROR: "critical",
        NotificationType.INFO: "low"
    }
    
    try:
        if system == "Linux":
            # Usar notify-send (libnotify)
            icon = icon_map.get(notification_type, "dialog-information")
            urgency = urgency_map.get(notification_type, "normal")
            subprocess.run([
                'notify-send',
                '--urgency', urgency,
                '--icon', icon,
                '--app-name', 'AutoGit',
                title,
                message
            ], check=False)
            
        elif system == "Darwin":  # macOS
            script = f'display notification "{message}" with title "{title}"'
            subprocess.run(['osascript', '-e', script], check=False)
            
        elif system == "Windows":
            # Usar PowerShell para notificaciones toast
            ps_script = f'''
            [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
            $template = [Windows.UI.Notifications.ToastTemplateType]::ToastText02
            $xml = [Windows.UI.Notifications.ToastNotificationManager]::GetTemplateContent($template)
            $text = $xml.GetElementsByTagName("text")
            $text[0].AppendChild($xml.CreateTextNode("{title}")) | Out-Null
            $text[1].AppendChild($xml.CreateTextNode("{message}")) | Out-Null
            $toast = [Windows.UI.Notifications.ToastNotification]::new($xml)
            [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("AutoGit").Show($toast)
            '''
            subprocess.run(['powershell', '-Command', ps_script], check=False, capture_output=True)
            
    except Exception as e:
        print(f"No se pudo enviar notificación: {e}")

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

def check_merge_conflicts(project_path):
    """
    Verifica si hay conflictos de merge pendientes.
    """
    try:
        result = subprocess.run(
            ['git', 'diff', '--name-only', '--diff-filter=U'],
            capture_output=True, text=True, cwd=project_path
        )
        conflicted_files = result.stdout.strip()
        return conflicted_files if conflicted_files else None
    except Exception:
        return None

def git_pull(project_path, remote, remote_branch, local_branch):
    """
    Hace fetch del remoto y merge de remote_branch hacia local_branch.
    Ejemplo: git fetch Luis && git checkout main && git merge Luis/mongo
    Retorna: (success: bool, message: str, has_conflicts: bool)
    """
    project_name = os.path.basename(project_path)
    
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
        fetch_result = subprocess.run(
            ['git', 'fetch', remote], 
            capture_output=True, text=True
        )
        if fetch_result.returncode != 0:
            error_msg = f"Error en fetch: {fetch_result.stderr}"
            print(f"✗ {error_msg}")
            send_notification(
                f"❌ AutoGit - Error en {project_name}",
                f"No se pudo hacer fetch de {remote}\n{fetch_result.stderr[:100]}",
                NotificationType.ERROR
            )
            return False, error_msg, False
        
        # Checkout a la rama local
        print(f"Cambiando a rama local: {local_branch}...")
        checkout_result = subprocess.run(
            ['git', 'checkout', local_branch],
            capture_output=True, text=True
        )
        if checkout_result.returncode != 0:
            error_msg = f"Error en checkout: {checkout_result.stderr}"
            print(f"✗ {error_msg}")
            send_notification(
                f"❌ AutoGit - Error en {project_name}",
                f"No se pudo cambiar a rama {local_branch}\n{checkout_result.stderr[:100]}",
                NotificationType.ERROR
            )
            return False, error_msg, False
        
        # Merge de la rama remota
        print(f"Haciendo merge de {remote}/{remote_branch} -> {local_branch}...")
        result = subprocess.run(
            ['git', 'merge', f'{remote}/{remote_branch}'],
            capture_output=True, text=True
        )
        print(result.stdout)
        
        # Verificar si hay conflictos
        if result.returncode != 0 or 'CONFLICT' in result.stdout or 'CONFLICT' in result.stderr:
            conflicts = check_merge_conflicts(project_path)
            conflict_msg = f"Conflictos en merge de {remote}/{remote_branch}\nArchivos: {conflicts[:150] if conflicts else 'desconocido'}..."
            print(f"⚠ CONFLICTO DETECTADO: {conflict_msg}")
            send_notification(
                f"⚠️ AutoGit - CONFLICTO en {project_name}",
                f"Se detectaron conflictos de merge.\nRama: {remote}/{remote_branch} -> {local_branch}\nRequiere intervención manual.",
                NotificationType.WARNING
            )
            return False, conflict_msg, True
        
        if result.stderr and 'error' in result.stderr.lower():
            print(f"Advertencia: {result.stderr}")
            send_notification(
                f"⚠️ AutoGit - Advertencia en {project_name}",
                result.stderr[:150],
                NotificationType.WARNING
            )
            
        print("✓ Completado")
        return True, "Merge completado exitosamente", False
                
    except subprocess.CalledProcessError as e:
        error_msg = f"Error de Git: {str(e)}"
        print(f"✗ {error_msg}")
        send_notification(
            f"❌ AutoGit - Error en {project_name}",
            error_msg[:150],
            NotificationType.ERROR
        )
        return False, error_msg, False
        
    except Exception as e:
        error_msg = f"Error inesperado: {str(e)}"
        print(f"✗ Error procesando {project_path}: {str(e)}")
        send_notification(
            f"❌ AutoGit - Error en {project_name}",
            error_msg[:150],
            NotificationType.ERROR
        )
        return False, error_msg, False

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
    
    # Contadores para resumen final
    total_syncs = 0
    successful_syncs = 0
    failed_syncs = 0
    conflicts_detected = 0
    skipped_projects = 0
    
    for project, settings in config['projects'].items():
        path = settings.get('path')
        if not path or not os.path.exists(path):
            print(f"Saltando {project}: El path no existe - {path}")
            skipped_projects += 1
            continue
        
        # Soporta formato con "syncs" (múltiples) o formato simple (uno solo)
        if 'syncs' in settings:
            # Múltiples sincronizaciones
            for sync in settings['syncs']:
                total_syncs += 1
                success, msg, has_conflict = git_pull(
                    path,
                    sync.get('remote', 'origin'),
                    sync.get('remote_branch', 'main'),
                    sync.get('local_branch', 'main')
                )
                if success:
                    successful_syncs += 1
                else:
                    failed_syncs += 1
                    if has_conflict:
                        conflicts_detected += 1
        else:
            # Formato simple (una sola sincronización)
            total_syncs += 1
            success, msg, has_conflict = git_pull(
                path,
                settings.get('remote', 'origin'),
                settings.get('remote_branch', 'main'),
                settings.get('local_branch', 'main')
            )
            if success:
                successful_syncs += 1
            else:
                failed_syncs += 1
                if has_conflict:
                    conflicts_detected += 1
    
    # Resumen final con notificación
    print("\nGit automation completed.")
    print(f"  Total: {total_syncs} | Exitosos: {successful_syncs} | Fallidos: {failed_syncs} | Conflictos: {conflicts_detected}")
    
    # Notificación de resumen
    if failed_syncs == 0 and conflicts_detected == 0:
        if total_syncs > 0:
            send_notification(
                "✅ AutoGit - Completado",
                f"Todas las sincronizaciones completadas.\n{successful_syncs}/{total_syncs} exitosas.",
                NotificationType.SUCCESS
            )
    elif conflicts_detected > 0:
        send_notification(
            "⚠️ AutoGit - Conflictos Detectados",
            f"{conflicts_detected} conflicto(s) requieren atención manual.\nRevisa los proyectos afectados.",
            NotificationType.WARNING
        )
    else:
        send_notification(
            "❌ AutoGit - Errores Detectados",
            f"{failed_syncs} sincronización(es) fallaron.\nRevisa los logs para más detalles.",
            NotificationType.ERROR
        )

if __name__ == "__main__":
    main()
