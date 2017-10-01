#!/bin/bash

# qemu-img create -f qcow2 mac_hdd.img 128G
#
# echo 1 > /sys/module/kvm/parameters/ignore_msrs (this is required)
#
# printf 'DE:AD:BE:EF:%02X:%02X\n' $((RANDOM%256)) $((RANDOM%256))
#
# no_floppy = 1 is required for OS X guests!
#
# Commit 473a49460db0a90bfda046b8f3662b49f94098eb (qemu) makes "no_floppy = 0"
# for pc-q35-2.3 hardware, and OS X doesn't like this (it hangs at "Waiting for
# DSMOS" message). Hence, we switch to pc-q35-2.4 hardware.
#
# Network device "-device e1000-82545em" can be replaced with "-device vmxnet3"
# for possibly better performance.
#
# Use "-device usb-tablet" instead of "-device usb-mouse" for better mouse
# behaviour. This requires QEMU >= 2.9.0.

qemu-system-x86_64 -enable-kvm -m 3072 -cpu Penryn,kvm=off,vendor=GenuineIntel \
	  -machine pc-q35-2.4 \
	  -smp 4,cores=2 \
	  -usb -device usb-kbd -device usb-mouse \
	  -device isa-applesmc,osk="ourhardworkbythesewordsguardedpleasedontsteal(c)AppleComputerInc" \
	  -kernel ./enoch_rev2902_boot \
	  -smbios type=2 \
	  -device ich9-intel-hda -device hda-duplex \
	  -device ide-drive,bus=ide.2,drive=MacHDD \
	  -drive id=MacHDD,if=none,file=./mac_hdd.img \
	  -netdev tap,id=net0,ifname=tap0,script=no,downscript=no -device e1000-82545em,netdev=net0,id=net0,mac=52:54:00:c9:18:27 \
	  -monitor stdio \
	  -device ide-drive,bus=ide.0,drive=MacDVD \
	  -drive id=MacDVD,if=none,snapshot=on,file=./'Install_macOS_10.12.6_Sierra.iso'
	  # -vnc 0.0.0.0:0 -k en-us \
	  # -redir tcp:5901::5900 \
	  # -netdev user,id=hub0port0 -device e1000-82545em,netdev=hub0port0,id=mac_vnet0 \
