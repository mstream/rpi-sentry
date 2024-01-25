{
  description = "Nix Presentation";

  inputs = { nixpkgs.url = "github:nixos/nixpkgs/23.11"; };

  outputs = inputs:
    let
      name = "rpi-sentry";
      system = "aarch64-darwin";
      pkgs = import inputs.nixpkgs { inherit system; };
      deploy = import ./deploy.nix { inherit pkgs; };
      docker = import ./docker { inherit pkgs; };
      provisioning = import ./provisioning { inherit pkgs; };
    in
    {
      apps.${system} = {
        deploy-fake = deploy.fakeApp;
        deploy-real = deploy.realApp;
        run-fake = docker.fakeApp;
        provision-fake = provisioning.fakeApp;
        provision-real = provisioning.realApp;
      };
      devShell.${system} = pkgs.mkShell {
        inherit name;
        shellHook = ''
          PS1="\[\e[33m\][\[\e[m\]\[\e[34;40m\]${name}:\[\e[m\]\[\e[36m\]\w\[\e[m\]\[\e[33m\]]\[\e[m\]\[\e[32m\]\\$\[\e[m\] "
        '';
      };
    };
}
