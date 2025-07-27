"""
Search package for e-commerce datasets.

This package contains individual search engines for each dataset:
- flipkart_mobiles_data_search: For Flipkart mobile phones
- electronics_data_search: For electronics and gadgets
- amazon_data_search: For Amazon marketplace products
- dataset_data_search: For general mixed products
- fashion_data_search: For fashion items and clothing
- master_search: Master coordinator for all datasets

Each search engine is optimized for its specific dataset structure and provides
specialized search methods relevant to that dataset's content.
"""

from .flipkart_mobiles_data_search import FlipkartMobilesSearch
from .electronics_data_search import ElectronicsDataSearch
from .amazon_data_search import AmazonDataSearch
from .dataset_data_search import DatasetDataSearch
from .fashion_data_search import FashionDataSearch
from .master_search import MasterSearch

__all__ = [
    'FlipkartMobilesSearch',
    'ElectronicsDataSearch', 
    'AmazonDataSearch',
    'DatasetDataSearch',
    'FashionDataSearch',
    'MasterSearch'
]

# Version information
__version__ = '1.0.0'
__author__ = 'E-commerce Search System'
__description__ = 'Specialized search engines for multiple e-commerce datasets' 