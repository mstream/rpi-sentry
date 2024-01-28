{ pkgs, sources, ... }:
let
  deploy = { host, name, port }:
    pkgs.writeShellApplication {
      name = "deploy-${name}";
      runtimeInputs = [ pkgs.openssh ];
      text = ''
        cd ${sources}
        scp -P ${builtins.toString port} -r rpi-sentry pi@${host}:~/
      '';
    };
  deployApp = hostConfig:
    {
      program = "${deploy hostConfig}/bin/deploy-${hostConfig.name}";
      type = "app";
    };
in
deployApp
