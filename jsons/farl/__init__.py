import json
import os

root = os.path.dirname(os.path.realpath(__file__))

json_files_path = '{}/{}'.format(root, 'countries.json')

def load_json_data(file_name):
    file_path = '{}/{}'.format(root, file_name)
    with open(file_path) as json_file:
        json_data = json.load(json_file)

    return json_data

def get_countries_list(continent, dict_of_data):
    list_of_countries = list(dict_of_data[continent].keys())

    #return list(dict_of_data[continent].keys())

    return list_of_countries

def get_cities_list(continent, country, dict_of_data):
    list_of_cities = list(dict_of_data[continent][country])

    return list_of_cities

def get_aeroports_list(continent, country, city, dict_of_data):
    aeroports_list = dict_of_data[continent][country][city]

    return aeroports_list


class CountriesAndCities:
    @staticmethod
    def as_json():
        with open(json_files_path) as jsonFile:
            data = json.load(jsonFile)

        return data


        # countries = data.keys()
        # for country in countries:
        #     code = data[country]["Indicatif"]
        #     currency = data[country]["Monnaie"]
        #     cities = data[country]["Villes"].keys()
        #     print(cities)
        #     print('============================')
        # values = data.values()
    
    #dict_of_data = load_json_data('countries.json')

    #print(countries)
#
#countries = list(dict_of_data.keys())

#print(countries)

#countries = []
#for continent in continents:
#    _countries = get_countries_list(continent, dict_of_data)
#    countries.extend(_countries)
    
#countries = sorted(countries)
#print(countries)




