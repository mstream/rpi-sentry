{
  description = "A very basic flake";

  inputs = {
    flake-utils.url = "github:numtide/flake-utils/main";
    nixpkgs.url = "github:nixos/nixpkgs/23.11";
  };

  outputs = inputs:
    let
      name = "rpi-sentry";
      systems = [ "aarch64-darwin" "aarch64-linux" "armv7l-linux" "x86_64-linux" ];
      systemOutputs = system:
        let
          pkgs = import inputs.nixpkgs { inherit system; };
          buildPackages = pkgs: {
            app = import ./packages/app { inherit pkgs; };
            appDebug = import ./packages/app { inherit pkgs; enableDebug = true; };
            core = import ./packages/core { inherit pkgs; };
            gpiozero = import ./packages/gpiozero { inherit pkgs; };
            sandbox = import ./packages/sandbox { inherit pkgs; };
            sandboxDebug = import ./packages/sandbox { inherit pkgs; enableDebug = true; };
            tkgpio = import ./packages/tkgpio { inherit pkgs; };
          };
          buildApps = packages: {
            app = {
              type = "app";
              program = "${packages.app}/bin/app";
            };
            appDebug = {
              type = "app";
              program = "${packages.appDebug}/bin/app";
            };
            app-cross-armv7l-linux = {
              type = "app";
              program = "${packages.app-cross-armv7l-linux}/bin/app";
            };
            appDebug-cross-armv7l-linux = {
              type = "app";
              program = "${packages.appDebug-cross-armv7l-linux}/bin/app";
            };
            sandbox = {
              type = "app";
              program = "${packages.sandbox}/bin/sandbox";
            };
            sandboxDebug = {
              type = "app";
              program = "${packages.sandboxDebug}/bin/sandbox";
            };
          };
        in
        rec {
          apps = rec {
            inherit (buildApps packages) app appDebug sandbox sandboxDebug;
            default = sandbox;
          };
          devShell = pkgs.mkShell {
            inherit name;
            inputsFrom = [ packages.sandbox ];
            shellHook = ''
              PS1="\[\e[33m\][\[\e[m\]\[\e[34;40m\]${name}:\[\e[m\]\[\e[36m\]\w\[\e[m\]\[\e[33m\]]\[\e[m\]\[\e[32m\]\\$\[\e[m\] "
            '';
          };
          packages = rec {
            inherit (buildPackages pkgs) app appDebug core gpiozero sandbox sandboxDebug tkgpio;
            default = sandbox;
            app-cross-armv7l-linux = (buildPackages pkgs.pkgsCross.armv7l-hf-multiplatform).app;
            appDebug-cross-armv7l-linux = (buildPackages pkgs.pkgsCross.armv7l-hf-multiplatform).appDebug;
          };
        };
    in
    inputs.flake-utils.lib.eachSystem systems systemOutputs;
}
