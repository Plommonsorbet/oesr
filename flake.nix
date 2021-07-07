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
  	oesrApp = pkgs.poetry2nix.mkPoetryApplication {
		buildInputs = [ sss-cli ];
  	  projectDir = ./.;
  	};

  	oesrAppEnv = pkgs.poetry2nix.mkPoetryEnv {
  	  projectDir = ./.;
  	  editablePackageSources = {
  	    oesr = ./oers.py;
  	  };
  	};
      in {
        packages.sss-cli = sss-cli;
        packages.oesr = oesrApp.dependencyEnv;
        defaultPackage = self.packages.${system}.oesr;

        devShell = pkgs.mkShell {
          buildInputs = [ sss-cli pkgs.haskellPackages.hopenpgp-tools pkgs.poetry oesrAppEnv ];
        };
      });
}

