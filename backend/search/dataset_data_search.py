import os
import pandas as pd
import re

class DatasetDataSearch:
    def __init__(self):
        self.dataset_path = os.path.join(os.path.dirname(__file__), '../Dataset/dataset.csv')
        self.dataset_name = "General Dataset"
    
    def build_product_card(self, row):
        """Build a product card specifically for dataset.csv data"""
        # Title: Use title column
        title = str(row.get('title', '')).strip() if pd.notnull(row.get('title')) else 'Product'
        
        # Price: Use selling_price column
        price = 'N/A'
        if pd.notnull(row.get('selling_price')):
            price_val = str(row.get('selling_price')).replace('₹', '').replace(',', '').strip()
            if price_val and price_val != 'nan':
                price = f"₹{price_val}"
        
        # Rating: Use product_rating column
        rating = str(row.get('product_rating', 'N/A')).strip() if pd.notnull(row.get('product_rating')) else 'N/A'
        
        # Review: Build from description and categories
        description = str(row.get('description', '')).strip() if pd.notnull(row.get('description')) else ''
        categories = []
        for cat_field in ['category_1', 'category_2', 'category_3']:
            if pd.notnull(row.get(cat_field)):
                cat_val = str(row[cat_field]).strip()
                if cat_val and cat_val != 'nan':
                    categories.append(cat_val)
        
        review_parts = []
        if categories:
            review_parts.append(f"Categories: {', '.join(categories)}")
        if description and len(description) > 10:
            review_parts.append(description[:80] + '...' if len(description) > 80 else description)
        
        review = ' | '.join(review_parts) if review_parts else 'Product from general dataset'
        
        # Image: Generate placeholder based on title
        image_id = abs(hash(title)) % 1000
        image = f"https://picsum.photos/400/400?random={image_id}"
        
        return {
            'title': title,
            'price': price,
            'rating': rating,
            'review': review,
            'image': image,
            'dataset': self.dataset_name,
            'category_1': str(row.get('category_1', '')).strip() if pd.notnull(row.get('category_1')) else '',
            'category_2': str(row.get('category_2', '')).strip() if pd.notnull(row.get('category_2')) else '',
            'category_3': str(row.get('category_3', '')).strip() if pd.notnull(row.get('category_3')) else '',
            'mrp': str(row.get('mrp', '')).strip() if pd.notnull(row.get('mrp')) else '',
            'seller_name': str(row.get('seller_name', '')).strip() if pd.notnull(row.get('seller_name')) else '',
            'seller_rating': str(row.get('seller_rating', '')).strip() if pd.notnull(row.get('seller_rating')) else ''
        }
    
    def search(self, query, max_results=5):
        """Search specifically in dataset.csv"""
        query_lc = query.lower()
        results = []
        candidate_products = []
        
        # Price filter extraction
        price_limit = None
        price_match = re.search(r'(under|below|less than|upto|up to|≤|<=|<)\s*₹?([\d,]+)', query_lc)
        if price_match:
            price_limit = int(price_match.group(2).replace(',', ''))
        
        # Extract keywords
        query_main = query_lc
        if price_match:
            query_main = query_main[:price_match.start()].strip()
        
        # Stop words
        stop_words = ['under', 'below', 'less', 'than', 'upto', 'up', 'to', 'find', 'show', 'get', 'want', 'need', 'looking', 'for']
        keywords = [kw for kw in query_main.split() if kw not in stop_words and len(kw) > 2]
        
        try:
            # Read in chunks due to large file size
            for chunk in pd.read_csv(self.dataset_path, chunksize=1000):
                for _, row in chunk.iterrows():
                    # Build searchable text from all relevant fields
                    searchable_fields = []
                    
                    # Title is primary search field
                    if pd.notnull(row.get('title')):
                        searchable_fields.append(str(row['title']).lower())
                    
                    # Categories are secondary
                    for cat_field in ['category_1', 'category_2', 'category_3']:
                        if pd.notnull(row.get(cat_field)):
                            searchable_fields.append(str(row[cat_field]).lower())
                    
                    # Description is tertiary
                    if pd.notnull(row.get('description')):
                        searchable_fields.append(str(row['description']).lower())
                    
                    searchable_text = ' '.join(searchable_fields)
                    
                    # Price filtering
                    if price_limit is not None:
                        selling_price = row.get('selling_price')
                        if pd.notnull(selling_price):
                            price_str = str(selling_price).replace('₹', '').replace(',', '').replace(' ', '')
                            digits = re.sub(r'[^\d]', '', price_str)
                            if digits:
                                found_price = int(digits)
                                if found_price > price_limit:
                                    continue
                    
                    # Keyword matching
                    match_count = sum(1 for kw in keywords if kw in searchable_text)
                    if match_count > 0 or not keywords:
                        product_card = self.build_product_card(row)
                        product_card['match_count'] = match_count
                        candidate_products.append(product_card)
                        
        except Exception as e:
            print(f"[DatasetDataSearch] Error reading dataset: {e}")
            return []
        
        # Sort by match count and return top results
        candidate_products.sort(key=lambda x: x.get('match_count', 0), reverse=True)
        return candidate_products[:max_results]
    
    def search_by_category(self, category, max_results=5):
        """Search products by specific category"""
        try:
            category_lower = category.lower()
            results = []
            
            for chunk in pd.read_csv(self.dataset_path, chunksize=1000):
                for _, row in chunk.iterrows():
                    # Check all category fields
                    for cat_field in ['category_1', 'category_2', 'category_3']:
                        if pd.notnull(row.get(cat_field)):
                            if category_lower in str(row[cat_field]).lower():
                                product_card = self.build_product_card(row)
                                results.append(product_card)
                                break  # Found in one category, no need to check others
            
            return results[:max_results]
        except Exception as e:
            print(f"[DatasetDataSearch] Error in category search: {e}")
            return []
    
    def search_by_seller(self, seller_name, max_results=5):
        """Search products by specific seller"""
        try:
            seller_lower = seller_name.lower()
            results = []
            
            for chunk in pd.read_csv(self.dataset_path, chunksize=1000):
                for _, row in chunk.iterrows():
                    if pd.notnull(row.get('seller_name')):
                        if seller_lower in str(row['seller_name']).lower():
                            product_card = self.build_product_card(row)
                            results.append(product_card)
            
            return results[:max_results]
        except Exception as e:
            print(f"[DatasetDataSearch] Error in seller search: {e}")
            return []
    
    def search_by_price_range(self, min_price=None, max_price=None, max_results=5):
        """Search products by price range"""
        try:
            results = []
            
            for chunk in pd.read_csv(self.dataset_path, chunksize=1000):
                for _, row in chunk.iterrows():
                    if pd.notnull(row.get('selling_price')):
                        price_str = str(row['selling_price']).replace('₹', '').replace(',', '').replace(' ', '')
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
            print(f"[DatasetDataSearch] Error in price range search: {e}")
            return []
    
    def search_highly_rated_sellers(self, min_seller_rating=4.0, max_results=5):
        """Search products from highly rated sellers"""
        try:
            results = []
            
            for chunk in pd.read_csv(self.dataset_path, chunksize=1000):
                for _, row in chunk.iterrows():
                    if pd.notnull(row.get('seller_rating')):
                        try:
                            seller_rating = float(row['seller_rating'])
                            if seller_rating >= min_seller_rating:
                                product_card = self.build_product_card(row)
                                results.append(product_card)
                        except ValueError:
                            continue
            
            return results[:max_results]
        except Exception as e:
            print(f"[DatasetDataSearch] Error in seller rating search: {e}")
            return []

# Example usage
if __name__ == "__main__":
    search = DatasetDataSearch()
    
    # Test general search
    results = search.search("electronics under 10000")
    print(f"Found {len(results)} electronics under ₹10,000")
    
    # Test category search
    category_results = search.search_by_category("electronics")
    print(f"Found {len(category_results)} electronics products")
    
    # Test seller search
    seller_results = search.search_by_seller("amazon")
    print(f"Found {len(seller_results)} products from Amazon")
    
    # Test price range search
    price_results = search.search_by_price_range(min_price=1000, max_price=5000)
    print(f"Found {len(price_results)} products between ₹1,000-5,000")
    
    # Test highly rated sellers
    rated_seller_results = search.search_highly_rated_sellers(min_seller_rating=4.5)
    print(f"Found {len(rated_seller_results)} products from highly rated sellers") 