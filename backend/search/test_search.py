#!/usr/bin/env python3
"""
Test script for the e-commerce search system.
This script tests all individual search engines and the master search coordinator.
"""

import sys
import os

# Add the parent directory to the path so we can import the search modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_individual_search_engines():
    """Test each individual search engine"""
    print("🧪 Testing Individual Search Engines...")
    
    try:
        # Test Flipkart Mobiles Search
        print("\n📱 Testing Flipkart Mobiles Search...")
        from search import FlipkartMobilesSearch
        flipkart_search = FlipkartMobilesSearch()
        results = flipkart_search.search("OPPO mobile", max_results=2)
        print(f"   ✅ Found {len(results)} OPPO mobiles")
        
        # Test Electronics Data Search
        print("\n💻 Testing Electronics Data Search...")
        from search import ElectronicsDataSearch
        electronics_search = ElectronicsDataSearch()
        results = electronics_search.search("laptop", max_results=2)
        print(f"   ✅ Found {len(results)} laptops")
        
        # Test Amazon Data Search
        print("\n🛒 Testing Amazon Data Search...")
        from search import AmazonDataSearch
        amazon_search = AmazonDataSearch()
        results = amazon_search.search("electronics", max_results=2)
        print(f"   ✅ Found {len(results)} electronics products")
        
        # Test General Dataset Search
        print("\n📦 Testing General Dataset Search...")
        from search import DatasetDataSearch
        dataset_search = DatasetDataSearch()
        results = dataset_search.search("product", max_results=2)
        print(f"   ✅ Found {len(results)} products")
        
        # Test Fashion Data Search
        print("\n👗 Testing Fashion Data Search...")
        from search import FashionDataSearch
        fashion_search = FashionDataSearch()
        results = fashion_search.search("saree", max_results=2)
        print(f"   ✅ Found {len(results)} sarees")
        
    except Exception as e:
        print(f"   ❌ Error testing individual search engines: {e}")
        return False
    
    return True

def test_master_search():
    """Test the master search coordinator"""
    print("\n🚀 Testing Master Search Coordinator...")
    
    try:
        from search import MasterSearch
        master = MasterSearch()
        
        # Test search across all datasets
        print("\n   🔍 Testing search across all datasets...")
        results = master.search_all_datasets("laptop", max_results_per_dataset=1, max_total_results=5)
        print(f"   ✅ Found {len(results)} laptops across all datasets")
        
        # Test specific dataset search
        print("\n   📱 Testing specific dataset search...")
        results = master.search_specific_dataset("flipkart_mobiles", "mobile", max_results=2)
        print(f"   ✅ Found {len(results)} mobiles in Flipkart dataset")
        
        # Test category search
        print("\n   🏷️ Testing category search...")
        results = master.search_by_category("saree", max_results_per_dataset=1, max_total_results=3)
        print(f"   ✅ Found {len(results)} sarees across fashion datasets")
        
        # Test price range search
        print("\n   💰 Testing price range search...")
        results = master.search_by_price_range(min_price=1000, max_price=5000, max_results_per_dataset=1, max_total_results=3)
        print(f"   ✅ Found {len(results)} products between ₹1,000-5,000")
        
        # Test dataset statistics
        print("\n   📊 Testing dataset statistics...")
        stats = master.get_dataset_stats()
        print(f"   ✅ Retrieved statistics for {len(stats)} datasets")
        
        # Test available datasets
        print("\n   📋 Testing available datasets...")
        datasets = master.get_available_datasets()
        print(f"   ✅ Found {len(datasets)} available datasets")
        
    except Exception as e:
        print(f"   ❌ Error testing master search: {e}")
        return False
    
    return True

def test_dataset_access():
    """Test if all dataset files are accessible"""
    print("\n📁 Testing Dataset File Access...")
    
    datasets = [
        '../Dataset/Flipkart_Mobiles.csv',
        '../Dataset/ElectronicsData.csv',
        '../Dataset/amazon.csv',
        '../Dataset/dataset.csv',
        '../Dataset/Data - Copy.csv'
    ]
    
    all_accessible = True
    for dataset_path in datasets:
        full_path = os.path.join(os.path.dirname(__file__), dataset_path)
        if os.path.exists(full_path):
            size_mb = os.path.getsize(full_path) / (1024 * 1024)
            print(f"   ✅ {dataset_path} - {size_mb:.1f}MB")
        else:
            print(f"   ❌ {dataset_path} - File not found")
            all_accessible = False
    
    return all_accessible

def main():
    """Main test function"""
    print("🎯 E-commerce Search System Test Suite")
    print("=" * 50)
    
    # Test dataset access
    if not test_dataset_access():
        print("\n❌ Dataset access test failed. Please check your dataset files.")
        return
    
    # Test individual search engines
    if not test_individual_search_engines():
        print("\n❌ Individual search engine tests failed.")
        return
    
    # Test master search
    if not test_master_search():
        print("\n❌ Master search tests failed.")
        return
    
    print("\n🎉 All tests passed successfully!")
    print("\n✅ Your e-commerce search system is working correctly.")
    print("\n📚 You can now use the search engines in your application:")
    print("   from backend.search import MasterSearch")
    print("   master = MasterSearch()")
    print("   results = master.search_all_datasets('your query')")

if __name__ == "__main__":
    main() 