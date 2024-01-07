{ pkgs, ... }:
pkgs.python3Packages.buildPythonPackage rec {
  pname = "tkgpio";
  version = "0.1.1";
  pyproject = true;

  src = pkgs.fetchPypi {
    inherit pname version;
    hash = "sha256-VUDztpS7IT7q4izmJvwkqkfHr5/2pk6jbgiacMMMx0g=";
  };

  nativeBuildInputs = with pkgs; [
    pkgs.python3Packages.poetry-core
  ];

  propagatedBuildInputs = [
    pkgs.python3Packages.pillow
    pkgs.python3Packages.tkinter
  ];

  meta = with pkgs.lib; {
    homepage = "https://github.com/wallysalami/tkgpio";
  };
}
