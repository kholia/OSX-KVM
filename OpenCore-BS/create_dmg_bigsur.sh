#!/usr/bin/env bash

# Create a DMG from the Big Sur Beta 3 installer app

# Bail at first DMG creation error
set -e

display_help() {
    echo "Usage: $(basename $0) [-h] [<path/to/install_app.app> <path/to/output_dmg_file.dmg>]"
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
    in_path=/Applications/Install\ macOS\ Big\ Sur\ Beta.app
    dmg_path=~/Desktop/BigSurBeta.dmg
    echo "Using default paths:"
    echo "Install app: $in_path"
    echo "Output disk: $dmg_path"
else
    display_help
fi

hdiutil create -o "$dmg_path" -size 14g -layout GPTSPUD -fs HFS+J
hdiutil attach "$dmg_path" -noverify -mountpoint /Volumes/install_build
sudo "$in_path/Contents/Resources/createinstallmedia" --volume /Volumes/install_build --nointeraction

# createinstallmedia  leaves a bunch of subvolumes still mounted when it exits, so we need to use -force here.
# This might be fixed in a later Beta release:
hdiutil detach -force "/Volumes/Install macOS Big Sur Beta"
