{ enableDebug ? false, pkgs, ... }:
let
  lib = import ../../nix/lib { inherit pkgs; };
  conf = {
    name = "app";
    version = "0.1.0";
    src = ./.;
    deps = [
      (import ../core { inherit pkgs; })
      (import ../gpiozero { inherit pkgs; })
    ];
  };
in
lib.mkPoetryApp conf enableDebug
