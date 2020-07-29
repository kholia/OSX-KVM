#!/usr/bin/env bash

# Special thanks to...
# https://github.com/Leoyzen/KVM-Opencore
# https://github.com/thenickdude/KVM-Opencore/
# https://github.com/qemu/qemu/blob/master/docs/usb2.txt

ALLOCATED_RAM="3072" # MiB
CPU_SOCKETS="1"
CPU_CORES="2"
CPU_THREADS="4"

REPO_PATH="./"
OVMF_DIR="."

qemu-system-x86_64 -enable-kvm -m "$ALLOCATED_RAM" -cpu host,kvm=on,vendor=GenuineIntel,+invtsc,vmware-cpuid-freq=on \
	-machine q35 -usb \
	-smp "$CPU_THREADS",cores="$CPU_CORES",sockets="$CPU_SOCKETS" \
	-drive if=pflash,format=raw,readonly,file="$REPO_PATH/$OVMF_DIR/OVMF_CODE.fd" \
	-drive if=pflash,format=raw,file="$REPO_PATH/$OVMF_DIR/OVMF_VARS-1024x768.fd" \
	-drive id=OpenCoreBoot,if=none,snapshot=on,format=qcow2,file=$REPO_PATH/'OpenCore-Catalina/OpenCore.qcow2' \
	-drive id=InstallMedia,if=none,file=$REPO_PATH/BaseSystem.img,format=raw \
	-drive id=MacHDD,if=none,file=$REPO_PATH/mac_hdd_ng.img,format=qcow2 \
	-smbios type=2 \
	-device isa-applesmc,osk="ourhardworkbythesewordsguardedpleasedontsteal(c)AppleComputerInc" \
	-device usb-ehci,id=ehci \
	-device usb-kbd,bus=ehci.0 \
	-device usb-mouse,bus=ehci.0 \
	-device nec-usb-xhci,id=xhci \
	-device ich9-ahci,id=sata \
	-device ich9-intel-hda -device hda-duplex \
	-device ide-hd,bus=sata.2,drive=OpenCoreBoot \
	-device ide-hd,bus=sata.3,drive=InstallMedia \
	-device ide-hd,bus=sata.4,drive=MacHDD \
	-netdev tap,id=net0,ifname=tap0,script=no,downscript=no -device vmxnet3,netdev=net0,id=net0,mac=52:54:00:c9:18:27 \
	-monitor stdio \
	-vga vmware
