{ pkgs, ... }:
let
  testPython = pkgs.python3.withPackages (ps: with ps; [ hypothesis pytest ]);
  mkSpec = { deps, src, name, version }:
    {
      inherit src version;
      doCheck = true;
      checkPhase = ''
        ${testPython}/bin/pytest -p no:cacheprovider ${src}/tests
      '';
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
