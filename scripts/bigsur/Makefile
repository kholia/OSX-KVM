# Builds either a recovery image (BigSur-recovery.img) or a full installer (BigSur-full.img) for Big Sur.

# To build the full installer you must run this on macOS.
# The recovery can be built on either macOS or Linux.

# For Ubuntu (or similar Linux distribution) you'll need to run this first to get the required packages:
# sudo apt install qemu-utils make

# For macOS you'll probably need to run xcode-select --install to get the commandline tools

BIG_SUR_APP=/Applications/Install\ macOS\ Big\ Sur.app

LINUX_TOOLS = qemu-img

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

%.img : %.dmg
	ln $< $@ || cp $< $@

ifeq ($(OS),MACOS)
BigSur-full.dmg : $(BIG_SUR_APP)
	hdiutil create -o "$@" -size 14g -layout GPTSPUD -fs HFS+J
	hdiutil attach -noverify -mountpoint /Volumes/install_build "$@"
	sudo "$</Contents/Resources/createinstallmedia" --volume /Volumes/install_build --nointeraction

	# createinstallmedia leaves a bunch of subvolumes still mounted when it exits, so we need to use -force here.
	hdiutil detach -force "/Volumes/Install macOS Big Sur"
else
BigSur-full.dmg :
	$(error "Building a full installer requires this script to be run on macOS, run 'make BigSur-recovery.img' instead")
endif

$(BIG_SUR_APP) : InstallAssistant.pkg
	sudo installer -pkg $< -target /

BigSur-recovery.dmg : com.apple.recovery.boot/BaseSystem.dmg
	rm -f $@
ifeq ($(OS),MACOS)
	hdiutil convert $< -format UDRW -o $@
else
	qemu-img convert $< -O raw $@
endif

com.apple.recovery.boot/BaseSystem.dmg :
	../../fetch-macOS-v2.py --action download --board-id Mac-2BD1B31983FE1663

InstallAssistant.pkg :
	../../backups/fetch-macOS.py --version latest --title "macOS Big Sur"

clean :
	rm -f SharedSupport.dmg InstallAssistant.pkg BigSur-recovery.img BigSur-full.img
	rm -rf content com.apple.recovery.boot
