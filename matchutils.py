
def get_all_animals(data):
    return next((item["animal_list"] for item in data if "animal_list" in item), None)

# def get_animals_bypath(file_name, data):
#     for entry in data:
#         if entry["file_name"] == file_name:
#                 return entry["animals"]
#     return []

def get_animals_bypath(file_name, data):
    for entry in data:
        if entry.get("file_name") == file_name:
            return entry.get("animals", [])
    return []

def compare_animal_names(input_string, animal1, animal2):
    input_string = input_string.lower()
    if animal1 in input_string and animal2 in input_string:
        return("all equal")
    elif animal1 in input_string or animal2 in input_string:
        return("one animal match")
    else:
        return("no match")

        