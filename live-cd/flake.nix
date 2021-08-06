{
  inputs = {
    nixos.url = "github:nixos/nixpkgs/nixos-21.05";
    oesr.url = "path:../";
  };

  outputs = { self, nixos, oesr }: {
    nixosConfigurations = {
      liveCD = nixos.lib.nixosSystem {
        system = "x86_64-linux";
        modules = [
          "${nixos}/nixos/modules/installer/cd-dvd/installation-cd-minimal.nix"
        ] ++ [

          ({ pkgs, ... }: {

            nixpkgs.overlays =
              [ (final: prev: { oesr = oesr.packages."x86_64-linux"; }) ];

            imports = [ (import ./live-cd.nix) ];

          })
        ];
      };
    };
  };
}

