import json
import os

def load_data_from_json(filename):
    with open(filename, 'r') as file:
        data = json.load(file)
    return data

def count_passed_levels(data):
    count = 0
    for key, value in data.items():
        if value['Passed']:
            count += 1
    return count

def count_number_of_levels():
    directory, extension = "../complevels", ".lvl"
    count = 0
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(extension):
                count += 1
    return count


if __name__ == "__main__":
    data = load_data_from_json('tests_cdij.json')
    number_of_files = count_number_of_levels()
    passed_count = count_passed_levels(data)
    print(f"Number of levels passed: {passed_count} of out {number_of_files}")
