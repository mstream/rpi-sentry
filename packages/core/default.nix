{ pkgs, ... }:
let
  lib = import ../../nix/lib { inherit pkgs; };
in
lib.mkPoetryPackage {
  name = "core";
  version = "0.1.0";
  src = ./.;
  deps = [
    (with pkgs.python3Packages; [ pydantic ])
    (import ../gpiozero { inherit pkgs; })
  ];
}
