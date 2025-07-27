import os
from .flipkart_mobiles_data_search import FlipkartMobilesSearch
from .electronics_data_search import ElectronicsDataSearch
from .amazon_data_search import AmazonDataSearch
from .dataset_data_search import DatasetDataSearch
from .fashion_data_search import FashionDataSearch

class MasterSearch:
    def __init__(self):
        """Initialize all dataset search engines"""
        self.search_engines = {
            'flipkart_mobiles': FlipkartMobilesSearch(),
            'electronics': ElectronicsDataSearch(),
            'amazon': AmazonDataSearch(),
            'general_dataset': DatasetDataSearch(),
            'fashion': FashionDataSearch()
        }
        
        # Dataset descriptions for better search targeting
        self.dataset_descriptions = {
            'flipkart_mobiles': 'Mobile phones and smartphones from Flipkart',
            'electronics': 'Electronics and gadgets from various categories',
            'amazon': 'General products from Amazon marketplace',
            'general_dataset': 'Mixed products from various categories',
            'fashion': 'Fashion items including sarees, clothing, and accessories'
        }
    
    def search_all_datasets(self, query, max_results_per_dataset=3, max_total_results=15):
        """Search across all datasets and return combined results"""
        all_results = []
        
        for dataset_name, search_engine in self.search_engines.items():
            try:
                results = search_engine.search(query, max_results_per_dataset)
                all_results.extend(results)
            except Exception as e:
                print(f"[MasterSearch] Error searching {dataset_name}: {e}")
                continue
        
        # Sort by match count and return top results
        all_results.sort(key=lambda x: x.get('match_count', 0), reverse=True)
        return all_results[:max_total_results]
    
    def search_specific_dataset(self, dataset_name, query, max_results=5):
        """Search in a specific dataset"""
        if dataset_name not in self.search_engines:
            raise ValueError(f"Dataset '{dataset_name}' not found. Available datasets: {list(self.search_engines.keys())}")
        
        return self.search_engines[dataset_name].search(query, max_results)
    
    def search_by_category(self, category, max_results_per_dataset=3, max_total_results=15):
        """Search for products by category across all datasets"""
        all_results = []
        
        # Map common categories to appropriate datasets
        category_mapping = {
            'mobile': ['flipkart_mobiles'],
            'phone': ['flipkart_mobiles'],
            'smartphone': ['flipkart_mobiles'],
            'electronics': ['electronics', 'amazon', 'general_dataset'],
            'laptop': ['electronics', 'amazon', 'general_dataset'],
            'computer': ['electronics', 'amazon', 'general_dataset'],
            'fashion': ['fashion'],
            'clothing': ['fashion'],
            'saree': ['fashion'],
            'dress': ['fashion'],
            'accessories': ['fashion', 'amazon', 'general_dataset']
        }
        
        category_lower = category.lower()
        target_datasets = []
        
        # Find matching datasets for the category
        for cat_key, datasets in category_mapping.items():
            if cat_key in category_lower:
                target_datasets.extend(datasets)
        
        # If no specific mapping, search all datasets
        if not target_datasets:
            target_datasets = list(self.search_engines.keys())
        
        # Remove duplicates
        target_datasets = list(set(target_datasets))
        
        for dataset_name in target_datasets:
            try:
                search_engine = self.search_engines[dataset_name]
                
                # Use category-specific search methods if available
                if hasattr(search_engine, 'search_by_category'):
                    results = search_engine.search_by_category(category, max_results_per_dataset)
                elif hasattr(search_engine, 'search_by_brand'):
                    results = search_engine.search_by_brand(category, max_results_per_dataset)
                else:
                    results = search_engine.search(category, max_results_per_dataset)
                
                all_results.extend(results)
            except Exception as e:
                print(f"[MasterSearch] Error searching {dataset_name} for category '{category}': {e}")
                continue
        
        # Sort by match count and return top results
        all_results.sort(key=lambda x: x.get('match_count', 0), reverse=True)
        return all_results[:max_total_results]
    
    def search_by_price_range(self, min_price=None, max_price=None, max_results_per_dataset=3, max_total_results=15):
        """Search for products by price range across all datasets"""
        all_results = []
        
        for dataset_name, search_engine in self.search_engines.items():
            try:
                if hasattr(search_engine, 'search_by_price_range'):
                    results = search_engine.search_by_price_range(min_price, max_price, max_results_per_dataset)
                    all_results.extend(results)
            except Exception as e:
                print(f"[MasterSearch] Error searching {dataset_name} by price range: {e}")
                continue
        
        # Sort by price (if available) and return top results
        all_results.sort(key=lambda x: self._extract_price(x.get('price', '0')))
        return all_results[:max_total_results]
    
    def search_with_discounts(self, min_discount_percentage=10, max_results_per_dataset=3, max_total_results=15):
        """Search for products with discounts across all datasets"""
        all_results = []
        
        for dataset_name, search_engine in self.search_engines.items():
            try:
                if hasattr(search_engine, 'search_with_discount'):
                    results = search_engine.search_with_discount(min_discount_percentage, max_results_per_dataset)
                    all_results.extend(results)
            except Exception as e:
                print(f"[MasterSearch] Error searching {dataset_name} for discounts: {e}")
                continue
        
        return all_results[:max_total_results]
    
    def get_available_datasets(self):
        """Get list of available datasets with descriptions"""
        return self.dataset_descriptions
    
    def get_dataset_stats(self):
        """Get basic statistics about each dataset"""
        stats = {}
        
        for dataset_name, search_engine in self.search_engines.items():
            try:
                dataset_path = search_engine.dataset_path
                if os.path.exists(dataset_path):
                    file_size = os.path.getsize(dataset_path)
                    stats[dataset_name] = {
                        'file_size_mb': round(file_size / (1024 * 1024), 2),
                        'description': self.dataset_descriptions.get(dataset_name, 'No description available')
                    }
                else:
                    stats[dataset_name] = {
                        'file_size_mb': 0,
                        'description': 'File not found',
                        'error': 'Dataset file not found'
                    }
            except Exception as e:
                stats[dataset_name] = {
                    'file_size_mb': 0,
                    'description': 'Error accessing dataset',
                    'error': str(e)
                }
        
        return stats
    
    def _extract_price(self, price_str):
        """Extract numeric price from price string for sorting"""
        try:
            # Remove currency symbols and commas
            clean_price = price_str.replace('₹', '').replace('$', '').replace(',', '').replace('â‚¹', '').strip()
            return float(clean_price) if clean_price and clean_price != 'N/A' else 0
        except:
            return 0

# Example usage
if __name__ == "__main__":
    master_search = MasterSearch()
    
    # Test search across all datasets
    print("=== Testing Master Search ===")
    
    # Search for laptops across all datasets
    results = master_search.search_all_datasets("laptop under 50000")
    print(f"Found {len(results)} laptops under ₹50,000 across all datasets")
    
    # Search in specific dataset
    mobile_results = master_search.search_specific_dataset("flipkart_mobiles", "Samsung mobile")
    print(f"Found {len(mobile_results)} Samsung mobiles in Flipkart dataset")
    
    # Search by category
    fashion_results = master_search.search_by_category("saree")
    print(f"Found {len(fashion_results)} sarees across fashion datasets")
    
    # Search by price range
    price_results = master_search.search_by_price_range(min_price=1000, max_price=5000)
    print(f"Found {len(price_results)} products between ₹1,000-5,000")
    
    # Search with discounts
    discount_results = master_search.search_with_discounts(min_discount_percentage=20)
    print(f"Found {len(discount_results)} products with 20%+ discount")
    
    # Get dataset statistics
    stats = master_search.get_dataset_stats()
    print("\n=== Dataset Statistics ===")
    for dataset, info in stats.items():
        print(f"{dataset}: {info['file_size_mb']}MB - {info['description']}") 