def get_animals(file_name, data):
    for entry in data:
        if entry["file_name"] == file_name:
            return entry["animals"]
    return []

def compare_animal_names(input_string, animal1, animal2):
    if animal1 in input_string and animal2 in input_string:
        return("all equal")
    elif animal1 in input_string or animal2 in input_string:
        return("one animal match")
    else:
        return("no match")