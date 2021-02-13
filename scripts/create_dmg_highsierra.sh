#!/usr/bin/env bash

# Create a "ISO" (DMG) image for powering offline macOS installations

# Bail at first ISO creation error
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
    dmg_path=$2
elif [ "$#" -eq 0 ]
then
    in_path=/Applications/Install\ macOS\ High\ Sierra.app
    dmg_path=~/Desktop/HighSierra.dmg
    echo "Using default paths:"
    echo "Install app: $in_path"
    echo "Output disk: $dmg_path"
else
    display_help
fi

# Borrrowed from multiple internet sources
hdiutil create -o "$dmg_path" -size 5600m -layout GPTSPUD -fs HFS+J
hdiutil attach "$dmg_path" -noverify -mountpoint /Volumes/install_build
sudo "$in_path/Contents/Resources/createinstallmedia" --volume /Volumes/install_build --nointeraction

# createinstallmedia may leave a bunch of subvolumes still mounted when it exits, so we need to use -force here.
hdiutil detach -force "/Volumes/Install macOS High Sierra"
