__name__ = "ruaumoko"
__author__ = "Cambridge University Spaceflight <contact@cusf.co.uk>"
__version__ = "0.1.0"
__version_info__ = tuple([int(d) for d in __version__.split(".")])
__licence__ = "GPL v3"

from .dataset import Dataset
from .download import Downloader
