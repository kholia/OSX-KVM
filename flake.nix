{
  inputs.nixpkgs.url = "github:nixos/nixpkgs/nixpkgs-unstable";

  inputs.flake-utils.url = "github:numtide/flake-utils";

  outputs =
    { self
    , nixpkgs
    , flake-utils
    ,
    }:
    flake-utils.lib.eachDefaultSystem (
      system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        src = pkgs.fetchFromGitHub {
          owner = "kholia";
          repo = "OSX-KVM";
          rev = "master";
          hash = "sha256-kxhVe3U2lFt6joSMUGWZuHOfFHdzwKXP4H3hz/cA2vE=";
        };
      in
      {
        devShells.default = pkgs.mkShell {
          nativeBuildInputs = with pkgs.buildPackages; [
            python3
            dmg2img
            qemu_kvm
          ];
        };
        apps.default = {
          type = "app";
          program = toString (pkgs.writeShellScript "build-osx" ''
            name=$1
            ${pkgs.coreutils}/bin/mkdir ./OSX-KVM 
            ${pkgs.coreutils}/bin/cp -r --no-preserve=mode ${src}/* ./OSX-KVM
            ${pkgs.coreutils}/bin/chmod -R +w ./OSX-KVM
            ${pkgs.coreutils}/bin/chmod -R +x ./OSX-KVM/*.sh
            cd ./OSX-KVM
            ${pkgs.python3}/bin/python3 ./fetch-macOS-v2.py --shortname=$name
            ${pkgs.dmg2img}/bin/dmg2img -i BaseSystem.dmg ./BaseSystem.img
            ${pkgs.qemu}/bin/qemu-img create -f qcow2 ./mac_hdd_ng.img 256G
            ./OpenCore-Boot.sh
          '');
        };
      }
    );
}
