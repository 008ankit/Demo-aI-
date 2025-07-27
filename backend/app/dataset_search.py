import os
import pandas as pd
import re

DATASET_DIR = os.path.join(os.path.dirname(__file__), '../Dataset')
DATASET_FILES = [
    'dataset.csv',
    'Flipkart_Mobiles.csv',
    'Flipkart_mobile_brands_scraped_data.csv',
    'Data - Copy.csv',  # Added fashion dataset
    'ElectronicsData.csv', # New dataset
    'amazon.csv' # New dataset
]

# Helper to build a product card from a row
def build_product_card(row):
    # Try to build a title from all possible relevant columns
    title = None
    
    # Priority order for title fields
    title_fields = ['title', 'product_name', 'Product Name']
    for field in title_fields:
        if field in row and pd.notnull(row[field]) and str(row[field]).strip():
            title = str(row[field]).strip()
            break
    
    # If no title found, try to build from brand/model fields
    if not title:
        brand_model_parts = []
        for field in ['Brand', 'Model', 'Color', 'Memory', 'Storage']:
            if field in row and pd.notnull(row[field]) and str(row[field]).strip():
                brand_model_parts.append(str(row[field]).strip())
        if brand_model_parts:
            title = ' '.join(brand_model_parts)
    
    # Final fallback
    if not title or title.strip() == '':
        title = 'Product'

    # Price: try multiple price fields in priority order
    price = None
    price_fields = ['selling_price', 'sold_price', 'Selling Price', 'Price', 'discounted_price', 'actual_price', 'mrp']
    for field in price_fields:
        if field in row and pd.notnull(row[field]):
            price_val = str(row[field]).strip()
            if price_val and price_val != 'nan':
                # Clean price formatting
                price_val = price_val.replace('₹', '').replace(',', '').strip()
                if price_val:
                    price = f"₹{price_val}" if not price_val.startswith('₹') else price_val
                    break
    
    if not price or price == '₹':
        price = 'N/A'

    # Rating: try multiple rating fields
    rating = None
    rating_fields = ['rating', 'Rating', 'product_rating']
    for field in rating_fields:
        if field in row and pd.notnull(row[field]):
            rating_val = str(row[field]).strip()
            if rating_val and rating_val != 'nan':
                rating = rating_val
                break
    
    if not rating or rating == '':
        rating = 'N/A'

    # Review: try multiple review fields
    review = None
    review_fields = ['review', 'Review', 'description', 'about_product', 'highlights', 'Feature']
    for field in review_fields:
        if field in row and pd.notnull(row[field]):
            review_val = str(row[field]).strip()
            if review_val and review_val != 'nan' and len(review_val) > 10:
                review = review_val[:100] + '...' if len(review_val) > 100 else review_val
                break
    
    if not review or review == '':
        review = 'No description available'

    # Image: try multiple image fields
    image = None
    image_fields = ['img', 'image', 'img_link', 'image_links']
    for field in image_fields:
        if field in row and pd.notnull(row[field]):
            img_val = str(row[field]).strip()
            if img_val and img_val != 'nan' and img_val.startswith('http'):
                image = img_val
                break
    
    # Fallback to placeholder image
    if not image or image == '':
        image_id = abs(hash(title)) % 1000
        image = f"https://picsum.photos/400/400?random={image_id}"

    return {
        'title': title,
        'price': price,
        'rating': rating,
        'review': review,
        'image': image
    }

def search_datasets(query, max_results=5):
    query_lc = query.lower()
    results = []
    candidate_products = []

    # Price filter extraction
    price_limit = None
    price_match = re.search(r'(under|below|less than|upto|up to|≤|<=|<)\s*₹?([\d,]+)', query_lc)
    if price_match:
        price_limit = int(price_match.group(2).replace(',', ''))

    # Extract keywords (remove price-related words)
    query_main = query_lc
    if price_match:
        query_main = query_main[:price_match.start()].strip()
    stop_words = ['under', 'below', 'less', 'than', 'upto', 'up', 'to', 'find', 'show', 'get', 'want', 'need', 'looking', 'for', 'color', 'style']
    keywords = [kw for kw in query_main.split() if kw not in stop_words and len(kw) > 2]

    for fname in DATASET_FILES:
        fpath = os.path.join(DATASET_DIR, fname)
        if not os.path.exists(fpath):
            continue
        try:
            for chunk in pd.read_csv(fpath, chunksize=500):
                for _, row in chunk.iterrows():
                    # Build searchable text from relevant fields
                    searchable_fields = []
                    title_fields = ['title', 'product_name', 'Product Name', 'Brand', 'Model']
                    for field in title_fields:
                        if field in row and pd.notnull(row[field]):
                            searchable_fields.append(str(row[field]).lower())
                    category_fields = ['category', 'category_1', 'category_2', 'category_3', 'Sub Category']
                    for field in category_fields:
                        if field in row and pd.notnull(row[field]):
                            searchable_fields.append(str(row[field]).lower())
                    desc_fields = ['description', 'about_product', 'highlights', 'Feature']
                    for field in desc_fields:
                        if field in row and pd.notnull(row[field]):
                            searchable_fields.append(str(row[field]).lower())
                    searchable_text = ' '.join(searchable_fields)

                    # Price filtering
                    if price_limit is not None:
                        price_fields = ['Selling Price', 'sold_price', 'Price', 'actual_price', 'selling_price', 'mrp', 'discounted_price']
                        found_price = None
                        for pf in price_fields:
                            val = row.get(pf)
                            if pd.notnull(val):
                                price_str = str(val).replace('₹', '').replace(',', '').replace(' ', '')
                                digits = re.sub(r'[^\d]', '', price_str)
                                if digits:
                                    found_price = int(digits)
                                    break
                        if found_price is None or found_price > price_limit:
                            continue

                    # Flexible keyword matching: count how many keywords are present
                    match_count = sum(1 for kw in keywords if kw in searchable_text)
                    if match_count > 0 or not keywords:
                        product_card = build_product_card(row)
                        product_card['match_count'] = match_count
                        candidate_products.append(product_card)
        except Exception as e:
            print(f"[dataset_search] Error reading {fname}: {e}")
            continue
    # Sort by number of keyword matches (descending), then return top results
    candidate_products.sort(key=lambda x: x.get('match_count', 0), reverse=True)
    return candidate_products[:max_results] 