# backend/app/chatgpt.py

import os
from openai import OpenAI # type: ignore
from dotenv import load_dotenv
import json
from .gemini import generate_multiple_product_images

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
                        "When asked for product recommendations, first write a warm, natural, and context-aware introduction (1-2 sentences) that is personalized to the user's query. "
                        "The intro should sound like a real assistant, not a robot, and should avoid repeating the query verbatim. "
                        "For example, you might say: 'Looking for a great ASUS laptop on a budget? Here are some top picks you might like!' or 'Here are some excellent options for your search.' "
                        "After the intro, provide the product list strictly in JSON format. "
                        "Each item must include: title, price, rating, review. "
                        "Make sure to suggest realistic products with reasonable prices. "
                        "Use specific, recognizable product names that will work well for image search. "
                        "The intro sentence should come before the JSON, separated by a blank line."
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
                        "]"
                    )
                }
            ],
            temperature=0.7,
            max_tokens=800
        )

        content = response.choices[0].message.content.strip()

        try:
            # Split intro and JSON
            split_idx = content.find("[")
            intro = content[:split_idx].strip() if split_idx != -1 else ""
            json_start = split_idx
            json_end = content.rfind("]") + 1
            if json_start != -1 and json_end != -1:
                json_content = content[json_start:json_end]
                products = json.loads(json_content)
            else:
                # Fallback: try to parse the entire content
                products = json.loads(content)
                intro = ""
            # Generate images for each product using Gemini
            image_results = generate_multiple_product_images(products)
            # Combine product data with generated images
            enhanced_products = []
            for i, product in enumerate(products):
                enhanced_product = product.copy()
                if i < len(image_results) and image_results[i]:
                    enhanced_product["image"] = image_results[i]["image_url"]
                else:
                    # Use a simple, reliable fallback
                    image_id = abs(hash(product.get('title', 'Product'))) % 1000
                    enhanced_product["image"] = f"https://picsum.photos/400/400?random={image_id}"
                enhanced_products.append(enhanced_product)
            return {"intro": intro, "products": enhanced_products}
        except json.JSONDecodeError as e:
            print("❌ Failed to parse JSON from OpenAI:", content)
            print("JSON Error:", e)
            # Fallback: return a simple text response
            return {"error": "Invalid response format from AI", "fallback_text": content}

    except Exception as e:
        print("ChatGPT Error:", e)
        return {"error": "❌ AI failed to generate suggestions"}

def ask_chatgpt_general(message: str):
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
