{ pkgs, ... }:
let
  app = import ../app { inherit pkgs; };
  core = import ../core { inherit pkgs; };
in
pkgs.stdenvNoCC.mkDerivation {
  name = "rpi-sentry-source-dist";
  src = ./.;
  buildInputs = [ pkgs.rsync ];
  installPhase = ''
    function unpack_sources() {
      store_path=$1
      cd $store_path/lib/python3.11/site-packages
      rsync -ar --exclude-from $src/rsync-exclude.txt . $out/sources
    }

    mkdir $out
    unpack_sources ${app}
    unpack_sources ${core}
    cp $src/requirements.txt $out
  '';
}
