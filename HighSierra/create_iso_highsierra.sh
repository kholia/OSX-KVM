#!/usr/bin/env bash

# Bail at first High Sierra ISO creation error
set -e

if [ "$#" -ne 2 ]
then
    echo "Illegal number of parameters"
    echo "Usage: create_iso_highsierra.sh <path/to/install_app.app> <path/to/output_iso_file.iso>"
    exit 1
fi

in_path=$1
iso_path=$2

# Borrrowed from multiple internet sources
hdiutil create -o "$iso_path.cdr" -size 5600m -layout SPUD -fs HFS+J
hdiutil attach "$iso_path.cdr.dmg" -noverify -mountpoint /Volumes/install_build
sudo "$in_path/Contents/Resources/createinstallmedia" --volume /Volumes/install_build --nointeraction
hdiutil detach "/Volumes/Install macOS High Sierra"

# hdiutil convert will actually put the output file at $iso_path.cdr
hdiutil convert "$iso_path.cdr.dmg" -format UDTO -o "$iso_path"

mv "$iso_path.cdr" "$iso_path"
rm "$iso_path.cdr.dmg"
