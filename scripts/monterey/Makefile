# Builds either a recovery image (Monterey-recovery.img) or a full installer (Monterey-full.img) for Monterey.

# To build the full installer you must run this on macOS.
# The recovery can be built on either macOS or Linux.

# For Ubuntu (or similar Linux distribution) you'll need to run this first to get the required packages:
# sudo apt install qemu-utils make

# For macOS you'll probably need to run xcode-select --install to get the commandline tools

MONTEREY_APP=/Applications/Install\ macOS\ Monterey.app

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

all: Monterey-recovery.img

%.img : %.dmg
	ln $< $@ || cp $< $@

ifeq ($(OS),MACOS)
Monterey-full.dmg : $(MONTEREY_APP)
	hdiutil create -o "$@" -size 14g -layout GPTSPUD -fs HFS+J
	hdiutil attach -noverify -mountpoint /Volumes/install_build "$@"
	sudo "$</Contents/Resources/createinstallmedia" --volume /Volumes/install_build --nointeraction
	hdiutil detach "/Volumes/Install macOS Monterey"
else
Monterey-full.dmg :
	$(error "Building a full installer requires this script to be run on macOS, run 'make Monterey-recovery.img' instead")
endif

$(MONTEREY_APP) : InstallAssistant.pkg
	sudo installer -pkg $< -target /

Monterey-recovery.dmg : BaseSystem.dmg
	rm -f $@
ifeq ($(OS),MACOS)
	hdiutil convert $< -format UDRW -o $@
else
	qemu-img convert $< -O raw $@
endif

BaseSystem.dmg :
	../../fetch-macOS-v2.py --action download --board-id Mac-7BA5B2D9E42DDD94 --os latest

InstallAssistant.pkg :
	../../backups/fetch-macOS.py --version latest --title "macOS Monterey"

clean :
	rm -f BaseSystem.chunklist BaseSystem.dmg SharedSupport.dmg InstallAssistant.pkg Monterey-recovery.img Monterey-full.img
	rm -rf content
