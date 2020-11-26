### Developing on Virtualized OSX

#### THIS IS THE BASIC SETUP PROCESS AND IS STILL BEING TESTED. IT WILL VARY FROM SYSTEM TO SYSTEM AND IS COMPILED USING PRIOR KNOWLEDGE AND OTHER NOTES IN THIS REPOSITORY.

- Step 1: Install XCode: This is a simple process, involving either installing fromt the App Store or downloading XCode from the [Apple developer website](https://developers.apple.com).

- Step 2: Create an XCode project: Since this isn't specific to this guide, it will not be explained in-depth. There are many ways to create an XCode project involving creating one in XCode or importing one from something like Unity.

- Step 3: Passing through the device you're building too: This is covered in these [notes](notes.md#usb-passthrough-notes), which explains how to passthrough an entire USB controller. If that's not an option, a paid software exists called [USB Network Gate](https://www.eltima.com/products/usb-over-ethernet/), which comes with a free trial and allows you to pass USB devices to your VM over the LAN. The file types that they provide are file types for macOS, Windows, as well as Linux .DEB and .RPM packages. If your operating system is not supported (e.g. Arch Linux), you can pick up a cheap Raspberry Pi and download the [Debian ARMv7
 version](https://cdn.electronic.us/products/usb-over-ethernet/linux/download/eveusb_armv7l.deb?_ga=2.69646291.2132765699.1606368918-411227281.1606368918). Once you have it installed on the host computer (the one with the USB device that you'll be sharing), you can install it on the virtualized macOS machine. Make sure to allow the extension in System Preferences>Security and Privacy and reboot. Once that's finished, you can open up `USB Network Gate` on the client (macOS) and click `Add Server` and type in the IP address of the Raspberry Pi or other device. Finally, you have to trust the computer on you iPhone, and it should be completely set up! It should work completely normally - showing up in Finder, XCode, etc.

- Step 4: Build and Test: Now that your virtualized OSX system has an XCode project and access to the device you plan to build to, you can finally use it as a regular computer running macOS, with an iPhone, iPad, or other device attached.
