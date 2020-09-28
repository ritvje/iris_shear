__version__ = "unknown"
try:
    from ._version import __version__
except ImportError:
    # No version info available; don't care
    pass
from . import iristools, utils
__all__ = [s for s in dir() if not s.startswith('_')]
