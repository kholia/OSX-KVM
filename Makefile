DISK_SIZE := 128G

all: BaseSystem.img mac_hdd_ng.img

BaseSystem.img: BaseSystem.dmg
	qemu-img convert BaseSystem.dmg -O raw BaseSystem.img

BaseSystem.dmg:
	./fetch-macOS-v2.py

mac_hdd_ng.img:
	qemu-img create -f qcow2 mac_hdd_ng.img ${DISK_SIZE}

clean:
	rm -rf BaseSystem{.dmg,.img,.chunklist}
