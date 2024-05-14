def find_key_by_value(dictionary: dict, value):
    for key, val in dictionary.items():
        if val == value:
            return key
    return None 