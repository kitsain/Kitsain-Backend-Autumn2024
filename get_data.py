import requests

import requests

def fetch_product_from_OFF(barcode):
    """
    Fetch product details from OpenFoodFacts API based on the provided barcode.

    Parameters:
    - barcode (str): The barcode of the product to fetch.

    Returns:
    - dict: A dictionary containing product details.
    """
    url = f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json"
    response = requests.get(url)

    if response.status_code == 200:
        product_data = response.json()
        product = product_data.get('product', {})

        # Basic product details
        product_name = product.get('product_name', 'Product name not found')
        quantity = product.get('quantity', '')  # Raw quantity string (e.g., "500 g", "1 L")
        category = product.get('categories', 'Category not found')
        esg_score = product.get('ecoscore_grade', 'Ecoscore Grade not found')
        co2_footprint = product.get('ecoscore_data', {}).get('agribalyse', {}).get('co2_total', 'CO2 Footprint not found')
        brand = product.get('brands', 'Brand not found')
        information_links = product.get('link')
        allergens = product.get('allergens_tags', [])

        # Determine if the product is gluten-free
        gluten_free = get_gluten_free(product)

        # Image URL
        image = product.get('selected_images', {}).get('front', {}).get('display', {}).get('en', 'Image not found')

        # Parse quantity into weight and volume
        weight_g = None
        volume_l = None
        if quantity:
            quantity = quantity.lower().strip()
            if 'g' in quantity:
                try:
                    weight_g = int(float(quantity.replace('g', '').strip()))
                except ValueError:
                    weight_g = None  # Default to None if parsing fails
            elif 'ml' in quantity:
                try:
                    volume_l = float(quantity.replace('ml', '').strip()) / 1000  # Convert to liters
                except ValueError:
                    volume_l = None
            elif 'l' in quantity:
                try:
                    volume_l = float(quantity.replace('l', '').strip())
                except ValueError:
                    volume_l = None

        return {
            'product_name': product_name,
            'weight_g': weight_g,
            'volume_l': volume_l,
            'category': category,
            'esg_score': esg_score,
            'co2_footprint': co2_footprint,
            'brand': brand,
            'information_links': information_links,
            'allergens': allergens,
            'gluten_free': gluten_free,
            'image': image
        }

    return {'error': 'Product not found or API request failed'}

def get_gluten_free(product):
    """
    Determine if the product is gluten-free.

    Parameters:
    - product (dict): The product details from OpenFoodFacts.

    Returns:
    - bool: True if gluten-free, False otherwise.
    """
    allergens = product.get('allergens_tags', [])
    return 'en:gluten' not in allergens

