{
  description = "OSX-KVM allows to run macOS on Linux machines";

  inputs.nixpkgs.url = "nixpkgs/22.11";
  inputs.flake-utils.url = "github:numtide/flake-utils";
  inputs.osx-kvm.url = "path:./";
  inputs.osx-kvm.flake = false;

  outputs = { self, nixpkgs, flake-utils, osx-kvm }:

    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};

        start =
          pkgs.writeShellScriptBin "start" ''
            set -e
            if [ ! -e BaseSystem.dmg ];then
              ${pkgs.python3}/bin/python ${osx-kvm}/fetch-macOS-v2.py
            fi
            if [ ! -e BaseSystem.img ];then
              ${pkgs.qemu}/bin/qemu-img convert BaseSystem.dmg -O raw BaseSystem.img
            fi
            if [ ! -e mac_hdd_ng.img ];then
              ${pkgs.qemu}/bin/qemu-img create -f qcow2 mac_hdd_ng.img 128G
            fi
            source ${osx-kvm}/OpenCore-Boot.sh
          '';
      in
      {
        packages = { inherit start; };
        defaultPackage = start;
      });
}
