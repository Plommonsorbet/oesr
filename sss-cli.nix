{ pkgs ? <nixpkgs>, rustPlatform, cmake, pkgconfig }:

#with (import <nixpkgs> {});
with pkgs;
rustPlatform.buildRustPackage rec {
  #cargoPatches = [ ./cargo.patch ];
  name = "sss-${version}";
  version = "v0.1";
  src = fetchGit {
    url = "https://github.com/dsprenkels/sss-cli";
    #owner = "dsprenkels";
    #repo = "sss-cli";
    rev = "df0dc744210b0851a0431a0951ea36f1e5ff0e91";
    ref = "v0.1";
    #sha256 = "0ipw864gxvp0pf787pgmmfn44zq683kmrhjc8j1x30mycpkrvxnl";

  };
  cargoSha256 = "sha256-3Wnz70DYe7mSFmvaHwxnX/w8xOlTn/uGtAhxzfsjOTM=";

  #buildInputs = [ 
  #  nixpkgs.latest.rustChannels.stable.rust
  #];
}
