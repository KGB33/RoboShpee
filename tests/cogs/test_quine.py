from pathlib import Path

import pytest
import pytest_check as check

from roboshpee.cogs import quine


@pytest.fixture
def fake_dir(tmp_path: Path):
    """
    Creates & populates a directory structure to
    help test the quine cog.
    """
    dirs = ["dir/", "dir/subdir/", "static"]
    files = [
        "README.md",
        "foo.py",
        "dir/bar.py",
        "dir/__init__.py",
        "dir/bar.pyc",
        "dir/subdir/baz.py",
        "static/pic.png",
    ]
    for d in dirs:
        (tmp_path / d).mkdir()
    for f in files:
        (tmp_path / f).touch()
    return tmp_path


@pytest.mark.asyncio
async def test_generate_valid_files(fake_dir):
    result = await quine._generate_valid_files(fake_dir)
    expected = {
        "foo.py": fake_dir / "foo.py",
        "bar.py": fake_dir / "dir" / "bar.py",
        "__init__.py": fake_dir / "dir" / "__init__.py",
        "baz.py": fake_dir / "dir" / "subdir" / "baz.py",
    }
    assert result == expected


@pytest.mark.asyncio
async def test_quinable_table_generation(fake_dir):
    result = await quine._quineables(fake_dir)
    check.equal(result._field_names, ["File Name", "File Path"])
    check.equal(len(result._rows), 4)
    check.equal(set(a for a in result.align.values()), {"c"})
