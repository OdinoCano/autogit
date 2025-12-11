# Git Auto-Pull Automation

Herramienta de automatización para mantener actualizados múltiples repositorios Git con un solo comando.

## Características

- Actualización automática de múltiples repositorios Git
- Configuración mediante archivo JSON
- Soporte para Linux (systemd) y Windows (Tareas Programadas)
- Registro de actividades en archivo de log
- **Notificaciones del sistema operativo** para alertar sobre:
  - ✅ Sincronizaciones exitosas
  - ⚠️ Conflictos de merge que requieren intervención manual
  - ❌ Errores de fetch, checkout o merge

## Requisitos

- Python 3.6 o superior
- Git
- Permisos de administrador para configurar tareas programadas (Windows) o servicios systemd (Linux)
- **Linux**: `libnotify` (notify-send) para notificaciones del sistema
- **macOS**: Soporte nativo via osascript
- **Windows**: PowerShell para notificaciones toast

## Instalación

### Linux

1. Clona el repositorio:
   ```bash
   git clone https://github.com/OdinoCano/autogit.git
   cd autogit
   ```

2. Haz ejecutable el script de instalación:
   ```bash
   chmod +x setup_linux.sh
   ```

3. Ejecuta el script de instalación (requiere sudo):
   ```bash
   sudo ./setup_linux.sh
   ```

### Windows

1. Clona el repositorio
2. Ejecuta `setup_windows.bat` como administrador

## Configuración

Edita el archivo `git_automation_config.json` para agregar tus repositorios:

```json
{
  "repos": [
    {
      "path": "/ruta/completa/al/repositorio",
      "remote": "origin",
      "branch": "main",
      "pull_strategy": "merge"
    }
  ]
}
```

## Uso

### Ejecución manual

```bash
python3 git_auto_pull.py [--force]
```

### Ver estado del servicio (Linux)

```bash
systemctl status git-autopull
```

### Ver logs (Linux)

```bash
tail -f ~/git_auto_pull_logs/git_autopull.log
```

## Notificaciones del Sistema

AutoGit envía notificaciones nativas del sistema operativo para mantenerte informado:

| Evento | Notificación |
|--------|-------------|
| Sincronización exitosa | ✅ Resumen de operaciones completadas |
| Conflicto de merge | ⚠️ Alerta con detalles del conflicto |
| Error de fetch/checkout | ❌ Error con información del problema |

### Instalación de dependencias de notificaciones

**Linux (Debian/Ubuntu):**
```bash
sudo apt-get install libnotify-bin
```

**Linux (Fedora/RHEL):**
```bash
sudo dnf install libnotify
```

**Linux (Arch):**
```bash
sudo pacman -S libnotify
```

**macOS y Windows:** No requieren instalación adicional.

## Licencia

MIT

## Contribución

Las contribuciones son bienvenidas. Por favor, envía un Pull Request con tus cambios.
