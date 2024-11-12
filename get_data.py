import requests


# Here is listed some data that can be used from OpenFoodFacts:
# Carbon footprint and ethics:
# "ecoscore_data": {
#   "adjustments": {
#       "origins_of_ingredients": {
#           "aggregated_origins": [
#               {
#                   "epi_score":,
#                   "origin":,
#                   "percent:",
#                   "transportation_score":
#               }
#           ],
#           "epi_score":,
#           "epi_value":,
#           "origins_from_categories": [
#           ],
#           "transportation_score":
#       },
#       "packaging": {
#           "non_recyclable_and_non_biodegradable_materials":,
#           "value":,
#           "warning":
#       },
#       "production_system": {
#           "labels":,
#           "value":,
#           "warning":
#       },
#       "threatened species": {
#       }
#   }
# }

# Nutrients:
# "nutrient_levels": {},
# "nutrient_levels_tags": [],
# "nutriments": {
#     "carbohydrates":,
#     "carbohydrates_100g":,
#     "carbohydrates_serving":,
#     "carbohydrates_unit":,
#     "carbohydrates_value":,
#     "energy":,
#     "energy-kcal":,
#     "energy-kcal_100g":,
#     "energy-kcal_serving":,
#     "energy-kcal_unit":,
#     "energy-kcal_value":,
#     "energy_100g":,
#     "energy_serving":,
#     "energy_unit":,
#     "energy_value":,
#     "sugars":,
#     "sugars_100g":,
#     "sugars_serving":,
#     "sugars_unit":,
#     "sugars_value":
# },
# "nutriscore": {
#             "2021": {
#                 "category_available":,
#                 "data": {
#                     "energy":,
#                     "fiber":,
#                     "fruits_vegetables_nuts_colza_walnut_olive_oils":,
#                     "is_beverage":,
#                     "is_cheese":,
#                     "is_fat":,
#                     "is_water":,
#                     "proteins":,
#                     "saturated_fat":,
#                     "sodium":,
#                     "sugars":
#                 },
#                 "grade":,
#                 "nutrients_available":,
#                 "nutriscore_applicable":,
#                 "nutriscore_computed":
#             },
#             "2023": {
#                 "category_available":,
#                 "data": {
#                     "energy":,
#                     "fiber":,
#                     "fruits_vegetables_legumes":,
#                     "is_beverage":,
#                     "is_cheese":,
#                     "is_fat_oil_nuts_seeds":,
#                     "is_red_meat_product":,
#                     "is_water":,
#                     "proteins":,
#                     "salt":,
#                     "saturated_fat":,
#                     "sugars":
#                 },
#                 "grade":,
#                 "nutrients_available":,
#                 "nutriscore_applicable":,
#                 "nutriscore_computed":
#             }
#         }
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
        co2_footprint = product.get('ecoscore_data', {}).\
            get('agribalyse', {}).get('co2_total', 'CO2 Footprint not found')


        return product_name, product_quantity, category, esg_score, \
               co2_footprint

def get_gluten_free(barcode):
    """
    Tries to open the url and find information from OpenFoodFact.
    :param barcode: With barcode, items are searched
    :return: Returns True if product is gluten free, False if it's not
    """
    url = f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json"
    response = requests.get(url)

    if response.status_code == 200:

        product_data = response.json()

        product = product_data.get('product', {})

        allergens = product.get('allergens_tags', 'Allergens not found')

        #if gluten is in allergens, it includes gluten
        if "en:gluten" in allergens:
            return False
        #otherwise not
        elif "Allergens not found" in allergens:
            return True
        else:
            return True

    else:
        print(f"Failed to fetch product data: {response.status_code}")
        return None
