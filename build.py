import argparse
import asyncio
import os
import shutil
import subprocess
import sys

import dagger
from dagger.api.gen import Container, ContainerID, Platform

# Wrapping strings in a platform makes type hints happy.
PLATFORMS: list[Platform] = [
    Platform("linux/amd64"),  # a.k.a. x86_64
    Platform("linux/arm64"),  # a.k.a. aarch64
]


async def main(args: argparse.Namespace):
    cfg = dagger.Config()
    if args.verbose:
        cfg.log_output = sys.stdout

    async with dagger.Connection(cfg) as client:
        if not args.skip_tests:
            await test()
        images = await build(client)
        if args.publish:
            await publish(client.container(), images)


async def build(client: dagger.Client) -> list[ContainerID]:
    """
    Build a `python:alpine` image packaging roboshpee.
    """
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
    os.makedirs("./build/linux", exist_ok=True)

    # Build each platform.
    tasks = []
    async with asyncio.TaskGroup() as tg:
        for platform in PLATFORMS:
            tasks.append(
                tg.create_task(
                    build_platform(client, platform, parse_reqs, source_files)
                )
            )
    return [t.result() for t in tasks]


async def build_platform(client, platform, requirement_file, src) -> ContainerID:
    print(f"Building {platform}...")
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
    print(f"{platform} done...")
    return await ctr.id()


async def test():
    """
    Run pytest tests.
    """
    subprocess.run(["pytest", "tests"], check=True)


async def publish(ctr: Container, images: list[ContainerID]):
    """
    Push images to ghcr.
    """
    print("Publishing images to ghcr...")
    await ctr.publish(
        address="ghcr.io/kgb33/roboshpee:latest", platform_variants=images
    )


async def load_local():
    # Load amd64 image into local docker cache
    subprocess.run(["docker", "load", "-i", "./build/linux/amd64.tar.gz"])


def clean():
    shutil.rmtree("build/")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Builds container images using dagger."
    )
    parser.add_argument(
        "-p", "--publish", action="store_true", help="Publish images to ghcr."
    )
    parser.add_argument(
        "-T", "--skip_tests", action="store_true", help="Don't run tests."
    )
    parser.add_argument(
        "-c",
        "--clean",
        action="store_true",
        help="Removes generated 'build/' directory.",
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enables dagger debug output"
    )
    parser.add_argument(
        "--gha",
        action="store_true",
        help="Enables Github action specific functionality",
    )

    args = parser.parse_args()
    if args.clean:
        clean()
        sys.exit(0)

    print("Starting pipeline...")
    asyncio.run(main(args))
