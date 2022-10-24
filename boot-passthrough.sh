#!/usr/bin/env bash

# Special thanks to:
# https://github.com/Leoyzen/KVM-Opencore
# https://github.com/thenickdude/KVM-Opencore/
# https://github.com/qemu/qemu/blob/master/docs/usb2.txt
#
# qemu-img create -f qcow2 mac_hdd_ng.img 128G
#
# echo 1 > /sys/module/kvm/parameters/ignore_msrs (this is required)
#
############################################################################
# NOTE: Tweak the "MY_OPTIONS" line in case you are having booting problems!
############################################################################
#
# VNC Usage:
#
# $ ./boot-passthrough.sh
#
# Set your desired VNC password below.
#
# (qemu) change vnc password
# Password: ********

MY_OPTIONS="+ssse3,+sse4.2,+popcnt,+avx,+aes,+xsave,+xsaveopt,check"

# This script works for Big Sur, Catalina, Mojave, and High Sierra. Tested with
# macOS 10.15.6, macOS 10.14.6, and macOS 10.13.6

ALLOCATED_RAM="3072" # MiB
CPU_SOCKETS="1"
CPU_CORES="2"
CPU_THREADS="4"

REPO_PATH="."
OVMF_DIR="."

# Note: This script assumes that you are doing CPU + GPU passthrough. This
# script will need to be modified for your specific needs!
#
# We recommend doing the initial macOS installation without using passthrough
# stuff. In other words, don't use this script for the initial macOS
# installation.

# shellcheck disable=SC2054
args=(
  -enable-kvm -m "$ALLOCATED_RAM" -cpu Penryn,kvm=on,vendor=GenuineIntel,+invtsc,vmware-cpuid-freq=on,"$MY_OPTIONS"
  -machine q35
  -usb -device usb-kbd -device usb-tablet -device usb-mouse
  -smp "$CPU_THREADS",cores="$CPU_CORES",sockets="$CPU_SOCKETS"
  -device usb-ehci,id=ehci
  -vga none
  # 01:00.0 VGA compatible controller [0300]: Advanced Micro Devices, Inc. [AMD/ATI] Ellesmere [Radeon RX 470/480/570/570X/580/580X/590] [1002:67df] (rev ef)
  #         Subsystem: Sapphire Technology Limited Nitro+ Radeon RX 570/580/590 [1da2:e366]
  # 01:00.1 Audio device [0403]: Advanced Micro Devices, Inc. [AMD/ATI] Ellesmere HDMI Audio [Radeon RX 470/480 / 570/580/590] [1002:aaf0]
  #         Subsystem: Sapphire Technology Limited Ellesmere HDMI Audio [Radeon RX 470/480 / 570/580/590] [1da2:aaf0]
  -device vfio-pci,host=01:00.0,multifunction=on,x-no-kvm-intx=on
  # -device vfio-pci,host=01:00.0,multifunction=on,romfile=gpu_original_bios.bin
  -device vfio-pci,host=01:00.1
  # ASMedia ASM1142 USB 3.1 Host Controller (comment out as needed)
  # 03:00.0 USB controller [0c03]: ASMedia Technology Inc. ASM1142 USB 3.1 Host Controller [1b21:1242]
  # -device vfio-pci,host=03:00.0,bus=pcie.0
  -device isa-applesmc,osk="ourhardworkbythesewordsguardedpleasedontsteal(c)AppleComputerInc"
  -drive if=pflash,format=raw,readonly=on,file="$REPO_PATH/$OVMF_DIR/OVMF_CODE.fd"
  -drive if=pflash,format=raw,file="$REPO_PATH/$OVMF_DIR/OVMF_VARS-1024x768.fd"
  -smbios type=2
  -device ich9-intel-hda -device hda-duplex
  -device ich9-ahci,id=sata
  -drive id=OpenCoreBoot,if=none,snapshot=on,format=qcow2,file="$REPO_PATH/OpenCore/OpenCore.qcow2"
  -device ide-hd,bus=sata.2,drive=OpenCoreBoot
  -device ide-hd,bus=sata.3,drive=InstallMedia
  -drive id=InstallMedia,if=none,file="$REPO_PATH/BaseSystem.img",format=raw
  -drive id=MacHDD,if=none,file="$REPO_PATH/mac_hdd_ng.img",format=qcow2
  -device ide-hd,bus=sata.4,drive=MacHDD
  # -netdev tap,id=net0,ifname=tap0,script=no,downscript=no -device vmxnet3,netdev=net0,id=net0,mac=52:54:00:c9:18:27
  -netdev user,id=net0 -device vmxnet3,netdev=net0,id=net0,mac=52:54:00:c9:18:27
  -monitor stdio
  -display none
  # -object input-linux,id=kbd1,evdev=/dev/input/by-id/usb-SEMITEK_USB-HID_Gaming_Keyboard_SN0000000001-event-kbd,grab_all=on,repeat=on
  # -object input-linux,id=mouse1,evdev=/dev/input/by-id/usb-PixArt_Dell_MS116_USB_Optical_Mouse-event-mouse
  -vnc 0.0.0.0:1,password -k en-us
)

qemu-system-x86_64 "${args[@]}"
