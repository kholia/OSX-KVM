# Builds a full installer (Monterey-full.img) for Monterey Developer Beta.

# You need to opt-in to the Developer beta program first and get the Monterey installer app using System Update

MONTEREY_APP=/Applications/Install\ macOS\ 12\ Beta.app

all: Monterey-full.img

%.img : %.dmg
	ln $< $@ || cp $< $@

Monterey-full.dmg : $(MONTEREY_APP)
	hdiutil create -o "$@" -size 14g -layout GPTSPUD -fs HFS+J
	hdiutil attach -noverify -mountpoint /Volumes/install_build "$@"
	sudo "$</Contents/Resources/createinstallmedia" --volume /Volumes/install_build --nointeraction
	hdiutil detach "/Volumes/Install macOS 12 Beta"

clean :
	rm -f Monterey-recovery.img Monterey-full.img
