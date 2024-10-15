import requests


def get_eco_score(barcode):
    """
    Tries to open the url and find information from OpenFoodFact.
    :param barcode: With barcode, items are searched
    :return: Return the values found or None if url can't be opened
    """
    url = f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json"
    response = requests.get(url)

    if response.status_code == 200:

        product_data = response.json()

        product = product_data.get('product', {})

        ecoscore_grade = product.get('ecoscore_grade', 'Eco score not found')

        ecoscore_score = product.get('ecoscore_score', 'Eco score not found')

        agribalyse = product.get('ecoscore_data', {}).get('agribalyse', {})
        name_en = agribalyse.get('name_en', 'Name not found')

        generic_name_en = product.get('generic_name_en', 'Generic name not '
                                                         'found')

        status = product_data.get('status_verbose')

        keywords = product.get('_keywords')
        keywords_joined = ""

        if keywords is not None:
            keywords_joined = ', '.join(keywords)

        if generic_name_en == "":
            generic_name_en = 'Generic name not found'

        if name_en == 'Name not found' and generic_name_en != "Generic name " \
                                                              "not found":
            name_en = generic_name_en

        return ecoscore_grade, ecoscore_score, name_en, keywords_joined, status

    else:
        print(f"Failed to fetch product data: {response.status_code}")
        return None
