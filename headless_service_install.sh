#!/bin/bash

# Fetch script directory
REPO_PATH=$(dirname "$(readlink -f "$0")")

# Replace %repo_path% in the service file with the actual path
sed -i "s|%repo_path%|$REPO_PATH|g" "$REPO_PATH/headless_opencore.service"

# Copy the modified service file to /etc/systemd/system/
sudo cp "$REPO_PATH/headless_opencore.service" /etc/systemd/system/

# Reload systemd daemon to apply the new service file
sudo systemctl daemon-reload

# Enable the service to start on boot
sudo systemctl enable headless_opencore.service
