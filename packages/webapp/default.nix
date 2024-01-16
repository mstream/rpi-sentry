{ pkgs, ... }:
let
  dash = pkgs.fetchurl {
    url = "http://cdn.dashjs.org/latest/dash.all.min.js";
    hash = "sha256-ANoKnniSzMvYpeWSL59jUdE29ugmAkVCzEhCkX1ujbU=";
  };
in
pkgs.stdenvNoCC.mkDerivation {
  name = "rpi-sentry-webapp";
  src = ./.;
  buildInputs = [ ];
  installPhase = ''
    mkdir $out
    cp index.html $out/
    cp ${dash} $out/dash.all.min.js
  '';
}
