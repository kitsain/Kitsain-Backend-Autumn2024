import datetime


def print_foods_data(waste_data):
    """
    Formats the print according to the information in the database (the longest
    word). Spaces are added to make the output look readable.
    :param waste_data: Contains the data in the database
    :return: Returns to the call function
    """

    longest_barcode = max(len("Barcode"),
                          max(len(str(w[0])) for w in waste_data))
    longest_food = max(len("Food"), max(len(w[1]) for w in waste_data))
    longest_expiry_date = len("Expiry Date")
    longest_ecoscore_grade = max(len("Ecoscore Grade"),
                                 max(len(w[3]) for w in waste_data))
    longest_ecoscore_score = max(len("Ecoscore Score"),
                                 max(len(str(w[4])) for w in waste_data))

    print(f"{'Barcode':<{longest_barcode}} | "
          f"{'Food':<{longest_food}} | "
          f"{'Expiry Date':<{longest_expiry_date}} | "
          f"{'Ecoscore Grade':<{longest_ecoscore_grade}} | "
          f"{'Ecoscore Score':<{longest_ecoscore_score}} | "
          f"Keywords")

    for waste in waste_data:
        expiry_date_str = waste[2]
        expiry_date_obj = datetime.datetime.strptime(expiry_date_str,
                                                     "%Y-%m-%d %H:%M:%S")
        formatted_expiry_date = expiry_date_obj.strftime("%d.%m.%Y")

        print(
            f"{str(waste[0]):<{longest_barcode}} | "
            f"{waste[1]:<{longest_food}} | "
            f"{formatted_expiry_date:<{longest_expiry_date}} | "
            f"{waste[3]:<{longest_ecoscore_grade}} | "
            f"{str(waste[4]):<{longest_ecoscore_score}} | "
            f"{waste[5]}")
