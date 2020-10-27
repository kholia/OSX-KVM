### Developing on Virtualized OSX

#### THIS IS THE BASIC SETUP PROCESS AND IS STILL BEING TESTED. IT WILL VARY FROM SYSTEM TO SYSTEM AND IS COMPILED USING PRIOR KNOWLEDGE AND OTHER NOTES IN THIS REPOSITORY.

- Step 1: Install XCode: This is a simple process, involving either installing fromt the App Store or downloading XCode from the [Apple developer website](https://developers.apple.com).

- Step 2: Create an XCode project: Since this isn't specific to this guide, it will not be explained in-depth. There are many ways to create an XCode project involving creating one in XCode or importing one from something like Unity.

- Step 3: Passing through the device you're building too: This is covered in these [notes](notes.md#usb-passthrough-notes), which explains how to passthrough an entire USB controller. If you're building for iOS, you can pass through an iPhone to build on.

- Step 4: Build and Test: Now that your virtualized OSX system has an XCode project and access to the device you plan to build to, you can finally use it as a regular computer running macOS.
