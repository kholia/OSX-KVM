# Builds either a recovery image (Ventura-recovery.img) or a full installer (Ventura-full.img) for Ventura.

# To build the full installer you must run this on macOS.
# The recovery can be built on either macOS or Linux.

# For Ubuntu (or similar Linux distribution) you'll need to run this first to get the required packages:
# sudo apt install qemu-utils make

# For macOS you'll probably need to run xcode-select --install to get the commandline tools

VENTURA_APP=/Applications/Install\ macOS\ Ventura.app

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

all: Ventura-recovery.img

%.img : %.dmg
	ln $< $@ || cp $< $@

ifeq ($(OS),MACOS)

Ventura-full.dmg : $(VENTURA_APP)
	hdiutil create -o "$@" -size 14g -layout GPTSPUD -fs HFS+J
	hdiutil attach -noverify -mountpoint /Volumes/install_build "$@"
	sudo "$</Contents/Resources/createinstallmedia" --volume /Volumes/install_build --nointeraction
	hdiutil detach "/Volumes/Install macOS Ventura"

# Avoid redownloading Ventura if the app already exists
ifeq (,$(wildcard $(VENTURA_APP)))
$(VENTURA_APP) : InstallAssistant.pkg
	sudo installer -pkg $< -target /
endif

else

Ventura-full.dmg :
	$(error "Building a full installer requires this script to be run on macOS, run 'make Ventura-recovery.img' instead")

endif

Ventura-recovery.dmg : BaseSystem.dmg
	rm -f $@
ifeq ($(OS),MACOS)
	hdiutil convert $< -format UDRW -o $@
else
	qemu-img convert $< -O raw $@
endif

BaseSystem.dmg :
	../../fetch-macOS-v2.py --action download --board-id Mac-AF89B6D9451A490B --os latest

InstallAssistant.pkg :
	../../backups/fetch-macOS.py --version latest --title "macOS Ventura"

clean :
	rm -f BaseSystem.chunklist BaseSystem.dmg SharedSupport.dmg InstallAssistant.pkg Ventura-recovery.img Ventura-full.img Ventura-recovery.dmg Ventura-full.dmg
	rm -rf content
