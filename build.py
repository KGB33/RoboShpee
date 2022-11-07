import asyncio
import os
import subprocess

import dagger
from dagger.api.gen import ContainerID, Platform

PLATFORMS: list[Platform] = [
    Platform("linux/amd64"),  # a.k.a. x86_64
    Platform("linux/arm64"),  # a.k.a. aarch64
]


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
        source_files = await client.host().workdir(include=["roboshpee/"]).id()
        os.makedirs(f"./build/linux", exist_ok=True)
        async with asyncio.TaskGroup() as tg:
            for platform in PLATFORMS:
                tg.create_task(
                    build_platform(client, platform, parse_reqs, source_files)
                )
        subprocess.run(["docker", "load", "-i", "./build/linux/amd64.tar.gz"])


async def build_platform(client, platform, requirement_file, src) -> ContainerID:
    ctr = (
        client.container(platform=platform)
        .from_("python:alpine")
        .exec(["apk", "add", "build-base", "libffi-dev"])
        .exec(["python", "-m", "pip", "install", "--upgrade", "pip"])
        .with_mounted_file("/requirements.txt", requirement_file.value)
        .exec(["python", "-m", "pip", "install", "-r", "/requirements.txt"])
        .with_mounted_directory("/host", src.value)
        .exec(["cp", "-r", "/host", "/app"])
        .with_workdir("/app")
        .with_entrypoint(["python", "-m", "roboshpee"])
    )
    await ctr.export(f"./build/{platform}.tar.gz")
    return (await ctr.id()).value

    # print(f"{platform_variants=}")
    # await client.container().publish("localhost:5000/roboshpee", platform_variants=platform_variants)

    # Loads the image to run locally. Check stdout for the sha to run.


async def test():
    """
    Run pytest tests.
    """
    pass


async def publish():
    """
    Push images to ghcr.
    """
    pass


if __name__ == "__main__":
    asyncio.run(build())
