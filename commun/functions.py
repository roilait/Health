from app import models
from datetime import date
import random
import pandas as pd


# Get country name form country id
def country_name(country_id):
    country, created = models.Countries.objects.get_or_create(id=country_id)

    return country.name


# Get city name form city id
def city_name(city_id):
    city, created = models.Cities.objects.get_or_create(id=city_id)

    return city.name


# Get aeroprt name form aeroport id
def aeroport_name(aeroport_id):
    aeroport, created = models.Aeroports.objects.get_or_create(id=aeroport_id)

    return aeroport.name


# Get cities linked to input country
def cities_linked_to_this_country(county):
    country, created = models.Countries.objects.get_or_create(name=county)
    country_id = country.id
    country_cities = models.Cities.objects.filter(
        country_id=country_id).values_list('name', flat=True)

    return list(country_cities)


# This function return the tab data as a dict, with fields as keys
# def db_model_to_dict(model_name):
#     model_as_list = list(model_name.values())
#     fields = model_as_list[0].keys()
#     fields_list = [field for field in fields]
#     tab_list = list(model_name.values())
#
#     dict_of_instance = {
#         field: [obj[field] for obj in tab_list] for field in fields_list
#     }
#
#     return dict_of_instance


# def dict_of_countries_instance(key=None):
#     countries_instance = models.Countries.objects.all()
#     dict_of_countries = db_model_to_dict(countries_instance)
#     if key is not None:
#         dict_of_countries = dict_of_countries[key]
#
#     return dict_of_countries


# def dict_of_cities_instance(key=None):
#     cities_instance = models.Cities.objects.all()
#     dict_of_cities = db_model_to_dict(cities_instance)
#     if key is not None:
#         dict_of_cities = dict_of_cities[key]
#
#     return dict_of_cities


# def db_model_as_dict(model):
#     countries_list = None
#     # if models.Countries.objects.all().exists():
#     obj = models.Countries.objects.all()
#     dict_of_obj = db_model_to_dict(obj)
#     countries_list = dict_of_obj['name']
#     countries_list = sorted(countries_list)
#
#     return countries_list


def get_post_detail(post_id):
    post_id = int(post_id)
    detail, created = models.Post.objects.get_or_create(id=post_id)

    return detail


def dict_of_user_profile_and_fields(user, profile):
    info_user = dict(zip(
        ['email', 'full_name', 'date_joined', 'updated_at'],
        [user.email, user.full_name, user.date_joined, user.updated_at]
    ))

    info_profile = dict(zip(
        ['gender', 'phone_number', 'language', 'country',
         'city', 'account_type', 'img_name'],
        [profile.gender, profile.phone_number, profile.language, profile.country,
         profile.city, profile.account_type, profile.image]
    ))
    # Merging the 2 dictionaries
    result = {**info_user, **info_profile}

    return result


def is_date_valid(date_as_string):
    today = date.today()
    y, m, d = str(date_as_string).split('-')
    cy, cm, cd = str(today).split('-')
    # Proposed day checker
    save_now = False
    if int(y) > int(cy):
        save_now = True
    elif int(y) == int(cy):
        if int(m) > int(cm):
            save_now = True
        else:
            if int(m) == int(cm):
                if int(d) >= int(cd):
                    save_now = True


def departure_date_checker(depart_date):
    today = date.today()
    y, m, d = str(depart_date).split('-')
    cy, cm, cd = str(today).split('-')
    # Proposed day checker
    save_now = False
    if int(y) > int(cy):
        save_now = True
    elif int(y) == int(cy):
        if int(m) > int(cm):
            save_now = True
        else:
            if int(m) == int(cm):
                if int(d) >= int(cd):
                    save_now = True

    return save_now


def get_all_posts(n=None, state=None):
    post, created = models.Posts.objects.get_or_create(id=1)

   # df_posts = (pd.DataFrame(list(post)))
    #print('==============+=============')
   # print(pd.DataFrame(list(post_set)))

    post_set = None
    if not created:
        if n is None:
            if state is None:
                post_set = models.Post.objects.all().values()
            else:
                post_set = models.Post.objects.filter(post_state=state).values()
        else:
            if state is None:
                post_set = models.Post.objects.all().values()
            else:
                post_set = models.Post.objects.filter(post_state=state).values()
    print('==============+=============')
    print(pd.DataFrame(list(post_set)))
    return post_set


def generate_post_code(poster_id):
    code = ''.join(
        random.choices(
            list('ABCDEFGHIJKLMNPQRSTUVWXYZ'), k=5
        )
    )
    trip_code = ''.join([str(poster_id), code])

    return trip_code


