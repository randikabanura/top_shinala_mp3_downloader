from pathlib import Path

def get_covers_root() -> Path:
    """Returns covers root folder."""
    return Path(__file__).parent

def get_downloader_root() -> Path:
    """Returns downloader root folder."""
    return Path(__file__).parent.parent