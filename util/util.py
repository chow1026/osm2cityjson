from pathlib import Path, PosixPath


def is_valid_filepath(filepath: Path) -> bool:
    if filepath.exists() and filepath.is_file():
        return True
    else:
        return False


def is_valid_dirpath(dirpath: Path) -> bool:
    if dirpath.exists() and dirpath.is_dir():
        return True
    else:
        return False