#!/bin/sh

# mafferri (https://bbs.archlinux.org)

if [ ! -e /sys/kernel/iommu_groups/$1 ]; then
	echo "IOMMU group $1 not found"
	exit 1
fi

for i in $(ls /sys/kernel/iommu_groups/$1/devices/); do
	VEN=$(cat /sys/kernel/iommu_groups/$1/devices/$i/vendor)
	DEV=$(cat /sys/kernel/iommu_groups/$1/devices/$i/device)
	echo $VEN $DEV | sudo tee \
		/sys/bus/pci/drivers/vfio-pci/remove_id
	echo $i | sudo tee \
		/sys/kernel/iommu_groups/$1/devices/$i/driver/unbind
done

for i in $(ls /sys/kernel/iommu_groups/$1/devices/); do
	echo $i | sudo tee /sys/bus/pci/drivers_probe
done
