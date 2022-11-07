import asyncio
import os
import subprocess

import dagger
from dagger.api.gen import Container, ContainerID, Platform

# Wrapping strings in a platform makes type hints happy.
PLATFORMS: list[Platform] = [
    Platform("linux/amd64"),  # a.k.a. x86_64
    Platform("linux/arm64"),  # a.k.a. aarch64
]


async def build():
    """
    Build a `python:alpine` image packaging roboshpee.
    """
    async with dagger.Connection() as client:
        # Grab Lock Files
        requirment_files = (
            await client.host().workdir(include=["pyproject.toml", "poetry.lock"]).id()
        )

        # Export Poetry lockfile into pip install -r able-format
        parse_reqs = await (
            client.container()
            .from_("alpine:edge")
            .exec(["apk", "add", "poetry"])
            .with_mounted_directory("/host", requirment_files)
            .with_workdir("/host")
            .exec(["poetry", "export"])
            .stdout()  # Returns a file
        ).id()

        # Grab Application Source Files
        source_files = await client.host().workdir(include=["roboshpee/"]).id()

        # create output directory
        os.makedirs(f"./build/linux", exist_ok=True)

        # Build each platform.
        tasks = []
        async with asyncio.TaskGroup() as tg:
            for platform in PLATFORMS:
                tasks.append(
                    tg.create_task(
                        build_platform(client, platform, parse_reqs, source_files)
                    )
                )

        await publish(client.container(), [t.result() for t in tasks])

        # Load amd64 image into local docker cache
        subprocess.run(["docker", "load", "-i", "./build/linux/amd64.tar.gz"])


async def build_platform(client, platform, requirement_file, src) -> ContainerID:
    ctr = (
        client.container(platform=platform)
        .from_("python:alpine")
        .exec(["apk", "add", "build-base", "libffi-dev"])
        .exec(["python", "-m", "pip", "install", "--upgrade", "pip"])
        .with_mounted_file("/requirements.txt", requirement_file)
        .exec(["python", "-m", "pip", "install", "-r", "/requirements.txt"])
        .with_mounted_directory("/host", src)
        .exec(["cp", "-r", "/host", "/app"])
        .with_workdir("/app")
        .with_entrypoint(["python", "-m", "roboshpee"])
    )
    await ctr.export(f"./build/{platform}.tar.gz")
    return await ctr.id()

    # print(f"{platform_variants=}")
    # await client.container().publish("localhost:5000/roboshpee", platform_variants=platform_variants)

    # Loads the image to run locally. Check stdout for the sha to run.


async def test():
    """
    Run pytest tests.
    """
    pass


async def publish(ctr: Container, images: list[ContainerID]):
    """
    Push images to ghcr.
    """
    await ctr.publish(
        address="ghcr.io/kgb33/roboshpee:latest", platform_variants=images
    )


if __name__ == "__main__":
    asyncio.run(build())
