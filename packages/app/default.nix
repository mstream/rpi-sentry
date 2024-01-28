{ lib
, config
, dream2nix
, ...
}:
let
  dir = "$out/rpi-sentry";
in
{
  imports = [
    dream2nix.modules.dream2nix.mkDerivation
    dream2nix.modules.dream2nix.nodejs-granular-v3
    dream2nix.modules.dream2nix.nodejs-package-json-v3
  ];

  name = lib.mkForce "app";
  version = lib.mkForce "1.0.0";

  nodejs-granular-v3 = {
    buildScript = ''
      browserify src/client/index.js -o ${dir}/static/index.js
      cp -r static ${dir}/
      cp -r templates ${dir}/
      cp src/server/* ${dir}/
      cp src/update.avsc ${dir}/
    '';
  };
  mkDerivation = {
    src = lib.cleanSource ./.;
  };
}
