#!/bin/bash

# Make the Python script executable
chmod +x git_auto_pull.py

# Instalar libnotify para notificaciones del sistema
echo "Verificando dependencias de notificaciones..."
if command -v apt-get &> /dev/null; then
    # Debian/Ubuntu
    sudo apt-get install -y libnotify-bin 2>/dev/null || echo "libnotify ya instalado o no se pudo instalar"
elif command -v dnf &> /dev/null; then
    # Fedora/RHEL
    sudo dnf install -y libnotify 2>/dev/null || echo "libnotify ya instalado o no se pudo instalar"
elif command -v pacman &> /dev/null; then
    # Arch Linux
    sudo pacman -S --noconfirm libnotify 2>/dev/null || echo "libnotify ya instalado o no se pudo instalar"
elif command -v zypper &> /dev/null; then
    # openSUSE
    sudo zypper install -y libnotify-tools 2>/dev/null || echo "libnotify ya instalado o no se pudo instalar"
fi

# Verificar que notify-send está disponible
if command -v notify-send &> /dev/null; then
    echo "✓ notify-send está disponible para notificaciones del sistema"
else
    echo "⚠ notify-send no está disponible. Las notificaciones del sistema no funcionarán."
    echo "  Instala libnotify manualmente según tu distribución."
fi

# Create log directory
LOG_DIR="$HOME/git_auto_pull_logs"
mkdir -p "$LOG_DIR"

# Create a systemd service file
SERVICE_FILE="/etc/systemd/system/git-autopull.service"
SCRIPT_PATH="$(pwd)/git_auto_pull.py"

cat << EOF | sudo tee "$SERVICE_FILE" > /dev/null
[Unit]
Description=Git Auto Pull Service
After=network.target

[Service]
Type=oneshot
User=$(whoami)
WorkingDirectory=$(pwd)
ExecStart=/usr/bin/python3 $SCRIPT_PATH
StandardOutput=append:$LOG_DIR/git_autopull.log
StandardError=append:$LOG_DIR/git_autopull_error.log

[Install]
WantedBy=multi-user.target
EOF

# Create a systemd timer
TIMER_FILE="/etc/systemd/system/git-autopull.timer"

cat << EOF | sudo tee "$TIMER_FILE" > /dev/null
[Unit]
Description=Run git auto pull during work hours

[Timer]
OnBootSec=5min
OnUnitActiveSec=4h
AccuracySec=1h
Persistent=true

[Install]
WantedBy=timers.target
EOF

# Reload systemd, enable and start the timer
sudo systemctl daemon-reload
sudo systemctl enable git-autopull.timer
sudo systemctl start git-autopull.timer

echo "Git auto-pull service has been set up."
echo "Logs will be saved to: $LOG_DIR"
echo "To check status: systemctl status git-autopull"
echo "To view logs: tail -f $LOG_DIR/git_autopull.log"
echo "To force a manual run: python3 git_auto_pull.py --force"
