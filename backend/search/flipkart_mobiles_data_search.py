import os
import pandas as pd
import re

class FlipkartMobilesSearch:
    def __init__(self):
        self.dataset_path = os.path.join(os.path.dirname(__file__), '../Dataset/Flipkart_Mobiles.csv')
        self.dataset_name = "Flipkart Mobiles"
    
    def build_product_card(self, row):
        """Build a product card specifically for Flipkart mobile data"""
        # Title: Combine Brand and Model
        brand = str(row.get('Brand', '')).strip() if pd.notnull(row.get('Brand')) else ''
        model = str(row.get('Model', '')).strip() if pd.notnull(row.get('Model')) else ''
        title = f"{brand} {model}".strip() if brand and model else 'Mobile Phone'
        
        # Price: Use Selling Price
        price = 'N/A'
        if pd.notnull(row.get('Selling Price')):
            price_val = str(row.get('Selling Price')).replace('₹', '').replace(',', '').strip()
            if price_val and price_val != 'nan':
                price = f"₹{price_val}"
        
        # Rating: Use Rating column
        rating = str(row.get('Rating', 'N/A')).strip() if pd.notnull(row.get('Rating')) else 'N/A'
        
        # Review: Build from specifications
        specs = []
        for field in ['Color', 'Memory', 'Storage']:
            if field in row and pd.notnull(row[field]):
                specs.append(str(row[field]).strip())
        
        review = f"{brand} {model} - {', '.join(specs)}" if specs else f"{brand} {model}"
        
        # Image: Generate placeholder based on brand
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
            'model': model,
            'color': str(row.get('Color', '')).strip() if pd.notnull(row.get('Color')) else '',
            'memory': str(row.get('Memory', '')).strip() if pd.notnull(row.get('Memory')) else '',
            'storage': str(row.get('Storage', '')).strip() if pd.notnull(row.get('Storage')) else ''
        }
    
    def search(self, query, max_results=5):
        """Search specifically in Flipkart mobiles dataset"""
        query_lc = query.lower()
        results = []
        candidate_products = []
        
        # Price filter extraction for mobiles
        price_limit = None
        price_match = re.search(r'(under|below|less than|upto|up to|≤|<=|<)\s*₹?([\d,]+)', query_lc)
        if price_match:
            price_limit = int(price_match.group(2).replace(',', ''))
        
        # Extract mobile-specific keywords
        query_main = query_lc
        if price_match:
            query_main = query_main[:price_match.start()].strip()
        
        # Mobile-specific stop words
        stop_words = ['under', 'below', 'less', 'than', 'upto', 'up', 'to', 'find', 'show', 'get', 'want', 'need', 'looking', 'for', 'mobile', 'phone', 'smartphone']
        keywords = [kw for kw in query_main.split() if kw not in stop_words and len(kw) > 2]
        
        try:
            df = pd.read_csv(self.dataset_path)
            
            for _, row in df.iterrows():
                # Build searchable text from mobile-specific fields
                searchable_fields = []
                
                # Brand and Model are primary search fields
                for field in ['Brand', 'Model']:
                    if field in row and pd.notnull(row[field]):
                        searchable_fields.append(str(row[field]).lower())
                
                # Color, Memory, Storage are secondary
                for field in ['Color', 'Memory', 'Storage']:
                    if field in row and pd.notnull(row[field]):
                        searchable_fields.append(str(row[field]).lower())
                
                searchable_text = ' '.join(searchable_fields)
                
                # Price filtering for mobiles
                if price_limit is not None:
                    selling_price = row.get('Selling Price')
                    if pd.notnull(selling_price):
                        price_str = str(selling_price).replace('₹', '').replace(',', '').replace(' ', '')
                        digits = re.sub(r'[^\d]', '', price_str)
                        if digits:
                            found_price = int(digits)
                            if found_price > price_limit:
                                continue
                
                # Keyword matching for mobile search
                match_count = sum(1 for kw in keywords if kw in searchable_text)
                if match_count > 0 or not keywords:
                    product_card = self.build_product_card(row)
                    product_card['match_count'] = match_count
                    candidate_products.append(product_card)
                    
        except Exception as e:
            print(f"[FlipkartMobilesSearch] Error reading dataset: {e}")
            return []
        
        # Sort by match count and return top results
        candidate_products.sort(key=lambda x: x.get('match_count', 0), reverse=True)
        return candidate_products[:max_results]
    
    def search_by_brand(self, brand, max_results=5):
        """Search mobiles by specific brand"""
        try:
            df = pd.read_csv(self.dataset_path)
            brand_lower = brand.lower()
            
            results = []
            for _, row in df.iterrows():
                if pd.notnull(row.get('Brand')):
                    if brand_lower in str(row['Brand']).lower():
                        product_card = self.build_product_card(row)
                        results.append(product_card)
            
            return results[:max_results]
        except Exception as e:
            print(f"[FlipkartMobilesSearch] Error in brand search: {e}")
            return []
    
    def search_by_price_range(self, min_price=None, max_price=None, max_results=5):
        """Search mobiles by price range"""
        try:
            df = pd.read_csv(self.dataset_path)
            results = []
            
            for _, row in df.iterrows():
                if pd.notnull(row.get('Selling Price')):
                    price_str = str(row['Selling Price']).replace('₹', '').replace(',', '').replace(' ', '')
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
            print(f"[FlipkartMobilesSearch] Error in price range search: {e}")
            return []

# Example usage
if __name__ == "__main__":
    search = FlipkartMobilesSearch()
    
    # Test general search
    results = search.search("Samsung mobile under 20000")
    print(f"Found {len(results)} Samsung mobiles under ₹20,000")
    
    # Test brand search
    brand_results = search.search_by_brand("OPPO")
    print(f"Found {len(brand_results)} OPPO mobiles")
    
    # Test price range search
    price_results = search.search_by_price_range(min_price=10000, max_price=15000)
    print(f"Found {len(price_results)} mobiles between ₹10,000-15,000") 