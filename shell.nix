with import <nixpkgs> {};
mkShell {
  buildInputs = [
    qemu
    python
    vncdo
    tightvnc
    imagemagick
    libcaca
  ];
}
