{ lib
, config
, dream2nix
, ...
}:
let
  healthCheckDir = "$out/rpi-sentry-health-check";
  serverDir = "$out/rpi-sentry";
in
{
  imports = [
    dream2nix.modules.dream2nix.mkDerivation
    dream2nix.modules.dream2nix.nodejs-devshell-v3
    dream2nix.modules.dream2nix.nodejs-granular-v3
    dream2nix.modules.dream2nix.nodejs-package-json-v3
  ];

  name = lib.mkForce "app";
  version = lib.mkForce "1.0.0";

  deps = { nixpkgs, ... }:
    {
      inherit
        (nixpkgs)
        avro-tools
        rsync;
    };

  nodejs-granular-v3 = {
    buildScript = ''
      mkdir -p ${healthCheckDir}
      browserify src/client/index.js -o ${serverDir}/static/index.js
      cp -r static ${serverDir}/
      cp -r templates ${serverDir}/
      cp src/server/* ${serverDir}/
      cp src/*.avsc ${serverDir}/
      cp src/health-check/* ${healthCheckDir}/
    '';
  };

  mkDerivation = {
    checkPhase = ''
      find src -name '*.avsc' | xargs -i ${config.deps.avro-tools}/bin/avro-tools canonical {} -
    '';
    doCheck = true;
    src = lib.cleanSource ./.;
  };
}
