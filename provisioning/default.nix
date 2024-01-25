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
  provision = host:
    pkgs.writeShellApplication {
      name = "provision-${host}";
      runtimeInputs = [ pkgs.ansible ];
      text = ''
        cd ${sources}
        ansible-playbook -i hosts -l ${host}-rpi playbook-sudo-rpi.yml
      '';
    };
  provisionApp = isReal:
    let
      host = if isReal then "real" else "fake";
    in
    {
      program = "${provision host}/bin/provision-${host}";
      type = "app";
    };
in
{
  fakeApp = provisionApp false;
  realApp = provisionApp true;
}
