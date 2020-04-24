#!/usr/bin/env bash

# All credits for OpenCore support go to https://github.com/Leoyzen/KVM-Opencore and
# https://github.com/thenickdude/KVM-Opencore/. Thanks!


# qemu-img create -f qcow2 mac_hdd_ng.img 128G
#
# echo 1 > /sys/module/kvm/parameters/ignore_msrs (this is required)

############################################################################
# NOTE: Tweak the "MY_OPTIONS" line in case you are having booting problems!
############################################################################

# This works for Catalina as well as Mojave. Tested with macOS 10.14.6 and macOS 10.15.

MY_OPTIONS="+pcid,+ssse3,+sse4.2,+popcnt,+avx,+aes,+xsave,+xsaveopt,check"

# OVMF=./firmware
OVMF="./"

# This causes high cpu usage on the *host* side
# qemu-system-x86_64 -enable-kvm -m 3072 -cpu Penryn,vendor=GenuineIntel,+invtsc,vmware-cpuid-freq=on,hypervisor=off,vmx=on,kvm=off,$MY_OPTIONS\

qemu-system-x86_64 -enable-kvm -m 3072 -cpu Penryn,kvm=on,vendor=GenuineIntel,+invtsc,vmware-cpuid-freq=on,$MY_OPTIONS\
	  -machine q35 \
	  -smp 4,cores=2 \
	  -usb -device usb-kbd -device usb-mouse \
	  -device isa-applesmc,osk="ourhardworkbythesewordsguardedpleasedontsteal(c)AppleComputerInc" \
	  -drive if=pflash,format=raw,readonly,file=$OVMF/OVMF_CODE.fd \
	  -drive if=pflash,format=raw,file=$OVMF/OVMF_VARS-1024x768.fd \
	  -smbios type=2 \
	  -device ich9-intel-hda -device hda-duplex \
	  -device ich9-ahci,id=sata \
	  -drive id=OpenCoreBoot,if=none,snapshot=on,format=qcow2,file=./'OpenCore-Catalina/OpenCore.qcow2' \
	  -device ide-hd,bus=sata.2,drive=OpenCoreBoot \
	  -device ide-hd,bus=sata.3,drive=InstallMedia \
	  -drive id=InstallMedia,if=none,file=BaseSystem.img,format=raw \
	  -drive id=MacHDD,if=none,file=./mac_hdd_ng.img,format=qcow2 \
	  -device ide-hd,bus=sata.4,drive=MacHDD \
	  -netdev tap,id=net0,ifname=tap0,script=no,downscript=no -device vmxnet3,netdev=net0,id=net0,mac=52:54:00:c9:18:27 \
	  -monitor stdio \
	  -vga vmware
