from typing import Annotated
import dagger
from dagger import dag, function, object_type, DefaultPath, Ignore

from gha import Actions

PYTHON_TAG = "3.12"


@object_type
class Roboshpee:
    src: dagger.Directory
    is_dev: bool

    def __init__(
        self,
        src: Annotated[dagger.Directory, DefaultPath("/"), Ignore([".venv"])],
        is_dev: bool = True,
    ):
        self.src = src
        self.is_dev = is_dev

        if is_dev:
            self.lockfile = self.src.file("uv.dev.lock")
        else:
            self.lockfile = self.src.file("uv.lock")
        self.pyproject = self.src.file("pyproject.toml")

    @function
    def generate_ci(self) -> Actions:
        return Actions()

    @function
    def build(
        self,
    ) -> dagger.Container:
        return (
            dag.container()
            .from_(f"python:{PYTHON_TAG}")
            .with_exec(["apt", "update"])
            .with_exec(["pip", "install", "uv"])
            .with_exec(["mkdir", "/app"])
            .with_workdir("/app")
            .with_file("/app/uv.lock", self.lockfile)
            .with_file("/app/pyproject.toml", self.pyproject)
            .with_exec(
                [
                    "uv",
                    "pip",
                    "install",
                    "--system",
                    "--break-system-packages",
                    "-r",
                    "uv.lock",
                ]
            )
            .with_directory("/app/roboshpee", self.src.directory("roboshpee"))
        )

    @function
    async def publish(self, ghcr_token: dagger.Secret) -> str:
        assert (
            not self.is_dev
        ), "You probably don't want to publish a dev build (pass --is-dev=false)."
        return await (
            self.build()
            .with_entrypoint(["python", "-m", "roboshpee"])
            .with_registry_auth("ghcr.io", "kgb33", ghcr_token)
            .publish(address="ghcr.io/kgb33/roboshpee:latest")
        )

    @function
    async def test(
        self, tests: Annotated[dagger.Directory, DefaultPath("/tests")]
    ) -> str:
        return await (
            self.build()
            .with_exec(
                [
                    "uv",
                    "pip",
                    "install",
                    "--system",
                    "--break-system-packages",
                    "-e",
                    ".",
                ]
            )
            .with_directory("/app/tests", tests)
            .with_exec(["pytest"])
            .stdout()
        )

    @function
    def run(
        self,
        token: dagger.Secret,
    ) -> dagger.Container:
        return (
            self.build()
            .with_secret_variable("DISCORD_TOKEN", token)
            .with_exec(["python", "-m", "roboshpee"])
        )
