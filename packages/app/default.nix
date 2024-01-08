{ pkgs, ... }:
let
  lib = import ../../nix/lib { inherit pkgs; };
in
lib.mkPoetryApp {
  name = "app";
  version = "0.1.0";
  src = ./.;
  deps = [
    (import ../core { inherit pkgs; })
    (import ../gpiozero { inherit pkgs; })
  ];
}
