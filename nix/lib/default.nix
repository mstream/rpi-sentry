{ pkgs, ... }:
let
  testPython = pkgs.python3.withPackages (ps: with ps; [
    hypothesis
    pyfakefs
    pytest
    pytest-mock
  ]);
  mkSpec = { deps, src, name, version }:
    {
      inherit src version;
      doCheck = true;
      checkPhase = ''
        ${testPython}/bin/python -m pytest -p no:cacheprovider ${src}/tests
      '';
      pname = "rpi-sentry-${name}";
      pyproject = true;

      nativeBuildInputs = [
        pkgs.python3Packages.poetry-core
      ];

      propagatedBuildInputs = deps;

      meta = with pkgs.lib; { };
    };

  mkPoetryApp = conf: enableDebug:
    let
      makeWrapperArgs =
        if enableDebug
        then [ "--set LOGLEVEL DEBUG" ]
        else [ "--set LOGLEVEL INFO" ];
      spec = (mkSpec conf) // { inherit makeWrapperArgs; };
    in
    pkgs.python3Packages.buildPythonApplication spec;

  mkPoetryPackage = conf:
    pkgs.python3Packages.buildPythonPackage (mkSpec conf);

in
{ inherit mkPoetryApp mkPoetryPackage; }
