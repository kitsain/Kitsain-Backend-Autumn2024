import requests

def fetch_product_from_OFF(barcode):
    url = f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json"
    response = requests.get(url)

    if response.status_code == 200:
        product_data = response.json()
        product = product_data.get('product', {})

        product_name = product.get('product_name', 'Product name not found')
        product_quantity = product.get('quantity', 'Quantity not found')
        category = product.get('compared_to_category', 'Category not found')
        esg_score = product.get('ecoscore_grade', 'Ecoscore Grade not found')
        co2_footprint = product.get('ecoscore_data', {}). \
            get('agribalyse', {}).get('co2_total', 'CO2 Footprint not found')
        brand = product.get('brands', 'Brand not found')
        information_links = product.get('link')

        allergens = product.get('allergens_tags', [])

        gluten_free = get_gluten_free(product)

        image = product.get('selected_images', {}).get('front', {}).get(
            'display', {}).get('en', 'Image not found')

        return {
            'product_name': product_name,
            'product_quantity': product_quantity,
            'category': category,
            'esg_score': esg_score,
            'co2_footprint': co2_footprint,
            'brand': brand,
            'information_links': information_links,
            'allergens': allergens,
            'gluten_free': gluten_free,
            'image': image
        }


def get_gluten_free(product):
    """
    Tries to open the url and find information from OpenFoodFact.
    :param barcode: With barcode, items are searched
    :return: Returns True if product is gluten free, False if it's not
    """

    allergens = product.get('allergens_tags', [])

    # if gluten is in allergens, it includes gluten
    if "en:gluten" in allergens:
        return False
    # otherwise not
    elif "Allergens not found" in allergens:
        return True
    else:
        return True

