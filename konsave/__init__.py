"""Top-level Konsave package."""

from pkg_resources import get_distribution, DistributionNotFound

try:
    __version__ = get_distribution("konsave-urban").version
except DistributionNotFound:
    # Package is not installed
    pass
