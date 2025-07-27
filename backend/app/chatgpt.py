# backend/app/chatgpt.py

import os
from openai import OpenAI # type: ignore
from dotenv import load_dotenv
import json
from .gemini import generate_multiple_product_images
import re
# Use the new master search system
from search import MasterSearch

# Instantiate master search (singleton for the app)
master_search = MasterSearch()

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

def ask_chatgpt(query: str):
    if not api_key:
        return {"error": "❌ OpenAI API key not found."}

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a friendly, conversational e-commerce assistant. "
                        "When asked for product recommendations, you must always respond with a warm, natural, and context-aware introduction (1-2 sentences) followed by a JSON array of 5 products. "
                        "Each product must have: title, price, rating, review. "
                        "Do NOT include any text after the JSON. If the user query is ambiguous, make reasonable assumptions and still return 5 realistic products. "
                        "The intro should come before the JSON, separated by a blank line."
                    )
                },
                {
                    "role": "user",
                    "content": (
                        f"Suggest 5 e-commerce products under budget for: {query}. "
                        "Use specific, well-known product names that are easily recognizable. "
                        "First, write a warm, conversational intro, then respond in this JSON format:\n"
                        "[\n"
                        "  {\n"
                        "    \"title\": \"Samsung Galaxy M34 5G\",\n"
                        "    \"price\": \"₹18,999\",\n"
                        "    \"rating\": \"4.3\",\n"
                        "    \"review\": \"Great camera quality, long battery life\"\n"
                        "  }\n"
                        "]\n"
                        "Do NOT include any text after the JSON."
                    )
                }
            ],
            temperature=0.7,
            max_tokens=800
        )

        content = response.choices[0].message.content.strip()

        try:
            # Use regex to extract the first JSON array from the response
            match = re.search(r'(\[.*?\])', content, re.DOTALL)
            if match:
                json_content = match.group(1)
                intro = content[:match.start()].strip()
                products = json.loads(json_content)
            else:
                # Try to extract product-like objects with a more robust regex
                product_matches = re.findall(r'\{[^}]*title[^}]*\}', content, re.DOTALL)
                products = []
                for prod_str in product_matches:
                    try:
                        prod = json.loads(prod_str.replace("'", '"'))
                        products.append(prod)
                    except Exception:
                        continue
                intro = content.split('\n')[0] if '\n' in content else "Here are some products you might like:"
                if not products:
                    print("[DEBUG] Raw AI response content (no products found):", content)
                    raise ValueError("No product JSON found")
            # Generate images for each product using Gemini
            image_results = generate_multiple_product_images(products)
            enhanced_products = []
            for i, product in enumerate(products):
                enhanced_product = product.copy()
                if i < len(image_results) and image_results[i]:
                    enhanced_product["image"] = image_results[i]["image_url"]
                else:
                    image_id = abs(hash(product.get('title', 'Product'))) % 1000
                    enhanced_product["image"] = f"https://picsum.photos/400/400?random={image_id}"
                enhanced_products.append(enhanced_product)
            return {"intro": intro, "products": enhanced_products}
        except Exception as e:
            print("[DEBUG] Raw AI response content (parse error):", content)
            print("❌ Failed to parse JSON from OpenAI:", content)
            print("JSON Error:", e)
            # Fallback: return a default set of product cards
            fallback_products = [
                {
                    "title": "Samsung Galaxy M34 5G",
                    "price": "₹18,999",
                    "rating": "4.3",
                    "review": "Great camera quality, long battery life",
                    "image": "https://picsum.photos/400/400?random=101"
                },
                {
                    "title": "Apple AirPods Pro",
                    "price": "₹19,999",
                    "rating": "4.5",
                    "review": "Excellent sound quality, noise cancellation",
                    "image": "https://picsum.photos/400/400?random=102"
                },
                {
                    "title": "Kindle Paperwhite",
                    "price": "₹10,999",
                    "rating": "4.8",
                    "review": "High-resolution display, long battery life",
                    "image": "https://picsum.photos/400/400?random=103"
                },
                {
                    "title": "Sony WH-1000XM4",
                    "price": "₹24,990",
                    "rating": "4.7",
                    "review": "Industry-leading noise cancellation",
                    "image": "https://picsum.photos/400/400?random=104"
                },
                {
                    "title": "Fitbit Versa 3",
                    "price": "₹15,999",
                    "rating": "4.2",
                    "review": "Accurate fitness tracking, long battery life",
                    "image": "https://picsum.photos/400/400?random=105"
                }
            ]
            return {"intro": "Here are some popular products you might like:", "products": fallback_products}

    except Exception as e:
        print("ChatGPT Error:", e)
        return {"error": "❌ AI failed to generate suggestions"}

def ask_chatgpt_general(message: str):
    # First, try to answer from the dataset using the new master search
    dataset_results = master_search.search_all_datasets(message)
    if dataset_results:
        return {
            "intro": "✨ Here are some top picks from our catalogue for your search:",
            "products": dataset_results
        }
    # Fallback to OpenAI if no dataset results
    if not api_key:
        return {"error": "❌ OpenAI API key not found."}
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a helpful, friendly AI assistant. Answer the user's questions conversationally. "
                        "If the user asks about products, you can answer, but otherwise, just chat normally."
                    )
                },
                {"role": "user", "content": message}
            ],
            temperature=0.7,
            max_tokens=500
        )
        content = response.choices[0].message.content.strip()
        return {"response": content}
    except Exception as e:
        print("ChatGPT General Error:", e)
        return {"error": "❌ AI failed to generate a response"}
