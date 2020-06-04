import re


def validate_hexadecimal_color_code(color_code):
    """
    Checking if the provided hexadecimal color code is valid or not

    :param color_code:
    :return boolean:
    """
    return True if re.search(r'^#(?:[0-9a-fA-F]{3}){1,2}$', color_code) else False
