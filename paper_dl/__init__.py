"""paper_dl — Academic Paper Downloader"""

from paper_dl.config import get_config, load_config, set_config
from paper_dl.models import (
    AccessStatus,
    Author,
    DownloadStatus,
    DownloadTask,
    PaperMetadata,
    SearchQuery,
)

__version__ = "1.0.0"
__all__ = [
    "AccessStatus",
    "Author",
    "DownloadStatus",
    "DownloadTask",
    "PaperMetadata",
    "SearchQuery",
    "get_config",
    "load_config",
    "set_config",
]
