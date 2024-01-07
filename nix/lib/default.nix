{ pkgs, ... }:
let
  mkSpec = { deps, src, name, version }:
    {
      inherit src version;
      pname = "rpi-sentry-${name}";
      pyproject = true;

      nativeBuildInputs = [
        pkgs.python3Packages.poetry-core
      ];

      propagatedBuildInputs = deps;

      meta = with pkgs.lib; { };
    };

  mkPoetryApp = conf:
    pkgs.python3Packages.buildPythonApplication (mkSpec conf);

  mkPoetryPackage = conf:
    pkgs.python3Packages.buildPythonPackage (mkSpec conf);

in
{ inherit mkPoetryApp mkPoetryPackage; }
