import os
import pandas as pd
import re

class ElectronicsDataSearch:
    def __init__(self):
        self.dataset_path = os.path.join(os.path.dirname(__file__), '../Dataset/ElectronicsData.csv')
        self.dataset_name = "Electronics Data"
    
    def build_product_card(self, row):
        """Build a product card specifically for Electronics data"""
        # Title: Use Title column
        title = str(row.get('Title', '')).strip() if pd.notnull(row.get('Title')) else 'Electronics Product'
        
        # Price: Use Price column (in USD)
        price = 'N/A'
        if pd.notnull(row.get('Price')):
            price_val = str(row.get('Price')).replace('$', '').replace(',', '').strip()
            if price_val and price_val != 'nan':
                price = f"${price_val}"
        
        # Rating: Use Rating column
        rating = str(row.get('Rating', 'N/A')).strip() if pd.notnull(row.get('Rating')) else 'N/A'
        
        # Review: Use Feature column
        review = str(row.get('Feature', '')).strip() if pd.notnull(row.get('Feature')) else 'No description available'
        if len(review) > 100:
            review = review[:100] + '...'
        
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
            'sub_category': str(row.get('Sub Category', '')).strip() if pd.notnull(row.get('Sub Category')) else '',
            'discount': str(row.get('Discount', '')).strip() if pd.notnull(row.get('Discount')) else '',
            'currency': str(row.get('Currency', '')).strip() if pd.notnull(row.get('Currency')) else '$'
        }
    
    def search(self, query, max_results=5):
        """Search specifically in Electronics dataset"""
        query_lc = query.lower()
        results = []
        candidate_products = []
        
        # Price filter extraction for electronics (USD)
        price_limit = None
        price_match = re.search(r'(under|below|less than|upto|up to|≤|<=|<)\s*\$?([\d,]+)', query_lc)
        if price_match:
            price_limit = int(price_match.group(2).replace(',', ''))
        
        # Extract electronics-specific keywords
        query_main = query_lc
        if price_match:
            query_main = query_main[:price_match.start()].strip()
        
        # Electronics-specific stop words
        stop_words = ['under', 'below', 'less', 'than', 'upto', 'up', 'to', 'find', 'show', 'get', 'want', 'need', 'looking', 'for', 'electronics', 'electronic', 'device']
        keywords = [kw for kw in query_main.split() if kw not in stop_words and len(kw) > 2]
        
        try:
            df = pd.read_csv(self.dataset_path)
            
            for _, row in df.iterrows():
                # Build searchable text from electronics-specific fields
                searchable_fields = []
                
                # Title is primary search field
                if pd.notnull(row.get('Title')):
                    searchable_fields.append(str(row['Title']).lower())
                
                # Sub Category is secondary
                if pd.notnull(row.get('Sub Category')):
                    searchable_fields.append(str(row['Sub Category']).lower())
                
                # Feature/description is tertiary
                if pd.notnull(row.get('Feature')):
                    searchable_fields.append(str(row['Feature']).lower())
                
                searchable_text = ' '.join(searchable_fields)
                
                # Price filtering for electronics
                if price_limit is not None:
                    price_val = row.get('Price')
                    if pd.notnull(price_val):
                        price_str = str(price_val).replace('$', '').replace(',', '').replace(' ', '')
                        digits = re.sub(r'[^\d]', '', price_str)
                        if digits:
                            found_price = int(digits)
                            if found_price > price_limit:
                                continue
                
                # Keyword matching for electronics search
                match_count = sum(1 for kw in keywords if kw in searchable_text)
                if match_count > 0 or not keywords:
                    product_card = self.build_product_card(row)
                    product_card['match_count'] = match_count
                    candidate_products.append(product_card)
                    
        except Exception as e:
            print(f"[ElectronicsDataSearch] Error reading dataset: {e}")
            return []
        
        # Sort by match count and return top results
        candidate_products.sort(key=lambda x: x.get('match_count', 0), reverse=True)
        return candidate_products[:max_results]
    
    def search_by_category(self, category, max_results=5):
        """Search electronics by specific category"""
        try:
            df = pd.read_csv(self.dataset_path)
            category_lower = category.lower()
            
            results = []
            for _, row in df.iterrows():
                if pd.notnull(row.get('Sub Category')):
                    if category_lower in str(row['Sub Category']).lower():
                        product_card = self.build_product_card(row)
                        results.append(product_card)
            
            return results[:max_results]
        except Exception as e:
            print(f"[ElectronicsDataSearch] Error in category search: {e}")
            return []
    
    def search_by_price_range(self, min_price=None, max_price=None, max_results=5):
        """Search electronics by price range"""
        try:
            df = pd.read_csv(self.dataset_path)
            results = []
            
            for _, row in df.iterrows():
                if pd.notnull(row.get('Price')):
                    price_str = str(row['Price']).replace('$', '').replace(',', '').replace(' ', '')
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
            print(f"[ElectronicsDataSearch] Error in price range search: {e}")
            return []
    
    def search_with_discount(self, max_results=5):
        """Search electronics that have discounts"""
        try:
            df = pd.read_csv(self.dataset_path)
            results = []
            
            for _, row in df.iterrows():
                discount = str(row.get('Discount', '')).strip() if pd.notnull(row.get('Discount')) else ''
                if discount and discount.lower() != 'no discount':
                    product_card = self.build_product_card(row)
                    results.append(product_card)
            
            return results[:max_results]
        except Exception as e:
            print(f"[ElectronicsDataSearch] Error in discount search: {e}")
            return []

# Example usage
if __name__ == "__main__":
    search = ElectronicsDataSearch()
    
    # Test general search
    results = search.search("laptop under 1000")
    print(f"Found {len(results)} laptops under $1000")
    
    # Test category search
    category_results = search.search_by_category("Desktop Computers")
    print(f"Found {len(category_results)} desktop computers")
    
    # Test price range search
    price_results = search.search_by_price_range(min_price=500, max_price=1000)
    print(f"Found {len(price_results)} electronics between $500-$1000")
    
    # Test discount search
    discount_results = search.search_with_discount()
    print(f"Found {len(discount_results)} electronics with discounts") 