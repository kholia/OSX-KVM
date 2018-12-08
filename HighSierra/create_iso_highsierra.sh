#!/usr/bin/env bash

# Bail at first High Sierra ISO creation error
set -e

display_help() {
    echo "Usage: $(basename $0) [-h] [<path/to/install_app.app> <path/to/output_iso_file.iso>]"
    exit 0
}

if [ "$1" == "-h" ] ; then
    display_help
fi

if [ "$#" -eq 2 ]
then
    in_path=$1
    iso_path=$2
elif [ "$#" -eq 0 ]
then
    in_path=/Applications/Install\ macOS\ High\ Sierra.app
    iso_path=~/Desktop/HighSierra.iso
    echo "Using default paths:"
    echo "Install app: $in_path"
    echo "Output disk: $iso_path"
else
    display_help
fi

# Borrrowed from multiple internet sources
hdiutil create -o "$iso_path.cdr" -size 5600m -layout SPUD -fs HFS+J
hdiutil attach "$iso_path.cdr.dmg" -noverify -mountpoint /Volumes/install_build
sudo "$in_path/Contents/Resources/createinstallmedia" --volume /Volumes/install_build --nointeraction
hdiutil detach "/Volumes/Install macOS High Sierra"

# hdiutil convert will actually put the output file at $iso_path.cdr
hdiutil convert "$iso_path.cdr.dmg" -format UDTO -o "$iso_path"

mv "$iso_path.cdr" "$iso_path"
rm "$iso_path.cdr.dmg"
