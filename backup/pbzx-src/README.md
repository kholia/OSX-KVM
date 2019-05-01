# Building pbzx from scratch

A decent version of Xcode is required to builz pbzx. Xcode is available for
free in Apple's App Store.

## Building

Simply run
```bash
make
```
This first downloads, configures and builds a static version of liblzma
and then builds the pbxz binary itself.

The following false libtool warning can be safely ignored:

`libtool: warning: remember to run 'libtool --finish /usr/lib'`
