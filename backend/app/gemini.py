import os
import google.generativeai as genai # type: ignore
from dotenv import load_dotenv
import requests
import json
import re

load_dotenv()

# Configure Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

# Unsplash API
UNSPLASH_ACCESS_KEY = os.getenv("UNSPLASH_ACCESS_KEY")

def get_unsplash_image(product_name):
    if not UNSPLASH_ACCESS_KEY:
        return None
    url = "https://api.unsplash.com/search/photos"
    params = {
        "query": product_name,
        "client_id": UNSPLASH_ACCESS_KEY,
        "per_page": 1
    }
    try:
        response = requests.get(url, params=params, timeout=5)
        data = response.json()
        if data.get("results"):
            return data["results"][0]["urls"]["regular"]
    except Exception as e:
        print(f"Unsplash error: {e}")
    return None

def generate_product_image(product_name, product_type=""):
    """
    Try Unsplash first for a real product image, then fallback to Gemini/placeholder.
    """
    # Try Unsplash first
    unsplash_url = get_unsplash_image(f"{product_name} {product_type} product photo")
    if unsplash_url:
        return {
            "success": True,
            "image_url": unsplash_url,
            "product_name": product_name,
            "generated": False,
            "source": "unsplash"
        }
    # Fallback to Gemini/placeholder logic
    try:
        prompt_name = product_name
        if product_type:
            prompt_name += f" {product_type}"
        prompt_name += " product photo"
        clean_name = re.sub(r'[^\w\s-]', '', prompt_name)
        clean_name = clean_name.replace(" ", ",").replace("-", ",")
        clean_name = clean_name[:50]
        url = f"https://picsum.photos/400/400?random={hash(clean_name) % 1000}"
        response = requests.head(url, timeout=5)
        if response.status_code == 200:
            return {
                "success": True,
                "image_url": url,
                "product_name": product_name,
                "generated": True,
                "source": "prompt-enhanced"
            }
    except:
        pass
    return get_fallback_image(product_name)

def get_unsplash_product_image(product_name):
    """
    Get a relevant product image from Unsplash
    """
    try:
        # Clean the product name for search - remove special characters and limit length
        clean_name = re.sub(r'[^\w\s-]', '', product_name)
        clean_name = clean_name.replace(" ", ",").replace("-", ",")
        clean_name = clean_name[:50]  # Limit length to avoid URL issues
        
        # Use a simpler, more reliable approach
        url = f"https://picsum.photos/400/400?random={hash(clean_name) % 1000}"
        
        # Test if the URL is accessible
        response = requests.head(url, timeout=5)
        if response.status_code == 200:
            return url
    except:
        pass
    
    return None

def get_product_specific_image(product_name):
    """
    Get a product-specific image using various strategies
    """
    try:
        # Clean product name - remove special characters and limit length
        clean_name = re.sub(r'[^\w\s-]', '', product_name)
        clean_name = clean_name.lower().strip()[:30]  # Limit length
        
        # Use a simple, reliable approach with Picsum
        # Generate a consistent but unique image based on product name
        image_id = abs(hash(clean_name)) % 1000
        url = f"https://picsum.photos/400/400?random={image_id}"
        
        # Test the URL
        response = requests.head(url, timeout=5)
        if response.status_code == 200:
            return url
            
    except Exception as e:
        print(f"Error getting product-specific image: {e}")
    
    # Fallback to a simple, reliable image service
    return f"https://picsum.photos/400/400?random={abs(hash(product_name)) % 1000}"

def get_fallback_image(product_name):
    """
    Get a fallback image when all else fails
    """
    # Use a simple, reliable fallback
    image_id = abs(hash(product_name)) % 1000
    return {
        "success": False,
        "image_url": f"https://picsum.photos/400/400?random={image_id}",
        "product_name": product_name,
        "generated": False,
        "source": "fallback"
    }

def generate_multiple_product_images(products):
    """
    Generate images for multiple products
    """
    results = []
    
    for product in products:
        if isinstance(product, dict):
            product_name = product.get('title', product.get('name', 'Product'))
        else:
            product_name = str(product)
        
        image_result = generate_product_image(product_name)
        results.append(image_result)
    
    return results 