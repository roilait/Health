import json, random


def load_json_file(file_path):
    # First we load existing data into a dict.
    with open(file_path, 'r+') as file:
        # First we load existing data into a dict.
        file_data = json.load(file)

    return file_data


class AccessToJsonFile:
    @staticmethod
    def update_json_file(json_object, filename='jsons/farl/patients.json'):
        a_file = open(filename, "w")
        json.dump(json_object, a_file)
        a_file.close()

    @staticmethod
    def get_medicine_names(filename='jsons/farl/ordonnance.json'):
        with open(filename, 'r+') as file:
            # First we load existing data into a dict.
            file_data = json.load(file)

            return file_data

    @staticmethod
    def add_new_patient(dicts_of_new_data, filename='jsons/farl/patients.json'):
        with open(filename, 'r+') as file:
            # First we load existing data into a dict.
            file_data = json.load(file)
            # Create a new pin for this new user
            new_pin = "_".join(["PIN", str(random.randrange(100, 10000, 2))])
            while new_pin in file_data["Patients"].keys():
                new_pin = "_".join(["PIN", str(random.randrange(100, 10000, 2))])
            # Join new_data with file_data inside emp_details

            file_data["Patients"][new_pin] = dicts_of_new_data
            # Sets file's current position at offset.
            file.seek(0)
            # convert back to json.
            json.dump(file_data, file, indent=4)

            return new_pin

    @staticmethod
    def find_a_patient(pin):
        filename = 'jsons/farl/patients.json'
        with open(filename, 'r+') as file:
            # First we load existing data into a dict.
            file_data = json.load(file)

        patient_pin = "_".join(["PIN", str(pin)])
        # Initialize the dictionary
        patient_data = {}
        if patient_pin in file_data["Patients"].keys():
            patient_data = file_data["Patients"][patient_pin]

        return patient_data, file_data

