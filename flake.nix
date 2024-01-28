{
  description = "Nix Presentation";

  inputs = {
    dream2nix.url = "github:nix-community/dream2nix";
    nixpkgs.follows = "dream2nix/nixpkgs";
  };

  outputs = inputs:
    let
      name = "rpi-sentry";
      system = "aarch64-darwin";
      fakeHostConfig = { host = "localhost"; name = "fake"; port = 2022; };
      realHostConfig = { host = "192.168.0.96"; name = "real"; port = 22; };
      pkgs = import inputs.nixpkgs { inherit system; };
      docker = import ./docker { inherit pkgs; };
      provisioning = import ./provisioning { inherit pkgs; };
      packages = inputs.dream2nix.lib.importPackages {
        projectRoot = ./.;
        projectRootFile = "flake.nix";
        packagesDir = ./packages;
        packageSets.nixpkgs = pkgs;
      };
      deploy = import ./deploy.nix {
        inherit pkgs;
        sources = packages.app;
      };
    in
    {
      packages.${system} = packages;
      apps.${system} = {
        deploy-fake = deploy fakeHostConfig;
        deploy-real = deploy realHostConfig;
        run-fake = docker.fakeApp;
        provision-fake = provisioning fakeHostConfig;
        provision-real = provisioning realHostConfig;
      };
      devShell.${system} = pkgs.mkShell {
        inherit name;
        shellHook = ''
          PS1="\[\e[33m\][\[\e[m\]\[\e[34;40m\]${name}:\[\e[m\]\[\e[36m\]\w\[\e[m\]\[\e[33m\]]\[\e[m\]\[\e[32m\]\\$\[\e[m\] "
        '';
      };
    };
}
