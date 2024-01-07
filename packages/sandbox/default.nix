{ pkgs, ... }:
let
  lib = import ../../nix/lib { inherit pkgs; };
in
lib.mkPoetryApp {
  name = "sandbox";
  version = "0.1.0";
  src = ./.;
  deps = [
    (import ../core { inherit pkgs; })
    (import ../gpiozero { inherit pkgs; })
    (import ../tkgpio { inherit pkgs; })
  ];
}
