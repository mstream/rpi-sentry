{
  description = "A very basic flake";

  inputs = { nixpkgs.url = "github:nixos/nixpkgs/23.11"; };

  outputs = inputs:
    let
      name = "rpi-sentry";
      system = "aarch64-darwin";
      pkgs = import inputs.nixpkgs { inherit system; };
      packages = {
        app = import ./packages/app { inherit pkgs; };
        appDebug = import ./packages/app { inherit pkgs; enableDebug = true; };
        core = import ./packages/core { inherit pkgs; };
        gpiozero = import ./packages/gpiozero { inherit pkgs; };
        sandbox = import ./packages/sandbox { inherit pkgs; };
        sandboxDebug = import ./packages/sandbox { inherit pkgs; enableDebug = true; };
        tkgpio = import ./packages/tkgpio { inherit pkgs; };
      };
      apps = {
        app = {
          type = "app";
          program = "${packages.app}/bin/app";
        };
        appDebug = {
          type = "app";
          program = "${packages.appDebug}/bin/app";
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
    {
      apps.${system} = {
        inherit (apps) app appDebug sandbox sandboxDebug;
        default = apps.sandbox;
      };
      devShell.${ system} = pkgs.mkShell {
        inherit name;
        inputsFrom = [ packages.sandbox ];
        shellHook = ''
          PS1="\[\e[33m\][\[\e[m\]\[\e[34;40m\]${name}:\[\e[m\]\[\e[36m\]\w\[\e[m\]\[\e[33m\]]\[\e[m\]\[\e[32m\]\\$\[\e[m\] "
        '';
      };
      packages.${system} = {
        inherit (packages) app appDebug core gpiozero sandbox sandboxDebug tkgpio;
        default = packages.sandbox;
      };
    };
}
