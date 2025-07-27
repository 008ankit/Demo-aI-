import os
import pandas as pd
import re

class FashionDataSearch:
    def __init__(self):
        self.dataset_path = os.path.join(os.path.dirname(__file__), '../Dataset/Data - Copy.csv')
        self.dataset_name = "Fashion Data"
    
    def build_product_card(self, row):
        """Build a product card specifically for fashion data"""
        # Title: Use title column
        title = str(row.get('title', '')).strip() if pd.notnull(row.get('title')) else 'Fashion Item'
        
        # Price: Use sold_price column
        price = 'N/A'
        if pd.notnull(row.get('sold_price')):
            price_val = str(row.get('sold_price')).replace('₹', '').replace('â‚¹', '').replace(',', '').strip()
            if price_val and price_val != 'nan':
                price = f"₹{price_val}"
        
        # Rating: Not available in this dataset, use placeholder
        rating = 'N/A'
        
        # Review: Build from brand and title
        brand = str(row.get('brand', '')).strip() if pd.notnull(row.get('brand')) else ''
        review = f"{brand} - {title}" if brand else title
        
        # Image: Use img column if available, otherwise generate placeholder
        image = str(row.get('img', '')).strip() if pd.notnull(row.get('img')) else ''
        if not image or image == 'nan':
            image_id = abs(hash(title)) % 1000
            image = f"https://picsum.photos/400/400?random={image_id}"
        
        return {
            'title': title,
            'price': price,
            'rating': rating,
            'review': review,
            'image': image,
            'dataset': self.dataset_name,
            'brand': brand,
            'actual_price': str(row.get('actual_price', '')).strip() if pd.notnull(row.get('actual_price')) else '',
            'url': str(row.get('url', '')).strip() if pd.notnull(row.get('url')) else '',
            'id': str(row.get('id', '')).strip() if pd.notnull(row.get('id')) else ''
        }
    
    def search(self, query, max_results=5):
        """Search specifically in fashion dataset"""
        query_lc = query.lower()
        results = []
        candidate_products = []
        
        # Price filter extraction for fashion (INR)
        price_limit = None
        price_match = re.search(r'(under|below|less than|upto|up to|≤|<=|<)\s*₹?([\d,]+)', query_lc)
        if price_match:
            price_limit = int(price_match.group(2).replace(',', ''))
        
        # Extract fashion-specific keywords
        query_main = query_lc
        if price_match:
            query_main = query_main[:price_match.start()].strip()
        
        # Fashion-specific stop words
        stop_words = ['under', 'below', 'less', 'than', 'upto', 'up', 'to', 'find', 'show', 'get', 'want', 'need', 'looking', 'for', 'fashion', 'clothing', 'wear', 'dress']
        keywords = [kw for kw in query_main.split() if kw not in stop_words and len(kw) > 2]
        
        try:
            # Read in chunks due to large file size
            for chunk in pd.read_csv(self.dataset_path, chunksize=1000):
                for _, row in chunk.iterrows():
                    # Build searchable text from fashion-specific fields
                    searchable_fields = []
                    
                    # Title is primary search field
                    if pd.notnull(row.get('title')):
                        searchable_fields.append(str(row['title']).lower())
                    
                    # Brand is secondary
                    if pd.notnull(row.get('brand')):
                        searchable_fields.append(str(row['brand']).lower())
                    
                    searchable_text = ' '.join(searchable_fields)
                    
                    # Price filtering for fashion
                    if price_limit is not None:
                        sold_price = row.get('sold_price')
                        if pd.notnull(sold_price):
                            price_str = str(sold_price).replace('₹', '').replace('â‚¹', '').replace(',', '').replace(' ', '')
                            digits = re.sub(r'[^\d]', '', price_str)
                            if digits:
                                found_price = int(digits)
                                if found_price > price_limit:
                                    continue
                    
                    # Keyword matching for fashion search
                    match_count = sum(1 for kw in keywords if kw in searchable_text)
                    if match_count > 0 or not keywords:
                        product_card = self.build_product_card(row)
                        product_card['match_count'] = match_count
                        candidate_products.append(product_card)
                        
        except Exception as e:
            print(f"[FashionDataSearch] Error reading dataset: {e}")
            return []
        
        # Sort by match count and return top results
        candidate_products.sort(key=lambda x: x.get('match_count', 0), reverse=True)
        return candidate_products[:max_results]
    
    def search_by_brand(self, brand, max_results=5):
        """Search fashion items by specific brand"""
        try:
            brand_lower = brand.lower()
            results = []
            
            for chunk in pd.read_csv(self.dataset_path, chunksize=1000):
                for _, row in chunk.iterrows():
                    if pd.notnull(row.get('brand')):
                        if brand_lower in str(row['brand']).lower():
                            product_card = self.build_product_card(row)
                            results.append(product_card)
            
            return results[:max_results]
        except Exception as e:
            print(f"[FashionDataSearch] Error in brand search: {e}")
            return []
    
    def search_by_category(self, category, max_results=5):
        """Search fashion items by category (saree, dress, etc.)"""
        try:
            category_lower = category.lower()
            results = []
            
            for chunk in pd.read_csv(self.dataset_path, chunksize=1000):
                for _, row in chunk.iterrows():
                    if pd.notnull(row.get('title')):
                        if category_lower in str(row['title']).lower():
                            product_card = self.build_product_card(row)
                            results.append(product_card)
            
            return results[:max_results]
        except Exception as e:
            print(f"[FashionDataSearch] Error in category search: {e}")
            return []
    
    def search_by_price_range(self, min_price=None, max_price=None, max_results=5):
        """Search fashion items by price range"""
        try:
            results = []
            
            for chunk in pd.read_csv(self.dataset_path, chunksize=1000):
                for _, row in chunk.iterrows():
                    if pd.notnull(row.get('sold_price')):
                        price_str = str(row['sold_price']).replace('₹', '').replace('â‚¹', '').replace(',', '').replace(' ', '')
                        digits = re.sub(r'[^\d]', '', price_str)
                        if digits:
                            price = int(digits)
                            
                            # Check price range
                            if min_price is not None and price < min_price:
                                continue
                            if max_price is not None and price > max_price:
                                continue
                            
                            product_card = self.build_product_card(row)
                            results.append(product_card)
            
            return results[:max_results]
        except Exception as e:
            print(f"[FashionDataSearch] Error in price range search: {e}")
            return []
    
    def search_with_discount(self, min_discount_percentage=20, max_results=5):
        """Search fashion items with significant discounts"""
        try:
            results = []
            
            for chunk in pd.read_csv(self.dataset_path, chunksize=1000):
                for _, row in chunk.iterrows():
                    sold_price = row.get('sold_price')
                    actual_price = row.get('actual_price')
                    
                    if pd.notnull(sold_price) and pd.notnull(actual_price):
                        # Clean price strings
                        sold_str = str(sold_price).replace('₹', '').replace('â‚¹', '').replace(',', '').strip()
                        actual_str = str(actual_price).replace('₹', '').replace('â‚¹', '').replace(',', '').strip()
                        
                        if sold_str and actual_str and sold_str != 'nan' and actual_str != 'nan':
                            try:
                                sold = int(re.sub(r'[^\d]', '', sold_str))
                                actual = int(re.sub(r'[^\d]', '', actual_str))
                                
                                if actual > 0:
                                    discount_percentage = ((actual - sold) / actual) * 100
                                    if discount_percentage >= min_discount_percentage:
                                        product_card = self.build_product_card(row)
                                        results.append(product_card)
                            except ValueError:
                                continue
            
            return results[:max_results]
        except Exception as e:
            print(f"[FashionDataSearch] Error in discount search: {e}")
            return []
    
    def search_by_fabric_type(self, fabric_type, max_results=5):
        """Search fashion items by fabric type (silk, cotton, etc.)"""
        try:
            fabric_lower = fabric_type.lower()
            results = []
            
            for chunk in pd.read_csv(self.dataset_path, chunksize=1000):
                for _, row in chunk.iterrows():
                    if pd.notnull(row.get('title')):
                        if fabric_lower in str(row['title']).lower():
                            product_card = self.build_product_card(row)
                            results.append(product_card)
            
            return results[:max_results]
        except Exception as e:
            print(f"[FashionDataSearch] Error in fabric search: {e}")
            return []

# Example usage
if __name__ == "__main__":
    search = FashionDataSearch()
    
    # Test general search
    results = search.search("saree under 1000")
    print(f"Found {len(results)} sarees under ₹1,000")
    
    # Test brand search
    brand_results = search.search_by_brand("Vaidehi")
    print(f"Found {len(brand_results)} Vaidehi fashion items")
    
    # Test category search
    category_results = search.search_by_category("saree")
    print(f"Found {len(category_results)} sarees")
    
    # Test price range search
    price_results = search.search_by_price_range(min_price=500, max_price=2000)
    print(f"Found {len(price_results)} fashion items between ₹500-2,000")
    
    # Test discount search
    discount_results = search.search_with_discount(min_discount_percentage=50)
    print(f"Found {len(discount_results)} fashion items with 50%+ discount")
    
    # Test fabric search
    fabric_results = search.search_by_fabric_type("silk")
    print(f"Found {len(fabric_results)} silk items") 