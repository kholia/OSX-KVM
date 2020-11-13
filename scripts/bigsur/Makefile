# Builds either a recovery image (BigSur-recovery.img) or a full installer (BigSur-full.img) for Big Sur.

# To build the full installer you must run this on macOS.
# The recovery can be built on either macOS or Linux.

# For Ubuntu (or similar Linux distribution) you'll need to run this first to get the required packages:
# sudo apt install git qemu-utils p7zip-full -y

# For macOS you'll probably need to run xcode-select --install to get the commandline tools

BIG_SUR_APP=/Applications/Install\ macOS\ Big\ Sur.app

LINUX_TOOLS = qemu-img git

OS :=
UNAME_S := $(shell uname -s)

ifeq ($(UNAME_S),Darwin)
	OS = MACOS
endif

# If this is Linux make sure we have all our build tools available:
ifeq ($(OS),)
	K := $(foreach exec,$(LINUX_TOOLS),\
			$(if $(shell which $(exec)),some string,$(error "Missing required $(exec) tool for build")))
endif

all: BigSur-recovery.img

BigSur-full.img : BigSur-full.dmg
	mv $< $@

ifeq ($(OS),MACOS)
BigSur-full.dmg : $(BIG_SUR_APP)
	hdiutil create -o "$@" -size 14g -layout GPTSPUD -fs HFS+J
	hdiutil attach -noverify -mountpoint /Volumes/install_build "$@"
	sudo "$</Contents/Resources/createinstallmedia" --volume /Volumes/install_build --nointeraction

	# createinstallmedia leaves a bunch of subvolumes still mounted when it exits, so we need to use -force here.
	hdiutil detach -force "/Volumes/Install macOS Big Sur"
else
BigSur-full.dmg :
	$(error "Building a full installer requires this script to be run on macOS, build BigSur-recovery.img instead")
endif

$(BIG_SUR_APP) : InstallAssistant.pkg
	sudo installer -pkg $< -target /

BigSur-recovery.img : BaseSystem.dmg
ifeq ($(OS),MACOS)
	hdiutil convert $< -format RdWr -o $@
else
	qemu-img convert $< -O raw $@
endif

ifeq ($(OS),MACOS)
BaseSystem.dmg : SharedSupport.dmg
	hdiutil detach -force .bigsur-package-tmp || true
	rm -rf .bigsur-package-tmp
	mkdir .bigsur-package-tmp
	hdiutil attach -quiet -nobrowse -mountpoint .bigsur-package-tmp $<
	tar -O -xf .bigsur-package-tmp/com_apple_MobileAsset_MacSoftwareUpdate/*.zip AssetData/Restore/BaseSystem.dmg > BaseSystem.dmg
	hdiutil detach -force .bigsur-package-tmp
	rm -rf .bigsur-package-tmp
else
BaseSystem.dmg : SharedSupport.dmg
	umount .bigsur-package-tmp 2>/dev/null || true
	rm -rf .bigsur-package-tmp 2>/dev/null
	mkdir .bigsur-package-tmp

	7z e -txar InstallAssistant.pkg '*.dmg'
	7z e -tdmg SharedSupport.dmg 5.hfs
	sudo mount -oloop *.hfs .bigsur-package-tmp
	7z e .bigsur-package-tmp/*MacSoftwareUpdate/*.zip AssetData/Restore/Base*.dmg
endif

SharedSupport.dmg : InstallAssistant.pkg
	touch $@

InstallAssistant.pkg :
	../../fetch-macOS.py --version 11.0.1
