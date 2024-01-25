{ pkgs, ... }:
let
  imageName = "fake-rpi";
  sources = pkgs.stdenv.mkDerivation
    {
      installPhase = ''
        mkdir -p $out
        cp -r * $out/
      '';
      pname = "docker-source";
      version = "0.0.1";
      src = pkgs.lib.cleanSource ./.;
    };
  runFake = pkgs.writeShellApplication {
    name = "run-fake";
    runtimeInputs = [ pkgs.docker-client ];
    text = ''
      cd ${sources}
      docker build -t ${imageName} .
      docker run -p 2022:22 ${imageName}
    '';
  };
  runFakeApp = {
    program = "${runFake}/bin/run-fake";
    type = "app";
  };
in
{ fakeApp = runFakeApp; }
