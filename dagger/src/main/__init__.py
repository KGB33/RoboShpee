import dagger
from dagger import dag, function, object_type

# Wrapping strings in a platform makes type hints happy.
PLATFORMS: list[dagger.Platform] = [
    dagger.Platform("linux/amd64"),
    dagger.Platform("linux/arm64"),
]

PYTHON_TAG = "3.12"


@object_type
class Roboshpee:
    @function
    def build(self, req: dagger.File, src: dagger.Directory) -> list[dagger.Container]:
        return [self._build(req, src, platform) for platform in PLATFORMS]

    def _build(
        self,
        req: dagger.File,
        src: dagger.Directory,
        platform: dagger.Platform,
    ) -> dagger.Container:
        return (
            dag.container(platform=platform)
            .from_(f"python:{PYTHON_TAG}")
            .with_exec(["apt", "update"])
            # .with_exec(["apt", "install", "build-base", "libffi", "-y"])
            .with_exec(["pip", "install", "uv"])
            .with_exec(["mkdir", "/app"])
            .with_workdir("/app")
            .with_file("/app/pyproject.toml", req)
            .with_exec(
                [
                    "uv",
                    "pip",
                    "install",
                    "--break-system-packages",
                    "-r",
                    "pyproject.toml",
                    "--python",
                    "python",
                ]
            )
            .with_directory("/app/roboshpee", src)
        )

    @function
    async def publish(
        self, req: dagger.File, src: dagger.Directory, ghcr_token: dagger.Secret
    ):
        ctrs = [
            ctr.with_entrypoint(["python", "-m", "roboshpee"])
            for ctr in self.build(req, src)
        ]
        await (
            dag.container()
            .with_registry_auth("ghcr.io", "kgb33", ghcr_token)
            .publish(address="ghcr.io/kgb33/roboshpee:latest", platform_variants=ctrs)
        )

    @function
    async def test(
        self,
        req: dagger.File,
        src: dagger.Directory,
        tests: dagger.Directory,
        platform: str = "linux/amd64",  # Literal["linux/amd64", "linux/arm64"]
    ) -> str:
        return await (
            self._build(req, src, dagger.Platform(platform))
            .with_exec(
                [
                    "uv",
                    "pip",
                    "install",
                    "--break-system-packages",
                    "pytest",
                    "pytest-check",
                    "pytest-asyncio",
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
    async def run(
        self,
        req: dagger.File,
        src: dagger.Directory,
        token: dagger.Secret,
        platform: str = "linux/amd64",  # Literal["linux/amd64", "linux/arm64"]
    ) -> dagger.Container:
        return (
            self._build(dagger.Platform(platform), req, src)
            .with_env_variable("DISCORD_TOKEN", await token.plaintext())
            .with_exec(["python", "-m", "roboshpee"])
        )
