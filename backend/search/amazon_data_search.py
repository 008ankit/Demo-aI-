import os
import pandas as pd
import re

class AmazonDataSearch:
    def __init__(self):
        self.dataset_path = os.path.join(os.path.dirname(__file__), '../Dataset/amazon.csv')
        self.dataset_name = "Amazon Products"
    
    def build_product_card(self, row):
        """Build a product card specifically for Amazon data"""
        # Title: Use product_name column
        title = str(row.get('product_name', '')).strip() if pd.notnull(row.get('product_name')) else 'Amazon Product'
        
        # Price: Use discounted_price column
        price = 'N/A'
        if pd.notnull(row.get('discounted_price')):
            price_val = str(row.get('discounted_price')).replace('₹', '').replace(',', '').strip()
            if price_val and price_val != 'nan':
                price = f"₹{price_val}"
        
        # Rating: Use rating column
        rating = str(row.get('rating', 'N/A')).strip() if pd.notnull(row.get('rating')) else 'N/A'
        
        # Review: Build from category and rating count
        category = str(row.get('category', '')).strip() if pd.notnull(row.get('category')) else ''
        rating_count = str(row.get('rating_count', '')).strip() if pd.notnull(row.get('rating_count')) else ''
        
        review_parts = []
        if category:
            review_parts.append(f"Category: {category}")
        if rating_count:
            review_parts.append(f"Rated by {rating_count} users")
        
        review = ' | '.join(review_parts) if review_parts else 'Amazon product'
        
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
            'product_id': str(row.get('product_id', '')).strip() if pd.notnull(row.get('product_id')) else '',
            'category': category,
            'actual_price': str(row.get('actual_price', '')).strip() if pd.notnull(row.get('actual_price')) else '',
            'discount_percentage': str(row.get('discount_percentage', '')).strip() if pd.notnull(row.get('discount_percentage')) else '',
            'rating_count': rating_count
        }
    
    def search(self, query, max_results=5):
        """Search specifically in Amazon dataset"""
        query_lc = query.lower()
        results = []
        candidate_products = []
        
        # Price filter extraction for Amazon (INR)
        price_limit = None
        price_match = re.search(r'(under|below|less than|upto|up to|≤|<=|<)\s*₹?([\d,]+)', query_lc)
        if price_match:
            price_limit = int(price_match.group(2).replace(',', ''))
        
        # Extract Amazon-specific keywords
        query_main = query_lc
        if price_match:
            query_main = query_main[:price_match.start()].strip()
        
        # Amazon-specific stop words
        stop_words = ['under', 'below', 'less', 'than', 'upto', 'up', 'to', 'find', 'show', 'get', 'want', 'need', 'looking', 'for', 'amazon', 'product']
        keywords = [kw for kw in query_main.split() if kw not in stop_words and len(kw) > 2]
        
        try:
            # Read in chunks due to large file size
            for chunk in pd.read_csv(self.dataset_path, chunksize=1000):
                for _, row in chunk.iterrows():
                    # Build searchable text from Amazon-specific fields
                    searchable_fields = []
                    
                    # product_name is primary search field
                    if pd.notnull(row.get('product_name')):
                        searchable_fields.append(str(row['product_name']).lower())
                    
                    # category is secondary
                    if pd.notnull(row.get('category')):
                        searchable_fields.append(str(row['category']).lower())
                    
                    searchable_text = ' '.join(searchable_fields)
                    
                    # Price filtering for Amazon
                    if price_limit is not None:
                        discounted_price = row.get('discounted_price')
                        if pd.notnull(discounted_price):
                            price_str = str(discounted_price).replace('₹', '').replace(',', '').replace(' ', '')
                            digits = re.sub(r'[^\d]', '', price_str)
                            if digits:
                                found_price = int(digits)
                                if found_price > price_limit:
                                    continue
                    
                    # Keyword matching for Amazon search
                    match_count = sum(1 for kw in keywords if kw in searchable_text)
                    if match_count > 0 or not keywords:
                        product_card = self.build_product_card(row)
                        product_card['match_count'] = match_count
                        candidate_products.append(product_card)
                        
        except Exception as e:
            print(f"[AmazonDataSearch] Error reading dataset: {e}")
            return []
        
        # Sort by match count and return top results
        candidate_products.sort(key=lambda x: x.get('match_count', 0), reverse=True)
        return candidate_products[:max_results]
    
    def search_by_category(self, category, max_results=5):
        """Search Amazon products by specific category"""
        try:
            category_lower = category.lower()
            results = []
            
            for chunk in pd.read_csv(self.dataset_path, chunksize=1000):
                for _, row in chunk.iterrows():
                    if pd.notnull(row.get('category')):
                        if category_lower in str(row['category']).lower():
                            product_card = self.build_product_card(row)
                            results.append(product_card)
            
            return results[:max_results]
        except Exception as e:
            print(f"[AmazonDataSearch] Error in category search: {e}")
            return []
    
    def search_by_price_range(self, min_price=None, max_price=None, max_results=5):
        """Search Amazon products by price range"""
        try:
            results = []
            
            for chunk in pd.read_csv(self.dataset_path, chunksize=1000):
                for _, row in chunk.iterrows():
                    if pd.notnull(row.get('discounted_price')):
                        price_str = str(row['discounted_price']).replace('₹', '').replace(',', '').replace(' ', '')
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
            print(f"[AmazonDataSearch] Error in price range search: {e}")
            return []
    
    def search_with_discount(self, min_discount_percentage=10, max_results=5):
        """Search Amazon products with significant discounts"""
        try:
            results = []
            
            for chunk in pd.read_csv(self.dataset_path, chunksize=1000):
                for _, row in chunk.iterrows():
                    if pd.notnull(row.get('discount_percentage')):
                        discount_str = str(row['discount_percentage']).replace('%', '').strip()
                        if discount_str and discount_str != 'nan':
                            try:
                                discount = int(discount_str)
                                if discount >= min_discount_percentage:
                                    product_card = self.build_product_card(row)
                                    results.append(product_card)
                            except ValueError:
                                continue
            
            return results[:max_results]
        except Exception as e:
            print(f"[AmazonDataSearch] Error in discount search: {e}")
            return []
    
    def search_highly_rated(self, min_rating=4.0, max_results=5):
        """Search Amazon products with high ratings"""
        try:
            results = []
            
            for chunk in pd.read_csv(self.dataset_path, chunksize=1000):
                for _, row in chunk.iterrows():
                    if pd.notnull(row.get('rating')):
                        try:
                            rating = float(row['rating'])
                            if rating >= min_rating:
                                product_card = self.build_product_card(row)
                                results.append(product_card)
                        except ValueError:
                            continue
            
            return results[:max_results]
        except Exception as e:
            print(f"[AmazonDataSearch] Error in rating search: {e}")
            return []

# Example usage
if __name__ == "__main__":
    search = AmazonDataSearch()
    
    # Test general search
    results = search.search("laptop under 50000")
    print(f"Found {len(results)} laptops under ₹50,000")
    
    # Test category search
    category_results = search.search_by_category("electronics")
    print(f"Found {len(category_results)} electronics products")
    
    # Test price range search
    price_results = search.search_by_price_range(min_price=1000, max_price=5000)
    print(f"Found {len(price_results)} products between ₹1,000-5,000")
    
    # Test discount search
    discount_results = search.search_with_discount(min_discount_percentage=20)
    print(f"Found {len(discount_results)} products with 20%+ discount")
    
    # Test highly rated search
    rated_results = search.search_highly_rated(min_rating=4.5)
    print(f"Found {len(rated_results)} highly rated products") 