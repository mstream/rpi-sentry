{ pkgs, ... }:
pkgs.python3Packages.buildPythonPackage rec {
  pname = "gpiozero";
  version = "2.0";
  pyproject = true;

  src = pkgs.fetchPypi {
    inherit pname version;
    hash = "sha256-QDvMnn8k8Id2U+f87ZG6UVCNUZfJ0fgOOD/maTucPCc=";
  };

  nativeBuildInputs = [
    pkgs.python3Packages.setuptools
  ];

  propagatedBuildInputs = [
    pkgs.python3Packages.colorzero
  ];

  meta = with pkgs.lib; {
    homepage = "https://github.com/gpiozero/gpiozero";
  };
}
