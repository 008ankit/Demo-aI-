# E-commerce Dataset Search System

This directory contains specialized search engines for each of your 5 e-commerce datasets. Each search engine is optimized for its specific dataset structure and provides relevant search functionality.

## 📁 File Structure

```
backend/search/
├── __init__.py                    # Package initialization
├── README.md                      # This documentation
├── flipkart_mobiles_data_search.py    # Flipkart mobile phones
├── electronics_data_search.py         # Electronics and gadgets
├── amazon_data_search.py             # Amazon marketplace products
├── dataset_data_search.py            # General mixed products
├── fashion_data_search.py            # Fashion items and clothing
└── master_search.py                  # Master coordinator for all datasets
```

## 🎯 Individual Search Engines

### 1. Flipkart Mobiles Search (`flipkart_mobiles_data_search.py`)

**Dataset**: `Flipkart_Mobiles.csv`
**Specialization**: Mobile phones and smartphones
**Key Features**:

- Brand and model-based search
- Memory and storage filtering
- Color options
- Price range search
- Mobile-specific stop words

**Example Usage**:

```python
from search import FlipkartMobilesSearch

search = FlipkartMobilesSearch()
results = search.search("Samsung mobile under 20000")
brand_results = search.search_by_brand("OPPO")
price_results = search.search_by_price_range(min_price=10000, max_price=15000)
```

### 2. Electronics Data Search (`electronics_data_search.py`)

**Dataset**: `ElectronicsData.csv`
**Specialization**: Electronics and gadgets
**Key Features**:

- Category-based search (Desktop Computers, Cameras, etc.)
- USD pricing support
- Feature-based descriptions
- Discount filtering
- Electronics-specific search logic

**Example Usage**:

```python
from search import ElectronicsDataSearch

search = ElectronicsDataSearch()
results = search.search("laptop under 1000")
category_results = search.search_by_category("Desktop Computers")
discount_results = search.search_with_discount()
```

### 3. Amazon Data Search (`amazon_data_search.py`)

**Dataset**: `amazon.csv`
**Specialization**: Amazon marketplace products
**Key Features**:

- Large dataset handling (chunked reading)
- Product rating and review count
- Discount percentage filtering
- Category-based search
- Highly rated product search

**Example Usage**:

```python
from search import AmazonDataSearch

search = AmazonDataSearch()
results = search.search("laptop under 50000")
category_results = search.search_by_category("electronics")
rated_results = search.search_highly_rated(min_rating=4.5)
```

### 4. General Dataset Search (`dataset_data_search.py`)

**Dataset**: `dataset.csv`
**Specialization**: Mixed products from various categories
**Key Features**:

- Multi-level category search (category_1, category_2, category_3)
- Seller-based search
- Seller rating filtering
- Comprehensive product descriptions
- Flexible search across multiple fields

**Example Usage**:

```python
from search import DatasetDataSearch

search = DatasetDataSearch()
results = search.search("electronics under 10000")
seller_results = search.search_by_seller("amazon")
rated_seller_results = search.search_highly_rated_sellers(min_seller_rating=4.5)
```

### 5. Fashion Data Search (`fashion_data_search.py`)

**Dataset**: `Data - Copy.csv`
**Specialization**: Fashion items and clothing
**Key Features**:

- Fashion-specific search (sarees, dresses, etc.)
- Brand-based search
- Fabric type filtering (silk, cotton, etc.)
- Discount calculation and filtering
- Image URL support

**Example Usage**:

```python
from search import FashionDataSearch

search = FashionDataSearch()
results = search.search("saree under 1000")
brand_results = search.search_by_brand("Vaidehi")
fabric_results = search.search_by_fabric_type("silk")
discount_results = search.search_with_discount(min_discount_percentage=50)
```

## 🚀 Master Search Coordinator

The `master_search.py` file provides a unified interface to search across all datasets:

### Key Features:

- **Cross-dataset search**: Search all datasets with one call
- **Smart category mapping**: Automatically routes searches to relevant datasets
- **Price range search**: Search across all datasets by price
- **Discount search**: Find discounted products across all datasets
- **Dataset statistics**: Get information about available datasets

### Example Usage:

```python
from search import MasterSearch

# Initialize master search
master = MasterSearch()

# Search across all datasets
results = master.search_all_datasets("laptop under 50000")

# Search specific dataset
mobile_results = master.search_specific_dataset("flipkart_mobiles", "Samsung mobile")

# Search by category (automatically targets relevant datasets)
fashion_results = master.search_by_category("saree")

# Search by price range
price_results = master.search_by_price_range(min_price=1000, max_price=5000)

# Search for discounted products
discount_results = master.search_with_discounts(min_discount_percentage=20)

# Get dataset information
stats = master.get_dataset_stats()
available_datasets = master.get_available_datasets()
```

## 🔧 Installation and Setup

1. **Dependencies**: Make sure you have the required packages:

   ```bash
   pip install pandas
   ```

2. **Dataset Files**: Ensure all CSV files are in the `../Dataset/` directory:

   - `Flipkart_Mobiles.csv`
   - `ElectronicsData.csv`
   - `amazon.csv`
   - `dataset.csv`
   - `Data - Copy.csv`

3. **Import**: Import the search engines:
   ```python
   from backend.search import MasterSearch, FlipkartMobilesSearch, ElectronicsDataSearch
   ```

## 🎯 Benefits of This Approach

### ✅ **Clear Separation**

- Each dataset has its own dedicated search logic
- No confusion about which results come from which dataset
- Easy to understand and maintain

### ✅ **Optimized Performance**

- Each search engine is optimized for its specific dataset structure
- Efficient handling of large files (chunked reading)
- Dataset-specific search algorithms

### ✅ **Specialized Features**

- Mobile-specific search (brand, model, memory, storage)
- Electronics category filtering
- Fashion fabric and brand search
- Amazon rating and discount features
- Seller-based search for general dataset

### ✅ **Easy Maintenance**

- Modify one dataset's search without affecting others
- Add new datasets by creating new search files
- Clear error handling and logging

### ✅ **Flexible Usage**

- Use individual search engines for specific needs
- Use master search for comprehensive results
- Mix and match based on requirements

## 🐛 Troubleshooting

### Common Issues:

1. **File Not Found**: Ensure all CSV files are in the correct location
2. **Memory Issues**: Large datasets use chunked reading to prevent memory problems
3. **Import Errors**: Make sure the search directory is in your Python path

### Error Handling:

- Each search engine includes comprehensive error handling
- Failed searches return empty lists instead of crashing
- Detailed error messages help with debugging

## 📈 Performance Tips

1. **Use Specific Datasets**: If you know which dataset contains your target products, use the specific search engine
2. **Limit Results**: Use `max_results` parameter to limit the number of results
3. **Chunked Reading**: Large datasets automatically use chunked reading for better performance
4. **Category Filtering**: Use category-specific search methods for faster results

## 🔄 Future Enhancements

- Add caching for frequently searched queries
- Implement fuzzy matching for better search results
- Add support for more complex filters
- Create web API endpoints for the search engines
- Add result ranking and relevance scoring
