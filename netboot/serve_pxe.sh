#!/bin/bash

# Serve pxelinux.0, vmlinuz, and initrd via TFTP using dnsmasq

# Ensure dnsmasq is installed
if ! command -v dnsmasq &> /dev/null
then
    echo "dnsmasq could not be found, please install it."
    exit
fi

# Create tftpboot directory if it doesn't exist
TFTPBOOT_DIR="tftpboot"
if [ ! -d "$TFTPBOOT_DIR" ]; then
    mkdir -p "$TFTPBOOT_DIR"
fi

# Copy necessary files to tftpboot directory
cp pxelinux.0 "$TFTPBOOT_DIR/"
cp vmlinuz "$TFTPBOOT_DIR/"
cp initrd.img "$TFTPBOOT_DIR/"

# Start dnsmasq to serve PXE boot files
dnsmasq --conf-file=netboot/dnsmasq.conf
