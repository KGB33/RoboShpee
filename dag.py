import argparse
import asyncio
import os
import shutil
import subprocess
import sys

import dagger
from dagger import Container, Platform

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
        images = build(client)
        if args.load:
            await load(images)
        if args.publish:
            await publish(client, list(images.values()))
    if args.load:
        load_local()


def build(client: dagger.Client) -> dict[str, Container]:
    """
    Build a `python:alpine` image packaging roboshpee.
    """
    # Grab Lock Files
    requirment_files = client.host().directory(
        path=".", include=["pyproject.toml", "poetry.lock"]
    )

    # Export Poetry lockfile into pip install -r able-format
    parse_reqs = (
        client.container()
        .from_("alpine:edge")
        .with_exec(["apk", "add", "poetry"])
        .with_mounted_directory("/host", requirment_files)
        .with_workdir("/host")
        .with_exec(["poetry", "export"], redirect_stdout="requirements.txt")
        .file("requirements.txt")
    )

    # Grab Application Source Files
    source_files = client.host().directory(".", include=["roboshpee/"])

    # Build each platform.
    return {
        platform: build_platform(client, platform, parse_reqs, source_files)
        for platform in PLATFORMS
    }


def build_platform(client, platform, requirement_file, src) -> Container:
    print(f"Building {platform}...")
    ctr = (
        client.container(platform=platform)
        .from_("python:3.11-alpine")
        .with_exec(["apk", "add", "build-base", "libffi-dev"])
        .with_exec(["python", "-m", "pip", "install", "--upgrade", "pip"])
        .with_mounted_file("/requirements.txt", requirement_file)
        .with_exec(["python", "-m", "pip", "install", "-r", "/requirements.txt"])
        .with_mounted_directory("/host", src)
        .with_exec(["cp", "-r", "/host", "/app"])
        .with_workdir("/app")
        .with_entrypoint(["python", "-m", "roboshpee"])
    )
    return ctr


async def load(ctrs: dict[str, Container]):
    # create output directory
    os.makedirs("./build/linux", exist_ok=True)

    async with asyncio.TaskGroup() as tg:
        for platform, ctr in ctrs.items():
            tg.create_task(ctr.export(f"./build/{platform}.tar.gz"))


async def test():
    """
    Run pytest tests.
    """
    subprocess.run(["pytest", "tests"], check=True)


async def publish(client, images: list[Container]):
    """
    Push images to ghcr.
    """
    print("Publishing images to ghcr...")
    await client.container().publish(
        address="ghcr.io/kgb33/roboshpee:latest", platform_variants=images
    )


def load_local():
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
    parser.add_argument(
        "-l",
        "--load",
        action="store_true",
        help="Load the built image to your local docker engine",
    )

    args = parser.parse_args()
    if args.clean:
        clean()
        sys.exit(0)

    print("Starting pipeline...")
    asyncio.run(main(args))
