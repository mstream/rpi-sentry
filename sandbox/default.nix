{ pkgs, ... }:
pkgs.python3Packages.buildPythonApplication rec {
  pname = "rpi-sentry-sandbox";
  version = "0.1.0";
  pyproject = true;

  src = ./.;

  nativeBuildInputs = [
    pkgs.python3Packages.poetry-core
  ];

  propagatedBuildInputs = [
    (import ../gpiozero { inherit pkgs; })
    (import ../tkgpio { inherit pkgs; })
  ];

  meta = with pkgs.lib; { };
}
