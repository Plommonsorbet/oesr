{
  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        sss-cli = pkgs.callPackage ./sss-cli { };
  	oesrAppEnv = pkgs.poetry2nix.mkPoetryEnv {
  	  projectDir = ./.;
  	  editablePackageSources = {
  	    oesr = ./oers.py;
  	  };
  	};
      in {
        packages.sss-cli = sss-cli;
        defaultPackage = self.packages.${system}.sss-cli;

        devShell = pkgs.mkShell {
          buildInputs = [ sss-cli pkgs.poetry oesrAppEnv ];
        };
      });
}

