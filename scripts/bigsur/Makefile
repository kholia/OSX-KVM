# Builds either a recovery image (BigSur-recovery.img) or a full installer (BigSur-full.img) for Big Sur.

# To build the full installer you must run this on macOS. 
# The recovery can be built on either macOS or Linux.

# For Ubuntu (or similar Linux distribution) you'll need to run this first to get the required packages:
# sudo apt install g++ git qemu-utils libxml2-dev libssl-dev zlib1g-dev cmake libbz2-dev libfuse-dev fuse autoconf unzip

# For macOS you'll probably need to run xcode-select --install to get the commandline tools

BIG_SUR_APP=/Applications/Install\ macOS\ Big\ Sur.app

LINUX_TOOLS = qemu-img git cmake autoconf

OS := 
UNAME_S := $(shell uname -s)

ifeq ($(UNAME_S),Darwin)
	OS = MACOS
endif

# Use systemwide xar/darling-img if available:
XAR := $(shell which xar)
DARLING := $(shell which darling-dmg)

# Otherwise we'll build them from source:
ifeq ($(XAR),)
XAR = xar/xar/src/xar
endif

ifeq ($(DARLING),)
DARLING = darling-dmg/darling-dmg
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
BaseSystem.dmg : SharedSupport.dmg $(DARLING)
	umount .bigsur-package-tmp || true
	rm -rf .bigsur-package-tmp
	mkdir .bigsur-package-tmp
	$(DARLING) $< .bigsur-package-tmp
	unzip -p ".bigsur-package-tmp/com_apple_MobileAsset_MacSoftwareUpdate/*.zip" AssetData/Restore/BaseSystem.dmg > BaseSystem.dmg
	umount .bigsur-package-tmp
	rm -rf .bigsur-package-tmp
endif

SharedSupport.dmg : InstallAssistant.pkg $(XAR)
	$(XAR) -xf $< $@
	touch $@

InstallAssistant.pkg :
	../../fetch-macOS.py --version 11.0.1

xar/xar/src/xar : xar/
	cd xar/xar && ./autogen.sh
	cd xar/xar && make

xar/ :
	git clone https://github.com/VantaInc/xar.git

darling-dmg/darling-dmg : darling-dmg/
	cd darling-dmg && cmake .
	cd darling-dmg && make

darling-dmg/ :
	git clone https://github.com/darlinghq/darling-dmg.git
