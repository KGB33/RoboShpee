import dagger
from dagger import dag, function, object_type

PYTHON_TAG = "3.12"


@object_type
class Roboshpee:
    lockfile: dagger.File
    pyproject: dagger.File
    src: dagger.Directory

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
                    "--break-system-packages",
                    "-r",
                    "uv.lock",
                    "--python",
                    "python",
                ]
            )
            .with_directory("/app/roboshpee", self.src)
        )

    @function
    async def publish(self, ghcr_token: dagger.Secret):
        return (
            self.build()
            .with_entrypoint(["python", "-m", "roboshpee"])
            .with_registry_auth("ghcr.io", "kgb33", ghcr_token)
            .publish(address="ghcr.io/kgb33/roboshpee:latest")
        )

    @function
    async def test(
        self,
        tests: dagger.Directory,
    ) -> str:
        return await (
            self.build()
            .with_exec(
                [
                    "uv",
                    "pip",
                    "install",
                    "--break-system-packages",
                    "-r",
                    "uv.lock",
                    "--python",
                    "python",
                ]
            )
            .with_exec(
                [
                    "uv",
                    "pip",
                    "install",
                    "--break-system-packages",
                    "-e",
                    ".",
                    "--python",
                    "python",
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
