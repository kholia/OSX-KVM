#!/bin/bash

NAME=mac$1
MAC_DIGIT=$(printf "%02x" $1)

mkdir -p $NAME
cp -rp OVMF_CODE.fd $NAME
cp -rp OVMF_VARS-1024x768.fd $NAME
cp -rp OpenCore-Catalina/OpenCore.qcow2 $NAME
qemu-img create -f qcow2 -F qcow2 -b ../mac_hdd_ng.img $NAME/$NAME.img
sed -n "s/|NUMBER|/$1/g;s/|MAC_DIGIT|/$MAC_DIGIT/g;w $NAME/macOS-libvirt-Catalina_$1.xml" macOS-libvirt-Catalina.templ
virsh --connect qemu:///system define $NAME/macOS-libvirt-Catalina_$1.xml
