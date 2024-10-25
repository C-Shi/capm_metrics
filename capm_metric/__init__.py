import logging

# Set logging level to ERROR to suppress lower level messages
logging.getLogger("yfinance").setLevel(logging.ERROR)

from .core import CAPMAnalyzer