{ rustPlatform, cmake, pkgconfig }:

with (import <nixpkgs> {});
#with nixpkgs;
rustPlatform.buildRustPackage rec {
  cargoPatches = [ ./cargo.patch ];
  name = "sss-${version}";
  version = "v0.1";
  src = fetchGit {
    url = "https://github.com/dsprenkels/sss-cli";
    #owner = "dsprenkels";
    #repo = "sss-cli";
   # rev = "df0dc744210b0851a0431a0951ea36f1e5ff0e91";
   # ref = "v0.1";
  rev= "df0dc744210b0851a0431a0951ea36f1e5ff0e91";
  #sha256= "0ipw864gxvp0pf787pgmmfn44zq683kmrhjc8j1x30mycpkrvxnl";
    #sha256 = "0ipw864gxvp0pf787pgmmfn44zq683kmrhjc8j1x30mycpkrvxnl";

  };
 # cargoSha256 = "sha256-3Wnz70DYe7mSFmvaHwxnX/w8xOlTn/uGtAhxzfsjOTM=";
  cargoSha256 = "sha256-lh2MQ9U/0Vu4yWZkxzJ9MI/EMlbM0scZcRUCuDdjWOU=";


  #buildInputs = [ 
  #  nixpkgs.latest.rustChannels.stable.rust
  #];
}

#  "url": "https://github.com/dsprenkels/sss-cli",
#  "date": "2021-04-13T15:01:43+02:00",
#
#  "path": "/nix/store/rrdpmyffl89v22g72iq8i44fnmf7xfxn-sss-cli",
#  "fetchSubmodules": false,
#  "deepClone": false,
#  "leaveDotGit": false
#
