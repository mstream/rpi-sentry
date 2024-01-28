{ pkgs, ... }:
let
  sources = pkgs.stdenv.mkDerivation
    {
      installPhase = ''
        mkdir -p $out
        cp -r * $out/
      '';
      pname = "provisioning-source";
      version = "0.0.1";
      src = pkgs.lib.cleanSource ./.;
    };
  provision = { host, name, port }:
    let extraVars = "ansible_port=${builtins.toString port} arducam=true";
    in pkgs.writeShellApplication {
      name = "provision-${name}";
      runtimeInputs = [ pkgs.ansible ];
      text = ''
        cd ${sources}
        ansible-playbook playbook-sudo-rpi.yml --inventory="${host}," --extra-vars "${extraVars}"
      '';
    };
  provisionApp = hostConfig:
    {
      program = "${provision hostConfig}/bin/provision-${hostConfig.name}";
      type = "app";
    };
in
provisionApp
