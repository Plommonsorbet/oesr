{ pkgs, config, ... }: {
  #services.pcscd.enable = true;
  #services.udev.packages = with pkgs; [ yubikey-personalization ];

  environment.systemPackages = with pkgs;
    [ gnupg pinentry-curses haskellPackages.hopenpgp-tools oesr.sss-cli oesr.oesr-cli ];

  #programs = {
  #  ssh.startAgent = false;
  #  gnupg.agent = {
  #    enable = true;
  #  };
  #};
}
