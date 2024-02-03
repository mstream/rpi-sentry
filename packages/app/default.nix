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
      browserify src/client/index.js -o ${dir}/static/index.js
      cp -r static ${dir}/
      cp -r templates ${dir}/
      cp src/server/* ${dir}/
      cp src/*.avsc ${dir}/
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
