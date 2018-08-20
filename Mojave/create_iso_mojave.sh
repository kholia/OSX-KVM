#!/usr/bin/env bash

# Bail at first ISO creation error
set -e

# Borrrowed from multiple internet sources
hdiutil create -o ~/Desktop/Mojave.cdr -size 6g -layout SPUD -fs HFS+J
hdiutil attach ~/Desktop/Mojave.cdr.dmg -noverify -mountpoint /Volumes/install_build
sudo /Applications/Install\ macOS\ Mojave\ Beta.app/Contents/Resources/createinstallmedia --volume /Volumes/install_build --nointeraction
hdiutil detach "/Volumes/Install macOS Mojave Beta"
hdiutil convert ~/Desktop/Mojave.cdr.dmg -format UDTO -o ~/Desktop/Mojave.iso
mv ~/Desktop/Mojave.iso.cdr ~/Desktop/Mojave.iso
rm ~/Desktop/Mojave.cdr.dmg
