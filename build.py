import asyncio
import subprocess

import dagger


async def build():
    """
    Build a `python:alpine` image packaging roboshpee.

    """
    async with dagger.Connection() as client:
        requirment_files = (
            await client.host().workdir(include=["pyproject.toml", "poetry.lock"]).id()
        )
        parse_reqs = await (
            client.container()
            .from_("alpine:edge")
            .exec(["apk", "add", "poetry"])
            .with_mounted_directory("/host", requirment_files.value)
            .with_workdir("/host")
            .exec(["poetry", "export"])
            .stdout()  # Returns a file
        ).id()
        ctr = (
            client.container()
            .from_("python:alpine")
            .exec(["apk", "add", "build-base"])
            .exec(["python", "-m", "pip", "install", "--upgrade", "pip"])
            .with_mounted_file("/requirements.txt", parse_reqs.value)
            .exec(["python", "-m", "pip", "install", "-r", "/requirements.txt"])
        )
        source_files = await client.host().workdir(include=["roboshpee/"]).id()
        ctr = (
            ctr.with_mounted_directory("/host", source_files.value)
            .exec(["cp", "-r", "/host", "/app"])
            .with_workdir("/app")
            .with_entrypoint(["python", "-m", "roboshpee"])
        )

        await ctr.export("./build/rsphee.tar.gz")

        # Loads the image to run locally. Check stdout for the sha to run.
        subprocess.run(["docker", "load", "-i", "./build/rsphee.tar.gz"])


if __name__ == "__main__":
    asyncio.run(build())
