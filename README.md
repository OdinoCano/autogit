# Git Auto-Pull Automation

Herramienta de automatización para mantener actualizados múltiples repositorios Git con un solo comando.

## Características

- Actualización automática de múltiples repositorios Git
- Configuración mediante archivo JSON
- Soporte para Linux (systemd) y Windows (Tareas Programadas)
- Registro de actividades en archivo de log

## Requisitos

- Python 3.6 o superior
- Git
- Permisos de administrador para configurar tareas programadas (Windows) o servicios systemd (Linux)

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

## Licencia

MIT

## Contribución

Las contribuciones son bienvenidas. Por favor, envía un Pull Request con tus cambios.
