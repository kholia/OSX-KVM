#!/usr/bin/env bash

# run-diagnostics.sh: checks common virtualization programs, modules and
# options. Written by Foxlet <foxlet@furcode.co>. Modified by Dhiru for OSX-KVM
# project.
#
# Note: This script is borrowed from https://github.com/foxlet/macOS-Simple-KVM
# project.

echo "== Distro Info ==" >&2
lsb_release -a 2>/dev/null

echo -e "\n== Loaded Modules ==" >&2
lsmod | grep kvm
lsmod | grep amd_iommu
lsmod | grep intel_iommu
v=$(cat /sys/module/kvm/parameters/ignore_msrs)
if [ "$v" != "Y" ]; then
	echo -e "\nATTENTION: /sys/module/kvm/parameters/ignore_msrs setting seems to be incorrect!"
fi

echo -e "\n== Installed Binaries ==" >&2
if [ -x "$(command -v qemu-system-x86_64)" ]; then
	qemu-system-x86_64 --version
else
	echo -e "qemu is not installed." >&2
fi

if [ -x "$(command -v virt-manager)" ]; then
	echo -e "virt-manager version $(virt-manager --version)"
else
	echo -e "virt-manager is not installed." >&2
fi

if [ -x "$(command -v python)" ]; then
	python --version
else
	echo -e "python is not installed." >&2
fi

echo -e "\n== Networking ==" >&2
ip link show virbr0 >/dev/null 2>&1
if [ "$?" != 0 ]; then
	echo -e "Interface virbr0 doesn't seem to exist. Check your networking configuration." >&2
else
	echo -e "Found virbr0. Good."
fi
