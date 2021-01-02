"""
Home for pytest fixures
"""
import pytest


@pytest.fixture
def author():
    """
    Generates a discord-author-like object
    """

    class Author:
        def __init__(self, name: str):
            self.name: str = name

        @property
        def mention(self):
            return f"@{self.name}"

    return Author("AuthorName")
