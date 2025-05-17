{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
    crane.url = "github:ipetkov/crane";
    rust-overlay = {
      url = "github:oxalica/rust-overlay";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };
  outputs = {
    self,
    crane,
    flake-utils,
    nixpkgs,
    rust-overlay,
  }:
    flake-utils.lib.eachDefaultSystem
    (
      system: let
        pkgs = import nixpkgs {
          inherit system;
          overlays = [(import rust-overlay)];
        };
        rustToolchanfor = p:
          p.rust-bin.nightly.latest.default;
        craneLib =
          (crane.mkLib pkgs).overrideToolchain rustToolchanfor;
        src = craneLib.cleanCargoSource ./.;
        commonArgs = {
          inherit src;
          strictDeps = true;
          nativeBuildInputs = with pkgs; [pkg-config openssl];
        };
        cargoArtifacts = craneLib.buildDepsOnly commonArgs;
        roboshpee = craneLib.buildPackage (
          commonArgs // {inherit cargoArtifacts;}
        );
      in rec
      {
        checks = {
          inherit roboshpee;
          roboshpee-clippy = craneLib.cargoClippy (
            commonArgs
            // {
              inherit cargoArtifacts;
              cargoClippyExtraArgs = "--all-targets -- --deny warnings";
            }
          );
          roboshpee-fmt = craneLib.cargoFmt {inherit src;};
          roboshpee-test = craneLib.cargoNextest (
            commonArgs
            // {
              inherit cargoArtifacts;
              partitions = 1;
              partitionType = "count";
              cargoNextTestPartitionsExtraArgs = "--no-tests=pass";
            }
          );
        };
        packages = {
          roboshpee = roboshpee;
          default = packages.roboshpee;
        };
        # Nicer `nix run ...`
        apps.default = flake-utils.lib.mkApp {
          drv = roboshpee;
        };
        devShells = {
          default = craneLib.devShell {
            inputsFrom = [packages.default];
            checks = self.checks.${system};
            packages = with pkgs; [
              rust-analyzer
            ];
          };
        };
      }
    );
}
