{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
    crane = {
      url = "github:ipetkov/crane";
      inputs.nixpkgs.follows = "nixpkgs";
    };
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
          p.rust-bin.nightly.latest.default.override {
            targets = ["wasm32-unknown-unknown"];
          };
        craneLib =
          (crane.mkLib pkgs).overrideToolchain rustToolchanfor;
      in rec
      {
        packages = {
          roboshpee = craneLib.buildPackage {
            src = craneLib.cleanCargoSource ./.;
            nativeBuildInputs = with pkgs; [pkg-config openssl];
          };
          default = packages.roboshpee;
        };
        devShells = {
          default = craneLib.devShell {
            inputsFrom = [packages.default];
            packages = with pkgs; [
              rust-analyzer
            ];
          };
        };
      }
    );
}
