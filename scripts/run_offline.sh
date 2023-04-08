#!/usr/bin/env bash

cd /Volumes/macOS
mkdir -p private/tmp
cp -R "/Install macOS Ventura.app" private/tmp
cd "private/tmp/Install macOS Ventura.app"
mkdir Contents/SharedSupport
cp -R /Volumes/InstallAssistant/InstallAssistant.pkg Contents/SharedSupport/SharedSupport.dmg
./Contents/MacOS/InstallAssistant_springboard
