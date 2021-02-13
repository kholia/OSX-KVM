#!/bin/sh

# mafferri (https://bbs.archlinux.org)

if [ ! -e /sys/kernel/iommu_groups/$1 ]; then
	echo "IOMMU group $1 not found"
	exit 1
fi

if [ ! -e /sys/bus/pci/drivers/vfio-pci ]; then
	sudo modprobe vfio-pci
fi

for i in $(ls /sys/kernel/iommu_groups/$1/devices/); do
	if [ -e /sys/kernel/iommu_groups/$1/devices/$i/driver ]; then
		if [ "$(basename $(readlink -f \
			/sys/kernel/iommu_groups/$1/devices/$i/driver))" != \
			"pcieport" ]; then
			echo $i | sudo tee \
				/sys/kernel/iommu_groups/$1/devices/$i/driver/unbind
		fi
	fi
done

for i in $(ls /sys/kernel/iommu_groups/$1/devices/); do
	if [ ! -e /sys/kernel/iommu_groups/$1/devices/$i/driver ]; then
		VEN=$(cat /sys/kernel/iommu_groups/$1/devices/$i/vendor)
		DEV=$(cat /sys/kernel/iommu_groups/$1/devices/$i/device)
		echo $VEN $DEV | sudo tee \
			/sys/bus/pci/drivers/vfio-pci/new_id
	fi
done
