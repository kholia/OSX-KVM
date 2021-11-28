# export SHORTNAME=monterey
DISK_SIZE := 256G

all: BaseSystem.img mac_hdd_ng.img

BaseSystem.img: BaseSystem.dmg
	qemu-img convert BaseSystem.dmg -O raw BaseSystem.img

BaseSystem.dmg:
	./fetch-macOS-v2.py --short=$(SHORTNAME)

mac_hdd_ng.img:
	qemu-img create -f qcow2 mac_hdd_ng.img ${DISK_SIZE}

clean:
	rm -rf BaseSystem{.dmg,.img,.chunklist}
