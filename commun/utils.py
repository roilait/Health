from commun import variabless, threads, emails
from django.core.exceptions import ObjectDoesNotExist
################################################3
# Ajouter from django.core.cache import cache
#             if cache.get(post_id):
################################################
import random
from app import models
import pandas as pd
from datetime import date
import re, threading
from io import BytesIO
from django.core.files import File
from django.contrib import messages
from PIL import Image
# from django.contrib import messages
# from django.core.exceptions import ObjectDoesNotExist
from datetime import *
import jsons


data = jsons.CountriesAndCities.as_json()
# countries = data.keys()
# for country in countries:
#     code = data[country]["Indicatif"]
#     currency = data[country]["Monnaie"]
#     cities = data[country]["Villes"].keys()
#     print(cities)
#     print('============================')
# values = data.values()


class AddMember:
    def __init__(self, email, full_name, password):
        self.user = models.Users.objects.create_user(
            email.strip(),
            " ".join(full_name.strip().split()),
            password.strip(),
            is_active=False
        )

    def user(self):
        return self.user


class MemberProfileData:
    def __init__(self, user_id, context, forms):
        # Get the user profile data
        user_profile = QuerySet.using_get(
            model_name=models.Profiles, user_id=user_id
        )
        context['profile'] = user_profile

        edit_form = forms.RegisterForm(
            instance=user_profile
        )
        context['edit_form'] = edit_form
        # Add user's propositions and reservations as dataframe to context
        MemberPosts(user_id, context)
        MemberReservations(user_id, context)


class Random:
    @staticmethod
    def code(length):
        params = 'A1BC2DE3FGH4IJ5KL6MNO7PQ8R9STUV0WXYZ'
        random_code = ''.join(random.choices(list(params), k=length))

        return random_code


class CurrentPosts:
    @staticmethod
    def as_dataframe(n_rows=10):
        state = variabless.current
        last_n_rows = models.Posts.objects.filter(**{'post_state': state}).order_by('-id')[: n_rows]
        df_n_current_posts = pd.DataFrame(list(last_n_rows.values()))
        if not df_n_current_posts.empty:
            # Rename some dataframe columns
            df_n_current_posts = GetPostsData.as_dataframe(
                df_n_current_posts
            )
            # Adding day, month and year columns to dataframe
            DepartureDateInProgress(df_n_current_posts)
            # Get the posts in date
            df_n_current_posts = df_n_current_posts[
                (df_n_current_posts['departure_date_in_progress'] == True) &
                (df_n_current_posts['number_of_kg'] != 0)
            ]
            # Separate the first and last member's name
            names = df_n_current_posts['p_full_name'].tolist()
            names = [''.join([name.split(" ")[0], ' ', list(name.split(" ")[1])[0]]) for name in names]
            df_n_current_posts['publish_by'] = names
            # Sorting the current posts dataframe
            df_n_current_posts.sort_values(['departure_years', 'departure_months', 'departure_days'],  inplace=True)

        return df_n_current_posts


class SortingDataframe:
    def __init__(self, df, *columns):
        # Sorting by columns "Country" and then "Continent"
        df.sort_values(by=columns)


class DepartureDateInProgress:
    def __init__(self, dataframe):
        if not dataframe.empty:
            # Get the current date
            current_day, current_month, current_year = date.today().strftime("%d-%m-%Y").split('-')
            # Lists initialisation
            departure_days, departure_months, departure_years = [], [], []
            # Update the list
            for departure_date in dataframe['departure_date'].tolist():
                day, month, year = departure_date.split('-')
                month_index = int(variabless.mois.index(month)) + 1
                departure_days.append((int(day)))
                departure_months.append(int(month_index))
                departure_years.append(int(year))

            dataframe['departure_days'] = departure_days
            dataframe['departure_months'] = departure_months
            dataframe['departure_years'] = departure_years
            # Initialize the departure_date_in_progress column to False
            dataframe['departure_date_in_progress'] = [False for i in range(len(departure_years))]

            condition_1 = (dataframe['departure_years'] > int(current_year))
            condition_2 = (
                    (dataframe['departure_years'] == int(current_year)) &
                    (dataframe['departure_months'] > int(current_month))
            )
            condition_3 = (
                    (dataframe['departure_years'] == int(current_year)) &
                    (dataframe['departure_months'] == int(current_month)) &
                    (dataframe['departure_days'] >= int(current_day))
            )

            dataframe.loc[(condition_1 | condition_2 | condition_3), 'departure_date_in_progress'] = True


class MemberPosts:
    def __init__(self, user_id, context):
        context['user'] = QuerySet.using_get(
            model_name=models.Users, **{'id': user_id}
        )
        # Get the posts proposed by this member
        query_of_posts = QuerySet.using_filter(
            models.Posts, **{'poster_id': user_id}
        )
        # Adding same change to df_query_set dataframe
        df_user_posts = GetPostsData.as_dataframe(
            query_of_posts['query_as_dataframe']
        )
        DepartureDateInProgress(df_user_posts)
        # Find the reservers on the posts
        if not df_user_posts.empty:
            # Get user's id posts from dataframe as a list
            user_posts_id = df_user_posts['post_id'].tolist()
            # Get the reservations query made on this user post
            query_of_reservations = QuerySet.using_filter(
                models.Reservations, **{'post_id__in': user_posts_id}
            )
            # Get the reservations made on this user post as dataframe
            # context['df_reservers'] = pd.DataFrame()
            df_query_of_reservations = query_of_reservations['query_as_dataframe']
            if not df_query_of_reservations.empty:
                # Adding same change to df_query_set dataframe
                df_reserved = GetReservations.as_dataframe(
                    df_query_of_reservations
                )
                # Add reservations dataframe to the context
                context['df_reservers_in_progress'] = df_reserved[df_reserved['reserv_state'] == 'In progress']
                context['df_reservers_completed'] = df_reserved[df_reserved['reserv_state'] == 'Completed']
                context['df_reservers_canceled'] = df_reserved[df_reserved['reserv_state'] == 'Canceled']
                # Get the number of reservations did on each post
                df = df_reserved
                df_user_posts['nbr_current_res'] = [
                    df[(df['post_id'] == post_id) & (df['reserv_state'] == 'In progress')].shape[0] for post_id in user_posts_id
                ]
                df_user_posts['nbr_completed_res'] = [
                    df[(df['post_id'] == post_id) & (df['reserv_state'] == 'Completed')].shape[0] for post_id in user_posts_id
                ]
                df_user_posts['nbr_canceled_res'] = [
                    df[(df['post_id'] == post_id) & (df['reserv_state'] == 'Canceled')].shape[0] for post_id in user_posts_id
                ]
        # Get the posts with post_state In progress
        df_member_current_posts = MemberCurrentPosts.as_dataframe(
            df_user_posts
        )

        # Now update the context
        context['df_member_current_posts'] = df_member_current_posts
        context['df_member_completed_posts'] = MemberCompletedPosts.as_dataframe(df_user_posts)
        context['df_member_canceled_posts'] = MemberCanceledPosts.as_dataframe(df_user_posts)


class GetPostsData:
    @staticmethod
    def as_dataframe(dataframe):
        # Get query as dataframe
        df_post = dataframe
        # Rename some dataframe fields as
        df_post.rename(columns={
            'id': 'post_id',
            'depart_country_id': 'depart_country',
            'depart_city_id': 'depart_city',
            'arrival_country_id': 'arrival_country',
            'arrival_city_id': 'arrival_city'
        }, inplace=True)

        if not df_post.empty:
            df_post.sort_values(
                by=['publish_date'], inplace=True, ascending=True
            )
            # Get the departure information
            cities_id = df_post['depart_city'].tolist()
            cities_id.extend(df_post['arrival_city'].tolist())
            unique_cities_id = (list(set(cities_id)))
            # Change the cities' id to cities name
            for city_id in unique_cities_id:
                city_name = City.name(
                    city_id
                )
                df_post.loc[(df_post['depart_city'] == city_id), 'depart_city'] = city_name
                df_post.loc[(df_post['arrival_city'] == city_id), 'arrival_city'] = city_name
            # Get the departure information
            countries_id = df_post['depart_country'].tolist()
            countries_id.extend(df_post['arrival_country'].tolist())
            unique_countries_id = (list(set(countries_id)))

            # Change the countries' id to cities name
            for country_id in unique_countries_id:
                country_name = Country.name(
                    country_id=country_id
                )
                df_post.loc[(df_post['depart_country'] == country_id), 'depart_country'] = country_name
                df_post.loc[(df_post['arrival_country'] == country_id), 'arrival_country'] = country_name
            # Replace departure_date column values by adding month name
            old_format = [str(d) for d in df_post["departure_date"].tolist()]
            df_post.drop(["departure_date"], inplace=True, axis=1)
            df_post["departure_date"] = [
                MonthsName.departure_date(str(d)) for d in old_format
            ]
            # Adding the poster information to dataframe
            posters_id = df_post['poster_id'].unique()
            for poster_id in posters_id:
                user = QuerySet.using_get(
                    model_name=models.Users, **{'id': poster_id}
                )
                profile = QuerySet.using_get(
                    model_name=models.Profiles, **{'user_id': poster_id}
                )
                # col = "poster_id"
                keys = [
                    'p_full_name', 'p_notes', 'p_accept_rate', 'p_cancel_rate',
                    'p_profile_img', 'p_email', 'p_phone_number', 'p_language'
                ]
                values = [
                    user.full_name, profile.notes, profile.accept_rate, profile.cancel_rate,
                    profile.image.url, user.email, profile.phone_number, profile.language
                ]
                # Convert the keys and values list to a dictionary
                r_dict = dict(zip(keys, values))
                for key, value in r_dict.items():
                    df_post.loc[(df_post.poster_id == poster_id), key] = value

            df_post.columns = df_post.columns.tolist()

        return df_post


class PostDetail:
    @staticmethod
    def as_dataframe(post_id):
        # This function return a dictionary with df_query_set & query_set as key
        query_set = QuerySet.using_filter(
            models.Posts, **{'id': post_id}
        )

        df_post_detail = GetPostsData.as_dataframe(
            query_set['query_as_dataframe']
        )

        return df_post_detail


class MemberCurrentPosts:
    @staticmethod
    def as_dataframe(posts_as_dataframe):
        state = variabless.current
        df_current_member_posts = posts_as_dataframe[
            posts_as_dataframe['post_state'] == state
        ]

        return df_current_member_posts


class MemberCompletedPosts:
    @staticmethod
    def as_dataframe(posts_as_dataframe):
        state = variabless.completed
        df_completed_member_posts = posts_as_dataframe[
            posts_as_dataframe['post_state'] == state
        ]

        return df_completed_member_posts


class MemberCanceledPosts:
    @staticmethod
    def as_dataframe(posts_as_dataframe):
        state = variabless.canceled
        df_canceled_member_posts = posts_as_dataframe[
            posts_as_dataframe['post_state'] == state
        ]

        return df_canceled_member_posts


class MemberReservations:
    def __init__(self, user_id, context):
        # Now get the reservation for this member as dataframe
        dic_of_reservation_query = QuerySet.using_filter(
            models.Reservations, **{'reserver_id': user_id}
        )
        # Get the member reservations as dataframe by adding same changes to columns
        df_query_set = dic_of_reservation_query['query_as_dataframe']
        # Changing same columns name
        df_member_reservation = GetReservations.as_dataframe(
            df_query_set
        )
        # Check if the member has reservation(s)
        if not df_member_reservation.empty:
            posts_id = df_member_reservation['post_id'].values
            # Get the post query set that this member reserved on
            dict_of_post_query = QuerySet.using_filter(
                models.Posts, list_of_id=posts_id, **{}
            )
            # Adding same change to df_query_set dataframe
            df_post_query = GetPostsData.as_dataframe(
                dict_of_post_query['query_as_dataframe']
            )
            # This is the conditions

            DepartureDateInProgress(df_post_query)
            # The posts data as dataframe
            context['df_posts_reserved_on'] = df_post_query  # df_posts_reserved_on
            # Now update the context
            # context['df_member_current_posts'] = df_member_current_posts
        # df_member_current_reservations = MemberCurrentReservations.as_dataframe(df_member_reservation)
        # df_member_current_reservations[]
        context['df_member_current_reservations'] = MemberCurrentReservations.as_dataframe(df_member_reservation)
        context['df_member_completed_reservations'] = MemberCompletedReservations.as_dataframe(df_member_reservation)
        context['df_member_canceled_reservations'] = MemberCanceledReservations.as_dataframe(df_member_reservation)


class GetReservations:
    @staticmethod
    def as_dataframe(df_reservation):
        if not df_reservation.empty:
            reserver_id_list = df_reservation['reserver_id'].tolist()
            for reserver_id in reserver_id_list:
                # Get user data
                user = QuerySet.using_get(
                    models.Users, **{'id': reserver_id}
                )
                # Get user profile data
                profile = QuerySet.using_get(
                    models.Profiles, **{'user_id': reserver_id}
                )
                # Creation a dictionary from two lists
                keys = [
                    'r_full_name', 'r_notes', 'r_accept_rate', 'r_cancel_rate',
                    'r_profile_img', 'r_email', 'r_phone_number', 'r_language'
                ]
                values = [
                    user.full_name, profile.notes, profile.accept_rate, profile.cancel_rate,
                    profile.image.url, user.email, profile.phone_number, profile.language
                ]

                dicts = dict(zip(keys, values))
                #
                for key, value in dicts.items():
                    df_reservation.loc[(df_reservation['reserver_id'] == reserver_id), key] = value

        return df_reservation


class MemberCurrentReservations:
    @staticmethod
    def as_dataframe(reservations_as_dataframe):
        state = variabless.current
        df_current_member_reservations = reservations_as_dataframe[
            reservations_as_dataframe['reserv_state'] == state
        ]

        return df_current_member_reservations


class MemberCompletedReservations:
    @staticmethod
    def as_dataframe(reservations_as_dataframe):
        state = variabless.completed
        df_completed_member_reservations = reservations_as_dataframe[
            reservations_as_dataframe['reserv_state'] == state
        ]

        return df_completed_member_reservations


class MemberCanceledReservations:
    @staticmethod
    def as_dataframe(reservations_as_dataframe):
        state = variabless.canceled
        df_canceled_member_reservations = reservations_as_dataframe[
            reservations_as_dataframe['reserv_state'] == state
        ]

        return df_canceled_member_reservations


# class User:
#     @staticmethod
#     def email_host_password():
#         return '@Amadou2009'


class FromMonthName:
    @staticmethod
    def get_month_number(month_name):
        month_as_number = variabless.mois.index(month_name) + 1

        return month_as_number


class MonthsName:
    @staticmethod
    def departure_date(_date, language=None):
        var = _date.split('-')
        year, month_number, day = int(var[0]), int(var[1]), int(var[2])
        month_index = month_number - 1

        month_name = variabless.mois[month_index]

        return '{}-{}-{}'.format(day, month_name, year)


class Departure:
    @staticmethod
    def date(proposed_date):
        var = proposed_date.split('-')
        year, month_number, day = int(var[0]), int(var[1]), int(var[2])

        month_name = variabless.mois[month_number - 1]

        return '{}-{}-{}'.format(day, month_name, year)


class Countries:
    @staticmethod
    def name(name=False):
        try:
            countries = models.Countries.objects.all()
        except models.Countries.DoesNotExist:
            countries = None

        return countries


class Country:
    @staticmethod
    def name(country_id=None, country_name=None):
        try:
            if country_id is not None:
                country = models.Countries.objects.get(
                    id=country_id
                )
            elif country_name is not None:
                country = models.Countries.objects.get(
                    name=country_name
                )
            else:
                country = None
        except models.Countries.DoesNotExist:
            country = None

        return country


class Cities:
    @staticmethod
    def name(country_id):
        try:
            cities = models.Cities.objects.filter(
                country_id=country_id
            )
        except models.Cities.DoesNotExist:
            cities = None

        return cities


class City:
    @staticmethod
    def name(city_id):
        try:
            city = models.Cities.objects.get(
                id=city_id
            )
        except models.Cities.DoesNotExist:
            city = None

        return city


class CityAndCountry:
    @staticmethod
    def names(city_id, country_id):
        city_name = City.name(city_id)
        country_name = Country.name(country_id)

        city_and_country_name = '{}, {}'.format(
            city_name, country_name
        )

        return city_and_country_name


class ExistingReservationChecker:
    def __init__(self, post_id, reserver_id, checker=False):
        query = QuerySet.using_get(
            models.Reservations,
            **{
                'post_id': post_id,
                'reserver_id': reserver_id
            }
        )
        if query is not None:
            checker = True


class Generator:
    @staticmethod
    def post_code(user_id):
        random_code = Random.code(length=4)
        selected_code = ''.join([str(user_id), random_code])

        return selected_code


class QuerySet:
    @staticmethod
    def using_filter(model_name, get_n_rows=None, list_of_id=None, **kwargs):
        # Get the column names as a list
        column_names = [field.name for field in model_name._meta.get_fields()]
        try:
            if list_of_id is not None:
                # Get the query set
                query_set = model_name.objects.filter(
                    id__in=list_of_id
                )
            else:
                query_set = model_name.objects.filter(
                    **kwargs
                )
        except model_name.DoesNotExist:
            query_set = None

        # Check if the query exist
        if query_set.exists():
            if list_of_id is not None:
                df_query_set = pd.DataFrame(
                    list(query_set.values())
                )
            elif get_n_rows is not None:
                # Return just the first n rows
                n = int(get_n_rows)
                df_query_set = pd.DataFrame(list(query_set.values())).head(n)
            else:
                df_query_set = pd.DataFrame(
                    list(query_set.values())
                )
        else:
            df_query_set = pd.DataFrame(columns=column_names)

        results_as_dict = {
            'query_set': query_set,
            'query_as_dataframe': df_query_set
        }

        return results_as_dict

    @staticmethod
    def using_get(model_name, **kwargs):
        try:
            query = model_name.objects.get(
                **kwargs
            )
        except model_name.DoesNotExist:
            query = None

        return query


class MemberComments:
    @staticmethod
    def as_dataframe(post_id):
        pass
        # kwargs = {'id': post_id}
        '''
        df_post_comments = ServiceData.member_posts_as_dataframe(
            **{
                'id': post_id
            }
        )
        '''
        # Dataframe of the comment leave for the poster
        # poster_id = df_post_detail["poster_id"]
        # comments = models.Comments.objects.filter(recepter_id=poster_id)
        # df_comment = pd.DataFrame(list(comments.values()))

        # return df_post_comments


class ResizeImage:
    @staticmethod
    def make_thumbnail(image_name, size=(100, 100)):
        """ Makes thumbnails of given size from given image """
        ext = str(image_name).split('.')[-1]
        im = Image.open(image_name)
        im.convert('RGB')                            # convert mode
        im.thumbnail(size)                           # resize image
        thumb_io = BytesIO()                         # create a BytesIO object
        im.save(thumb_io, ext, quality=85)           # save image to BytesIO object
        thumbnail = File(thumb_io, name=image_name)  # create a django friendly File object

        return thumbnail


class DateChecker:
    def __init__(self):
        today = date.today()  # Get current date
        self.year, self.month, self.day = str(today).split('-')  # Split the current date

    def departure_date_checker(self, proposed_date):
        year, month, day = str(proposed_date).split('-')  # Split the proposed date
        current_year = self.year
        current_month = self.month
        current_day = self.day
        #
        date_is_valid = False
        if int(year) > int(current_year):
            date_is_valid = True
        elif int(year) == int(current_year):
            if int(month) > int(current_month):
                date_is_valid = True
            else:
                if int(month) == int(current_month):
                    if int(day) >= int(current_day):
                        date_is_valid = True

        return date_is_valid

    def proposed_date_checker(self, list_of_date):
        list_of_booleen = []
        for proposed_date in list_of_date:
            day, month, year = str(proposed_date[0]).split('-')  # Split the proposed date
            # Convert month name to month number
            month = FromMonthName.get_month_number(
                month
            )
            current_year = int(self.year)
            current_month = int(self.month)
            current_day = int(self.day)
            #
            state_in_past = True
            if current_year <= int(year):
                if current_year == int(year):
                    if current_month <= int(month):
                        if current_month == int(month):
                            if current_day < int(day) + 1:
                                state_in_past = False

            list_of_booleen.append(state_in_past)

        return list_of_booleen


class UpdateProfile:
    def __init__(self, request, user_id, context, **kwargs):
        self.update_now = True
        for key in kwargs.keys():
            if not bool(str(kwargs.get(key)).strip()):
                self.update_now = False
                break
        # Adding data to database
        if self.update_now:
            phone = kwargs['phone_number']
            # International phone number verification
            phone_match = re.compile(r'([0]{2}|\+)([0-9]{8,16})').match(phone)
            if phone_match is not None:
                # Update the profile
                threads.UpdateModel(
                    models.Profiles, user_id=user_id, **kwargs
                )
                # Get the updater profile
                profile = QuerySet.using_get(
                    model_name=models.Profiles, **{'user_id': user_id}
                )
                # Profile updated successfully
                context['profile'] = profile
                request.session['profile_is_updated'] = True
            else:
                messages.error(
                    request, 'Ind. + numéro, exemple: +222345678'
                )
        else:
            messages.error(
                request, 'Tous les champs sont obligatoires.'
            )


class UserAlerts:
    def __init__(self, user_id, context):
        alerts = QuerySet.using_filter(
            models.AlertMe,
            **{
                'member_id': user_id,
                'alert_state': 'In progress'
            }
        )
        df_alerts = alerts['query_as_dataframe']

        df_alerts.rename(columns={
            'depart_country_id': 'depart_country',
            'depart_city_id': 'depart_city',
            'arrival_country_id': 'arrival_country',
            'arrival_city_id': 'arrival_city'
        }, inplace=True)

        if not df_alerts.empty:
            df_alerts.sort_values(
                by=['publish_date'], inplace=True, ascending=True
            )
            # Get the departure information
            cities_id = df_alerts['depart_city'].tolist()
            cities_id.extend(df_alerts['arrival_city'].tolist())
            unique_cities_id = (list(set(cities_id)))
            # Change the cities' id to cities name
            for city_id in unique_cities_id:
                city_name = City.name(
                    city_id
                )

                df_alerts.loc[(df_alerts['depart_city'] == city_id), 'depart_city'] = city_name
                df_alerts.loc[(df_alerts['arrival_city'] == city_id), 'arrival_city'] = city_name
            # Get the departure information
            countries_id = df_alerts['depart_country'].tolist()
            countries_id.extend(df_alerts['arrival_country'].tolist())
            unique_countries_id = (list(set(countries_id)))
            # Change the countries' id to cities name
            for country_id in unique_countries_id:
                country_name = Country.name(
                    country_id=country_id
                )
                df_alerts.loc[(df_alerts['depart_country'] == country_id), 'depart_country'] = country_name
                df_alerts.loc[(df_alerts['arrival_country'] == country_id), 'arrival_country'] = country_name
            # Replace departure_date column values by adding month name
            old_format = [str(d) for d in df_alerts["departure_date"].tolist()]
            df_alerts.drop(["departure_date"], inplace=True, axis=1)
            df_alerts["departure_date"] = [
                MonthsName.departure_date(str(d)) for d in old_format
            ]
            # Adding the poster information to dataframe
            DepartureDateInProgress(df_alerts)
        else:
            df_alerts = pd.DataFrame()

        context['df_alerts'] = df_alerts
