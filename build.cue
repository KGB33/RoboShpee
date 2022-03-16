package main

import (
	"dagger.io/dagger"
	"universe.dagger.io/docker"
	"strings"
)

dagger.#Plan & {
	client: {
		filesystem: "./": read: contents: dagger.#FS
		env: GHCR_PAT: dagger.#Secret
		commands: {
			version: {
				name: "poetry"
				args: ["version", "-s"]
			}
		}
	}

	actions: {
		build: docker.#Build & {
			steps: [
				docker.#Pull & {source: "python:slim"},
				docker.#Run & {
					command: {name: "apt", args: ["update", "-y"]}
				},
				docker.#Run & {
					command: {name: "apt", args: ["upgrade", "-y"]}
				},
				docker.#Run & {
					command: {name: "apt", args: ["install", "gcc", "-y"]}
				},
				docker.#Run & {command: {name: "pip", args: ["install", "poetry"]}},
				for f, poetryFile in ["poetry.lock", "pyproject.toml"] {
					docker.#Copy & {
						contents: client.filesystem."./".read.contents
						source:   poetryFile
						dest:     "\(poetryFile)"
					}
				},
				docker.#Run & {
					command: {name: "poetry", args: ["config", "virtualenvs.create", "false"]}
				},
				docker.#Run & {
					command: {name: "poetry", args: ["install", "--no-dev"]}
				},
				docker.#Copy & {
					contents: client.filesystem."./".read.contents
					source:   "/roboshpee"
					dest:     "./roboshpee"
				},
				docker.#Set & {
					config: {
						cmd: ["python", "-m", "roboshpee"]
						label: "org.opencontainers.image.source": "https://github.com/kgb33/roboshpee"
						label: "version":                         strings.Trim(client.commands.version.stdout, "\n")
					}
				},
			]

		}
		publish: {
			_versions: ["latest", strings.Trim(client.commands.version.stdout, "\n")]
			for idx, version in _versions {
				"\(idx)": docker.#Push & {
					dest:  "ghcr.io/kgb33/roboshpee:\(version)"
					image: build.output
					auth: {username: "kgb33", secret: client.env.GHCR_PAT}
				}
			}

		}
	}
}
