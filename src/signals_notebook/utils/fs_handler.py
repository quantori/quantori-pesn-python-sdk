from typing import List, Protocol, Union


class FSHandler(Protocol):
    def write(self, path: str, data: Union[bytes, str]):
        """Write file content into given path."""

    def read(self, path: str) -> bytes:
        """Return file content from given path."""

    def list_subfolders(self, path) -> List[str]:
        """Return subfolders names from given path."""

    @classmethod
    def join_path(cls, *paths: str) -> str:
        """Concatenate file paths."""
