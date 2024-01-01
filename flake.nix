{
  description = "A very basic flake";

  inputs = { nixpkgs.url = "github:nixos/nixpkgs/23.11"; };

  outputs = inputs:
    let
      system = "aarch64-darwin";
      pkgs = import inputs.nixpkgs { inherit system; };
      gpiozero = import ./gpiozero { inherit pkgs; };
      sandbox = import ./sandbox { inherit pkgs; };
      tkgpio = import ./tkgpio { inherit pkgs; };
    in
    {
      packages.${system} = {
        inherit gpiozero sandbox tkgpio;
        default = sandbox;
      };
    };
}
