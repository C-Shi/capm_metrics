"""capm_metric package"""
import logging
from .capm import CAPMAnalyzer

# Set logging level to ERROR to suppress lower level messages
logging.getLogger("yfinance").setLevel(logging.ERROR)
