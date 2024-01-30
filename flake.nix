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
      pkgs = import inputs.nixpkgs { inherit system; };
      packages = inputs.dream2nix.lib.importPackages {
        projectRoot = ./.;
        projectRootFile = "flake.nix";
        packagesDir = ./packages;
        packageSets.nixpkgs = pkgs;
        packageSets.self = inputs.self.packages.${system};
      };
    in
    {
      packages.${system} = packages;
      apps.${system} = {
        deploy = {
          program = "${packages.provisioning}/bin/deploy";
          type = "app";
        };
        provision = {
          program = "${packages.provisioning}/bin/provision";
          type = "app";
        };
      };
      devShell.${system} = pkgs.mkShell {
        inherit name;
        shellHook = ''
          PS1="\[\e[33m\][\[\e[m\]\[\e[34;40m\]${name}:\[\e[m\]\[\e[36m\]\w\[\e[m\]\[\e[33m\]]\[\e[m\]\[\e[32m\]\\$\[\e[m\] "
        '';
      };
    };
}
