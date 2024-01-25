{ pkgs, ... }:
let
  sources = pkgs.stdenv.mkDerivation
    {
      buildInputs = [ pkgs.nodejs pkgs.nodePackages.browserify ];
      installPhase = ''
        mkdir -p $out
        cp -r rpi-sentry $out/
        npm set strict-ssl=false
        npm ci
        browserify index.js -o rpi-sentry/static/bundle.js
      '';
      pname = "rpi-sentry-source";
      version = "0.0.1";
      src = pkgs.lib.cleanSource ./.;
    };
  deploy = { host, name, port }:
    pkgs.writeShellApplication {
      name = "deploy-${name}";
      runtimeInputs = [ pkgs.openssh ];
      text = ''
        cd ${sources}
        scp -P ${port} -r rpi-sentry pi@${host}:~/
      '';
    };
  deployApp = isReal:
    let
      hostConfig =
        if isReal
        then { host = "192.168.0.75"; name = "real"; port = 22; }
        else { host = "localhost"; name = "fake"; port = 2022; };
    in
    {
      program = "${deploy hostConfig}/bin/deploy-${hostConfig.name}";
      type = "app";
    };
in
{
  fakeApp = deployApp false;
  realApp = deployApp true;
}
