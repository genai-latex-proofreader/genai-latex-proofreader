from pathlib import Path


def read_directory(directory: Path) -> dict[Path, bytes]:
    """
    Read all files in a directory and return them as a dictionary.

    Args:
        directory: Path to the directory to read.

    Returns:
        Dictionary with keys as relative paths to the directory and values as the
        contents of the files.
    """
    files = {}
    for file_path in directory.glob("**/*"):
        if file_path.is_file():
            files[file_path.relative_to(directory)] = file_path.read_bytes()
    return files


def write_directory(files: dict[Path, bytes], directory: Path) -> None:
    """
    Write files to a directory.

    Args:
        files: Dictionary with keys as relative paths to the directory and values as
            the contents of the files.
        directory: Path to the directory to write the files to.
    """
    for relative_path, content in files.items():
        file_path = directory / relative_path
        file_path.parent.mkdir(parents=True, exist_ok=True)

        if isinstance(content, bytes):
            file_path.write_bytes(content)
        else:
            raise Exception(
                f"Content for {file_path} is not bytes, but type is {type(content)}."
            )
