{ lib
, config
, dream2nix
, ...
}:
let
  sources = config.deps.stdenv.mkDerivation {
    name = "sources";
    installPhase = ''
      cp -r roles $out/
      cp -r tasks $out/
      cp playbook-sudo-rpi.yml $out/
    '';
    src = lib.cleanSource ./.;
  };
  provision = { host, port }:
    let extraVars = "ansible_port=${builtins.toString port} arducam=true";
    in config.deps.writeShellApplication {
      name = "provision";
      runtimeInputs = [ config.deps.ansible ];
      text = ''
        cd ${sources}
        ansible-playbook playbook-sudo-rpi.yml --inventory="${host}," --extra-vars "${extraVars}"
      '';
    };
  deploy = { host, port }:
    config.deps.writeShellApplication {
      name = "deploy";
      runtimeInputs = [ config.deps.openssh ];
      text = ''
        cd ${config.deps.app}
        scp -P ${builtins.toString port} -r rpi-sentry pi@${host}:~/
      '';
    };
  hostConfig = { host = "192.168.0.96"; port = 22; };
in
{
  imports = [
    dream2nix.modules.dream2nix.mkDerivation
  ];

  deps = { nixpkgs, self, ... }: {
    inherit
      (self)
      app;
    inherit
      (nixpkgs)
      ansible
      openssh
      stdenv
      writeShellApplication;
  };

  name = lib.mkForce "provision";
  version = lib.mkForce "1.0.0";

  mkDerivation = {
    installPhase = ''
      mkdir -p $out/bin
      cp ${deploy hostConfig}/bin/deploy $out/bin/;
      cp ${provision hostConfig}/bin/provision $out/bin/;
    '';
    src = lib.cleanSource ./.;
  };
}
