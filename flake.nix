{
  description = "A tex flake";

  inputs = { nixpkgs.url = "github:nixos/nixpkgs?ref=nixos-25.05"; };

  outputs = { self, nixpkgs }: {

    devShells.aarch64-darwin = {
      default = nixpkgs.legacyPackages.aarch64-darwin.mkShell {
        buildInputs = [
          nixpkgs.legacyPackages.aarch64-darwin.texliveFull
          nixpkgs.legacyPackages.aarch64-darwin.texliveTeTeX
        ];
      };
    };

  };
}
