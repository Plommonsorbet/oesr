#{
#  description = "GPG-SETUP";
#  inputs.nixos.url = "github:nixos/nixpkgs/nixos-20.09";
#  inputs.nixpkgs-unstable.url = "github:nixos/nixpkgs/nixos-unstable";
#
#  outputs = { self, nixos, nixpkgs-unstable }@inputs: {
#
#    #nixosConfigurations = {
#    #  #liveCD = nixos.lib.nixosSystem {
#    #  #  system = "x86_64-linux";
#    #  #  modules = [
#    #  #    #"${nixos}/nixos/modules/installer/cd-dvd/installation-cd-minimal.nix"
#    #  #  ] ++ [
#
#    #  #    ({ pkgs, ... }: {
#
#    #  #      nixpkgs.overlays = [
#    #  #        (final: prev: {
#    #  #          sss-cli = final.callPackage ./pkgs/sss-cli { };
#    #  #        })
#    #  #      ];
#
#    #  #      imports = [ (import ./liveCD) ];
#
#    #  #    })
#    #  #  ];
#    #  #};
#    #};
#  };
#}

{
  description = "Flake utils demo";

  inputs.flake-utils.url = "github:numtide/flake-utils";
  inputs.nixos.url = "github:nixos/nixpkgs/nixos-20.09";

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let pkgs = nixpkgs.legacyPackages.${system}; in
      rec {
	overlay = 
        (final: prev: {
          sss-cli = final.callPackage ./pkgs/sss-cli { };
        });
        packages = flake-utils.lib.flattenTree {
          "ds-sss-cli" = sss-cli;
          #gitAndTools = pkgs.gitAndTools;
        #};
        #defaultPackage = packages.sss-cli;
        #apps.hello = flake-utils.lib.mkApp { drv = packages.hello; };
        #defaultApp = apps.hello;
      }
    );
}
