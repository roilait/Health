from django.shortcuts import render, redirect
# from django.shortcuts import get_object_or_404
# web: gunicorn gp_project.wsgi --preload --log-file -
from django.contrib import messages
from django.contrib import auth
import os
import pandas as pd
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site
from django.views import View

from . import forms
from . import models
from commun import (
    emails, tokens, utils, variabless, threads
)


from commun import html_files_access as template

from jsons import loadJsonData

password_lenght = 5


class RegisterView(View):  # Registration class for a new member
    def __init__(self):
        # This is the class context
        self.context = {
            'form': forms.RegisterForm(),           # Registration form
            'registered': False,                    # The registration is not finished yet, initiation
            'df_current_n_posts': pd.DataFrame() # Get and display the 10 last posts
        }

    def get(self, request):
        # Go to the registration form for a new member,
        return render(
            request, template.register_html, self.context
        )

    def post(self, request):
        # Get the completed form after submission
        form = forms.RegisterForm(request.POST or None)
        # Get the email that will use to check if the member exist in our db
        email = request.POST['email'].strip()
        # Check if the email exist in our db
        if models.Users.objects.filter(email=email).exists():
            messages.error(
                request, "Hops, ce email existe déjà!"
            )
        else:
            if form.is_valid():
                # Clean the fields data
                full_name = form.cleaned_data.get('full_name')
                pwd1 = form.cleaned_data.get('password1')
                pwd2 = form.cleaned_data.get('password2')
                # check if the 2 password are same
                if pwd1 and pwd2 and pwd1 != pwd2:
                    messages.error(
                        request, "Hops, les mots de passe ne sont pas identiques!"
                    )
                else:
                    # The password length should be > 5
                    if len(list(pwd1)) < password_lenght:
                        messages.error(request, 'Hops, le mot de passe est très court!')
                    else:
                        self.context['registered'] = True
                        self.context['email'] = email
                        # Adding a new member by using threading
                        # Add the new member to user_table
                        user = models.Users.objects.create_user(
                            email.strip(),
                            " ".join(full_name.strip().split()),
                            pwd1.strip(),
                            is_active=False
                        )
                        # Sending activation email to new member
                        #
                        domain_name = get_current_site(request).domain
                        emails.SendActivationMail(
                            user, domain_name
                        )

            else:
                messages.error(
                    request, "Hops, formulaire non valide!"
                )

        return render(
            request, template.register_html, self.context
        )


class LoginView(View):
    def __init__(self):
        self.context = {
            'login_form': forms.LoginForm(),
            'profile_form': forms.UserProfileForm(),
            'df_current_n_posts': pd.DataFrame()
        }

    def get(self, request):

        return render(
            request, template.login_html, self.context
        )

    def post(self, request):
        # First displayed page
        page = 'login_page'
        if forms.LoginForm(request.POST or None).is_valid():
            # ===== Authenticate the user inputs ======
            user = auth.authenticate(
                username=request.POST['email'].strip(),
                password=request.POST['password'].strip()
            )
            if user is None:  # If the user does not exist
                messages.error(
                    request, "Email et/ou mot de passe incorrect!"
                )
            else:
                if not user.active:  # If the user account is not active
                    messages.error(
                        request, "Vous avez pas encore activé votre compte!"
                    )
                else:  # If the user account is active
                    auth.login(request, user)
                    # Get the user join date as date/month/year
                    date = str(user.date_joined).split(' ')[0].split('-')
                    join_date = '{}/{}/{}'.format(date[2], date[1], date[0])
                    # Store this data in a session
                    request.session['user_id'] = user.id
                    request.session['date_joined'] = join_date
                    request.session['logged_in'] = 'user'
                    # ==== Get the user profile data ====
                    user_profile = utils.QuerySet.using_get(
                        model_name=models.Profiles, user_id=user.id
                    )
                    self.context['profile'] = user_profile
                    # Get the user alerts
                    utils.UserAlerts(
                        request.session['user_id'], self.context
                    )
                    # Verify if the user profile has been updated or no
                    if not user_profile.is_updated:
                        page = 'profile_page'
                    else:
                        request.session['profile_is_updated'] = user_profile.is_updated
                        self.context['profile_picture'] = user_profile.image.url
                        # This is the member post as dataframe
                        utils.MemberPosts(user.id, self.context)
                        # This is the member reservations as dataframe
                        utils.MemberReservations(user.id, self.context)
                        # If the member is trying to do a reservation before to login
                        if 'post_detail' not in request.session:
                            page = 'profile_page'
                        else:
                            post_id = request.session['post_id']
                            # Get the detail of the post as dataframe
                            self.context['df_post'] = utils.PostDetail.as_dataframe(
                                post_id
                            )
                            self.context['df_comment'] = ''  # obj.get_user_comments(post_id)
                            page = 'post_detail_page'
        else:
            messages.error(
                request, "Le formulaire n'est pas valide!"
            )

        # What page will be display
        if page == 'login_page':
            return render(
                request, template.login_html, self.context
            )
        elif page == 'post_detail_page':
            return render(
                request, template.post_detail_html, self.context
            )
        elif page == 'profile_page':
            alerts = utils.QuerySet.using_filter(
                models.AlertMe, **{'member_id': request.session['user_id']}
            )
            df_alerts = alerts['query_as_dataframe']
            self.context['number_of_alerts'] = df_alerts.shape[0]

            return render(
                request, template.profile_html, self.context
            )


class ResetPasswordView(View):
    def __init__(self):
        self.context = {
            'df_current_n_posts': pd.DataFrame()
        }

    def get(self, request):
        request.session['reset_password'] = False
        self.context['form'] = forms.ForgotPasswordForm()
        #
        return render(
            request, template.reset_pwd_html, self.context
        )

    def post(self, request):
        form = forms.ForgotPasswordForm(request.POST or None)
        # Action allows knowing if the user is changing or updating the pwd
        action = request.POST['action']
        if action == 'get_security_code':  # The  password has been forgotten
            if form.is_valid():
                # Test if the user exist in our database
                user_email = request.POST['email'].strip()
                # Get the user data
                user = utils.QuerySet.using_get(
                    model_name=models.Users, **{'email': user_email}
                )
                if user is None:
                    messages.error(request, "Hops, on ne reconnaît pas ce email!")
                else:
                    request.session['reset_password'] = True
                    request.session['user_id'] = user.id
                    # Choice a random verification code
                    request.session['security_code'] = utils.Random.code(
                        length=4
                    )
                    # Send the security code to the user to change the password
                    verification_code = request.session['security_code']
                    emails.ResetPassword(user.full_name, user_email, verification_code)
            else:
                messages.error(request, 'e-mail non valide!')
        # The action is to reset the password, after submit
        elif action == 'new_password':
            password_1 = request.POST['password1']
            password_2 = request.POST['password2']
            security_code = request.POST['security_code']
            if password_1 != password_2:
                self.context['reset_password'] = True
                messages.error(
                    request, "Les 2 mots de passe ne sont pas identiques!"
                )
            # The password length should be > 5
            elif len(list(password_1)) < password_lenght:
                messages.error(request, 'Hops, le mot de passe est très court!')
            else:
                if security_code != request.session['security_code']:
                    messages.error(
                        request, "Votre code de sécurité n'est pas valide!"
                    )
                else:
                    user_id = request.session['user_id']
                    user = utils.QuerySet.using_get(
                        model_name=models.Users, **{'id': user_id}
                    )
                    # Update and save the password
                    user.set_password(password_1.strip())
                    user.save()
                    messages.success(
                        request, "Votre mot de passe a été mis à jour!"
                    )
                    request.session.modified = True
                    request.session['reset_password'] = False
                    # Delete this sessions
                    del request.session['user_id']
                    del request.session['security_code']

                    context = {
                        'login_form': forms.LoginForm(),
                        'profile_form': forms.UserProfileForm(),
                        'df_current_n_posts': pd.DataFrame()
                    }

                    return render(
                        request, template.login_html, context
                    )

        return render(
            request, template.reset_pwd_html, self.context
        )


class LogoutView(View):
    def __init__(self):
        self.context = {
            'df_current_n_posts': pd.DataFrame()
        }

    def get(self, request):
        auth.logout(request)

        return render(
            request, template.index_html, self.context
        )


class HomeView(View):
    def __init__(self):
        # Get the current post as Dataframe
        self.context = {
            'df_current_n_posts': pd.DataFrame()
        }

    def get(self, request):
        # send_email_task.delay()
        return render(
            request, template.index_html, self.context
        )

    def post(self, request):
        return render(
            request, template.index_html, self.context
        )


class ReservationView(View):
    def __init__(self):
        # self.dict_of_state = variables.Record.state()
        self.context = {
            'reserv_form': forms.LoginForm(),
            'df_current_n_posts': pd.DataFrame(),
            'reservation_confirmed': False
        }

    def get(self, request):
        pass

    def post(self, request):
        post_id = int(request.POST['post_id'])
        poster_id = int(request.POST['poster_id'])
        reserver_id = int(request.session['user_id'])
        kg_reserved = abs(int(request.POST['nbr_of_kg_reserved']))
        currency = request.POST['currency']
        # Get the current post information
        df_post = utils.PostDetail.as_dataframe(
            post_id
        )
        # df_post = utils.ServiceData.get_post_detail(post_id)
        self.context['df_post'] = df_post
        if poster_id == reserver_id:
            messages.error(request, 'Hops, ceci est votre proposition')
        else:
            # Get selected post information
            post = utils.QuerySet.using_get(
                model_name=models.Posts, id=post_id
            )
            if kg_reserved > post.number_of_kg:
                messages.error(
                    request, "Hops, il ne reste que {} kg pour cette annonce.".format(
                        post.number_of_kg
                    )
                )
            else:
                # Update the post kg available after this reservation
                rest_of_kg = post.number_of_kg - kg_reserved
                threads.UpdateModel(
                    models.Posts, row_id=post_id, **{'number_of_kg': rest_of_kg}
                )
                price_of_kg = post.price_of_kg
                post_code = post.post_code
                total_price = kg_reserved * price_of_kg
                # Check if the same reservation exist in the reservations table
                existing_reservation = utils.QuerySet.using_get(
                    models.Reservations,
                    **{
                        'post_id': post_id,
                        'poster_id': poster_id,
                        'reserver_id': reserver_id,
                        'reserv_state': 'In progress'
                    }

                )
                if existing_reservation is not None:
                    # Update the existing reservation
                    threads.UpdateModel(
                        models.Reservations, row_id=existing_reservation.id,
                        **{
                            'nbr_kilos': existing_reservation.nbr_kilos + int(kg_reserved),
                            'total_price': existing_reservation.total_price + int(total_price)
                        }
                    )
                else:
                    # Add new record
                    kwargs = {
                        'post_id': post_id,
                        'poster_id': poster_id,
                        'reserver_id': reserver_id,
                        'nbr_kilos': kg_reserved,
                        'total_price': total_price,
                        'post_code': post_code,
                        'reserv_state': variabless.current,
                        'canceled_by': '',
                        'reserver_comment': ''
                    }
                    threads.CreateNewRecord(
                        models.Reservations, **kwargs
                    )
                # new_reservation = {'currency': currency}
                self.context['reservation_confirmed'] = True
                # Get user's reservation info
                self.context['post_code'] = post_code
                self.context['total_price'] = total_price
                self.context['currency'] = currency
                self.context['kg_reserved'] = kg_reserved
                # Departure city and country names
                self.context['departure'] = utils.CityAndCountry.names(
                    post.depart_city_id, post.depart_country_id
                )
                # Destination city and country names
                self.context['destination'] = utils.CityAndCountry.names(
                    post.arrival_city_id, post.arrival_country_id
                )
                # Get poster information and added it to context
                user = utils.QuerySet.using_get(
                    model_name=models.Users, id=poster_id
                )
                profile = utils.QuerySet.using_get(
                    model_name=models.Profiles, user_id=poster_id
                )
                self.context['poster_full_name'] = user.full_name
                self.context['poster_email'] = user.email
                self.context['poster_phone_number'] = profile.phone_number
                self.context['poster_language'] = profile.language
                self.context['poster_picture'] = profile.image.url
                # Get reserver information and added it to context
                user = utils.QuerySet.using_get(
                    model_name=models.Users, id=reserver_id
                )
                profile = utils.QuerySet.using_get(
                    model_name=models.Profiles, user_id=reserver_id
                )
                self.context['reserver_full_name'] = user.full_name
                self.context['reserver_email'] = user.email
                self.context['reserver_phone_number'] = profile.phone_number
                self.context['reserver_language'] = profile.language
                # Adding months name to the departure date
                departure_date = str(post.departure_date)
                self.context['departure_date'] = utils.Departure.date(
                    departure_date
                )
                # Send email to reserver and poster after the reservation
                # Task here to email poster and reserver
                emails.ToReserverAndPoster(**self.context)

        return render(
            request, template.post_detail_html, self.context
        )


class ChoiceAServiceView(View):
    def __init__(self):
        self.context = {}

    def get(self, request):
        pass

    def post(self, request):
        return render(
            request, template.service_html, self.context
        )


class SelectedServiceView(View):
    form_class = forms.NewPostForm

    def __init__(self):
        # df_current_posts = utils.CurrentPosts.as_dataframe()
        self.context = {
            'df_current_n_posts': pd.DataFrame()
        }

    def get(self, request):
        pass

    def post(self, request):
        # Get the list of countries
        countries = models.Countries.objects.all()
        countries = countries.values_list('name', flat=True)
        self.context['countries'] = sorted(list(countries))
        request.session['selected_service'] = request.POST['service']
        if request.POST['service'] == 'gp':
            self.context['form'] = forms.NewPostForm()  # self.form_class()
        else:
            pass

        return render(
            request, template.new_post_form_html, self.context
        )


class PostDetailView(View):
    def __init__(self):
        self.context = {
            'login_form': forms.LoginForm(),
            'df_current_n_posts': pd.DataFrame(),
            'post_confirmed': False
        }

    # Define get function of this class
    def get(self, request, post_id):
        post_id = int(post_id)
        if 'logged_in' in request.session:
            # Get post detail
            df_post = utils.PostDetail.as_dataframe(
                post_id
            )
            self.context['df_post'] = df_post
            # Adding the proposer full name
            full_names = df_post['p_full_name'].tolist()
            full_names = [''.join([fn.split(" ")[0], ' ', list(fn.split(" ")[1])[0]]) for fn in full_names]
            df_post['publish_by'] = full_names
            # self.context['df_comment'] = df_comment

            return render(
                request, template.post_detail_html, self.context
            )
        else:
            messages.info(
                request, "Hops, vous êtes pas connecté."
            )
            # Store the visited post information for the next step
            request.session['post_id'] = post_id
            request.session['post_detail'] = 'post_detail'

            return render(
                request, template.login_html, self.context
            )

    def post(self, request):
        pass


class UserActions(View):
    @staticmethod
    def manage_bookers(post_id, user_action):
        state = variabless.current
        # Get the canceled post information
        df_post = utils.PostDetail.as_dataframe(
            post_id
        )
        reservations = utils.QuerySet.using_filter(
            models.Reservations,
            **{
                'reserv_state': state,
                'post_id': post_id
            }
        )
        reservations = reservations['query_set']

        for reservation in reservations:
            reserver_id = int(reservation.reserver_id)
            reserver = utils.QuerySet.using_get(
                models.Users, id=reserver_id
            )
            # Send cancellation email to the reservers
            emails.CancellationEmail(
                user_action, reserver.email, df_post, reserver.full_name
            )
            # Update the reservation state
            reservation.reserv_state = variabless.canceled
            reservation.canceled_by = variabless.canceled_by_pro
            reservation.save()

    def get(self, request):
        pass

    @staticmethod
    def post(request):
        user_action = request.POST['user_action']
        member_id = int(request.POST['member_id'])

        if (user_action == "canceled_by_pro") or (user_action == "completed_by_pro"):  #
            post_id = int(request.POST['post_id'])
            if user_action == "canceled_by_pro":  # Cancel this reservation
                # Update the post_state after user cancellation
                threads.UpdateModel(
                    models.Posts,
                    row_id=post_id,
                    **{
                        'post_state': variabless.canceled
                    }
                )
                # Get the canceled post information
                UserActions.manage_bookers(
                    post_id, user_action
                )
            elif user_action == "completed_by_pro":
                threads.UpdateModel(
                    models.Posts,
                    row_id=post_id,
                    **{
                        'post_state': variabless.completed
                    }
                )
        elif (user_action == "canceled_by_res") or (user_action == "completed_by_res"):
            reservation_id = request.POST["reservation_id"]
            poster_id = request.POST["poster_id"]
            post_id = request.POST["post_id"]
            full_name = request.POST["r_full_name"]
            language = request.POST["r_language"]
            # departure_date = request.POST["departure_date"]
            if user_action == "canceled_by_res":  # Cancel this reservation
                # Get the data of the post
                post = utils.QuerySet.using_get(
                    models.Posts,
                    **{'id': post_id}
                )
                # Update user post after the cancellation
                nbr_kilos = int(request.POST['nbr_kilos'])
                nbr_kilos = int(post.number_of_kg) + nbr_kilos
                post.number_of_kg = nbr_kilos
                post.save()
                # Update the reservation model states
                threads.UpdateModel(
                    models.Reservations,
                    row_id=reservation_id,
                    **{
                        'reserv_state': variabless.canceled,
                        'canceled_by': variabless.canceled_by_res
                    }
                )
                # Send a email to proposer after the cancellation
                poster = utils.QuerySet.using_get(
                    models.Users,
                    **{
                        'id': poster_id
                    }
                )
                df_post = utils.PostDetail.as_dataframe(post_id)
                # Send a email to the poster
                emails.CancellationEmail(
                    user_action, poster.email, df_post, full_name, language=language
                )
            elif user_action == "completed_by_res":
                threads.UpdateModel(
                    models.Reservations,
                    row_id=reservation_id,
                    **{
                        'reserv_state': variabless.completed
                    }
                )
        elif user_action == 'complete_alert':
            alert_id = request.POST['alert_id']
            alert = utils.QuerySet.using_get(models.AlertMe, **{'id': alert_id})
            alert.alert_state = 'Completed'
            alert.save()

        context = {}
        utils.MemberProfileData(member_id, context, forms)
        utils.UserAlerts(
            request.session['user_id'], context
        )

        return render(
             request, template.profile_html, context
         )


class RegisterNewPostView(View):
    def __init__(self):
        self.context = {
            'form': forms.NewPostForm(),
            'df_current_n_posts': pd.DataFrame(),
            'countries': utils.Countries.name(),
            'post_confirmed': False,
            'profile_is_updated': False
        }

    def get(self, request):
        self.context['post_confirmed'] = False
        if 'user_id' in request.session:
            pass

        return render(
            request, template.new_post_form_html, self.context
        )

    def post(self, request):
        form = forms.NewPostForm(request.POST or None)
        user_id = request.session['user_id']
        if form.is_valid():
            self.context['depart_date'] = request.POST['departure_date']
            self.context['number_of_kg'] = request.POST['numberOfKg']
            self.context['price_of_kg'] = request.POST['priceOfKg']
            self.context['gp_sent_by'] = request.POST['gpSentBy']
            self.context['comment'] = request.POST['comment']
            country_currency = request.POST['countryCurrency']
            # === Get the city and country id ===
            depart_city_id = request.POST['depart_city']
            depart_country_id = request.POST['depart_country']
            # === Get the departure city name ===
            departure = utils.CityAndCountry.names(
                depart_city_id, depart_country_id
            )
            self.context['departure'] = departure
            # === Get the city and country id ===
            arrival_city_id = request.POST['arrival_city']
            arrival_country_id = request.POST['arrival_country']
            # === Get the arrival city name ===
            destination = utils.CityAndCountry.names(
                arrival_city_id, arrival_country_id
            )
            self.context['destination'] = destination
            # === Generate a new code for this new post ===
            self.context['post_code'] = utils.Generator.post_code(user_id)
            # === Check if the proposed date is valid ===
            dep_date = self.context['depart_date']
            date_checker = utils.DateChecker()
            is_valid_date = date_checker.departure_date_checker(dep_date)
            # Save the data if the date is valid
            if is_valid_date:
                if country_currency != 'None':
                    # === Get the proposition currency (country)
                    country_query = utils.Country.name(
                        country_name=country_currency
                    )
                    currency = country_query.currency
                    # === Get the user information
                    user = utils.QuerySet.using_get(
                        model_name=models.Profiles, id=user_id
                    )
                    # Add the new data to the database
                    service = 'GP'
                    if service == 'GP':
                        # === Add the new post to db ===
                        kwargs = {
                            'poster_id': user.id,
                            'departure_date': self.context['depart_date'],
                            'depart_country_id': depart_country_id,
                            'depart_city_id': depart_city_id,
                            'arrival_country_id': arrival_country_id,
                            'arrival_city_id': arrival_city_id,
                            'number_of_kg': self.context['number_of_kg'],
                            'price_of_kg': self.context['price_of_kg'],
                            'gp_sent_by': self.context['gp_sent_by'],
                            'comment': self.context['comment'],
                            'service': service,
                            'currency_used': currency,
                            'post_code': self.context['post_code'],
                        }
                        threads.CreateNewRecord(
                            models.Posts, **kwargs
                        )
                        # Send alert after proposition
                        threads.SendAlert(
                            user.id, **kwargs
                        )
                    elif service == 'taxi':
                        pass
                    else:
                        pass

                    self.context['post_confirmed'] = True
                    self.context['currency'] = currency
                else:
                    messages.error(request, 'Sélectionner un pays pour le prix')
            else:
                messages.error(
                    request, 'Hops, vérifier la date du départ: \n {}'.format(
                        self.context['depart_date']
                    )
                )
        else:
            messages.error(
                request, "Formulaire non valide."
            )

        return render(
            request, template.new_post_form_html, self.context
        )


class UserProfileView(View):
    def __init__(self):
        # update_now = True
        self.context = {
            'profile_form': forms.UserProfileForm(),
            'df_current_n_posts': pd.DataFrame()
        }

    def get(self, request):
        user_id = request.session['user_id']
        #  ===== Get the user profile data =====
        utils.MemberProfileData(
            user_id, self.context, forms
        )
        # Get all user alerts
        utils.UserAlerts(
            request.session['user_id'], self.context
        )

        return render(
            request, template.profile_html, self.context
        )

    def post(self, request):
        user_id = request.session['user_id']
        # Update user's profile
        utils.UpdateProfile(
            request, user_id, self.context,
            **{
                'gender': request.POST['gender'],
                'phone_number': request.POST['phone_number'],
                'language': request.POST['language'],
                'country': request.POST['country'],
                'city': request.POST['city'],
                'account_type': request.POST['account_type'],
                'is_updated': True
            }
        )
        # Get all user alerts
        utils.UserAlerts(
            request.session['user_id'], self.context
        )

        return render(
            request, template.profile_html, self.context
        )


class EditUserProfileView(View):
    def __init__(self):
        self.context = {
            'df_current_n_posts': pd.DataFrame()
        }

    @staticmethod
    def user_profile_data(user_id, context, user):
        profile = utils.QuerySet.using_get(
            models.Profiles, user_id=user_id
        )
        context['user'] = user
        context['profile'] = profile

        user_form = forms.RegisterForm(instance=user)
        profile_form = forms.UserProfileForm(instance=profile)

        context['user_form'] = user_form
        context['profile_form'] = profile_form

    def get(self, request, user_id):
        user = utils.QuerySet.using_get(
            model_name=models.Users, id=user_id
        )
        #
        EditUserProfileView.user_profile_data(user_id, self.context, user)
        self.context['updating_user_profile'] = True
        # Get user's propositions and reservations
        utils.MemberPosts(user_id, self.context)
        utils.MemberReservations(user_id, self.context)

        return render(
            request, template.profile_html, self.context
        )

    def post(self, request, user_id):
        user = utils.QuerySet.using_get(
            model_name=models.Users, id=user_id
        )

        action = request.POST['action']
        if action == 'update_user_info':
            # updating user's email and full name
            full_name = request.POST['full_name'].strip()
            new_email = request.POST['email'].strip()
            if len(full_name.split(" ")) < 2:
                messages.error(request, 'Merci de saisir votre nom et prénom.')
            else:
                # Verify if the email is valid
                if emails.Checker.is_valid(new_email):
                    user.full_name = full_name
                    # It is an new email ?
                    if new_email != user.email:
                        user.email = new_email
                        user.active = False
                        user.save()
                        # Send a email confirmation
                        user = utils.QuerySet.using_get(
                            model_name=models.Users, id=user_id
                        )
                        domain_name = get_current_site(request).domain
                        emails.SendActivationMail(user, domain_name)
                        # Disconnect the use when the email have been changed
                        from django.contrib.sessions.models import Session
                        Session.objects.all().delete()
                        messages.success(
                            request, "Un email de confirmation vous a été envoyé."
                        )

                        return render(
                            request,
                            template.login_html,
                            {
                                'login_form': forms.LoginForm(),
                                'profile_form': forms.UserProfileForm(),
                                'df_current_n_posts': pd.DataFrame()
                            }
                        )
                    else:
                        user.save()
                    messages.success(
                        request, "Votre email et/ou nom et prenom ont été mis à jour."
                    )
                else:
                    messages.error(
                        request, "Format d'email incorrect!"
                    )
        elif action == "update_user_password":
            password1 = request.POST['password1']
            password2 = request.POST['password2']
            if password1 != password2:
                messages.error(request, "Les 2 mots de passe ne sont pas identiques.")
            else:
                user.password = password1
                user.save()
                messages.success(request, "Votre mot de pass ont été mis à jour.")
        elif action == "update_user_profile":
            user_id = request.session['user_id']
            # Adding data to database
            kwargs = {
                'gender': request.POST['gender'],
                'phone_number': request.POST['phone_number'],
                'language': request.POST['language'],
                'country': request.POST['country'],
                'city': request.POST['city'],
                'account_type': request.POST['account_type'],
                'is_updated': True
            }

            utils.UpdateProfile(
                request, user_id, self.context, **kwargs
            )
            messages.success(request, "Votre profil a été mis à jour.")
        # User's posts and reservations
        utils.MemberPosts(user_id, self.context)
        utils.MemberReservations(user_id, self.context)
        #
        EditUserProfileView.user_profile_data(user_id, self.context, user)
        self.context['updating_user_profile'] = True

        return render(
            request, template.profile_html, self.context
        )


class UploadUserPictureView(View):
    def __init__(self):
        self.context = {
            'df_current_n_posts': pd.DataFrame()
        }

    def get(self, request):
        user_id = request.session['user_id']
        #
        utils.MemberPosts(user_id, self.context)
        utils.MemberReservations(user_id, self.context)

        self.context['upload_picture'] = True

        return render(
            request, template.profile_html, self.context
        )

    def post(self, request):
        def upload_image(uploaded_filename, new_filename, ext):
            user_folder = 'media/profile_img/'
            if not os.path.exists(user_folder):
                os.mkdir(user_folder)
            img_save_path = "{}/{}.{}".format(user_folder, new_filename, ext)
            with open(img_save_path, 'wb+') as f:
                for chunk in uploaded_filename.chunks():
                    f.write(chunk)

        user_id = request.session['user_id']
        IMAGE_FILE_TYPES = ['png', 'jpg', 'jpeg', 'gif']
        uploaded_filename = request.FILES['pictureToUpload']
        ext = str(uploaded_filename).split('.')[-1].lower()
        if ext in IMAGE_FILE_TYPES:
            # Now resize the image
            uploaded_filename = utils.ResizeImage.make_thumbnail(
                uploaded_filename, size=(100, 100)
            )
            new_filename = '{}{}'.format(
                'profile', str(user_id)
            )
            upload_image(
                uploaded_filename, new_filename, ext
            )
            # Upload profile picture with new name
            kwargs = {
                'image': 'profile_img/{}{}.{}'.format(
                'profile', str(user_id), ext
                )
            }
            threads.UpdateModel(
                models.Profiles, user_id=user_id, **kwargs
            )
            messages.success(request, "Votre photo a été changée avec succès.")
        else:
            messages.error(request, "Le format \".{}\" n'est pas autorisée".format(ext))
        # User's posts and reservations
        utils.MemberPosts(user_id, self.context)
        utils.MemberReservations(user_id, self.context)
        self.context['upload_picture'] = True

        return render(
            request, template.profile_html, self.context
        )


class ConfirmationEmailView(View):
    def __init__(self):
        self.context = {
            'login_form': forms.LoginForm(),
            'df_current_n_posts': pd.DataFrame()
        }

    def get(self, request, user_id, token):
        try:
            user_id = force_text(urlsafe_base64_decode(user_id))
            user = utils.QuerySet.using_get(
                models.Users, id=int(user_id)
            )
            # user = models.Users.objects.get(id=int(user_id))
            if not tokens.user_tokenizer.check_token(user, token):
                # msg = 'Votre compte est déjà activé.'
                messages.info(request, 'Votre compte est déjà activé.')

                return render(
                    request, template.login_html, self.context
                )
            # Update user's active field to True
            kwargs = {'active': True}
            threads.UpdateModel(
                models.Users, row_id=user_id, **kwargs
            )
            messages.success(request, 'Votre compte a été activé avec succès.')
            return render(
                request, template.login_html, self.context
            )
        except(TypeError, ValueError, OverflowError, models.Users.DoesNotExist):
            return render(
                request, template.login_html, self.context
            )


class AjaxLoadCitiesView(View):
    def __init__(self):
        self.template_name = 'gp_app/city_dropdown_list_options.html'
        self.context = {}

    def get(self, request):
        country_id = request.GET.get('country_id')
        cities = utils.Cities.name(
            country_id
        )
        self.context['cities'] = cities

        return render(
            request, self.template_name, self.context
        )


class ResearchView(View):
    def __init__(self):
        self.context = {
            'form': forms.ResearchForm(),
            'df_current_n_posts': pd.DataFrame(),
            'countries': utils.Countries.name(),
            'doing_research': False
        }

    def get(self, request):
        return render(
            request, template.research_html, self.context
        )

    def post(self, request):
        form = forms.NewPostForm(request.POST or None)
        if form.is_valid():
            depart_date = request.POST['departure_date']
            depart_city_id = request.POST['depart_city']
            depart_country_id = request.POST['depart_country']
            arrival_city_id = request.POST['arrival_city']
            arrival_country_id = request.POST['arrival_country']
            # AND condition to query to find posts
            research_results = utils.QuerySet.using_filter(
                models.Posts,
                **{
                    'departure_date': depart_date,
                    'depart_country_id': depart_country_id,
                    'depart_city_id': depart_city_id,
                    'arrival_country_id': arrival_country_id,
                    'arrival_city_id': arrival_city_id,
                    'post_state': 'In progress'
                }
            )
            df_research_results = research_results['query_as_dataframe']
            if not df_research_results.empty:
                # Rename some dataframe columns
                df_research_results = utils.GetPostsData.as_dataframe(
                    df_research_results
                )
                # Adding day, month and year columns to dataframe
                utils.DepartureDateInProgress(df_research_results)
                # Get the posts in date
                df_research_results = df_research_results[
                    df_research_results['departure_date_in_progress'] == True
                ]
                # Separate the first and last member's name
                names = df_research_results['p_full_name'].tolist()
                names = [''.join([name.split(" ")[0], ' ', list(name.split(" ")[1])[0]]) for name in names]
                df_research_results['publish_by'] = names
            # Update context to
            self.context['doing_research'] = True
            # Sorting the results by price
            df_research_results.sort_values(['price_of_kg'],  inplace=True)
            # Store the fund results
            self.context['df_research_results'] = df_research_results

        return render(
            request, template.research_html, self.context
        )


class AlertMeView(View):
    def __init__(self):
        self.context = {
            'form': forms.AlertMeForm(),
            'df_current_n_posts': pd.DataFrame(),
            'countries': utils.Countries.name(),
            'alert_me': False,
            'alert_me_confirmed': False
        }

    def get(self, request):
        return render(
            request, template.alert_me_html, self.context
        )

    def post(self, request):
        form = forms.AlertMeForm(request.POST or None)
        if form.is_valid():
            take_departure_date = request.POST['take_departure_date']
            depart_country_id = request.POST['depart_country']
            depart_city_id = request.POST['depart_city']
            arrival_country_id = request.POST['arrival_country']
            arrival_city_id = request.POST['arrival_city']
            departure_date = request.POST['departure_date']
            service = request.POST['service']
            # === Get the departure city name ===
            departure = utils.CityAndCountry.names(
                depart_city_id, depart_country_id
            )
            destination = utils.CityAndCountry.names(
                arrival_city_id, arrival_country_id
            )
            # Update context
            self.context['departure'] = departure
            self.context['destination'] = destination
            self.context['take_departure_date'] = take_departure_date
            # putting the inputs in sessions
            request.session['departure_date'] = departure_date
            request.session['take_departure_date'] = take_departure_date
            request.session['depart_country_id'] = depart_country_id
            request.session['depart_city_id'] = depart_city_id
            request.session['arrival_country_id'] = arrival_country_id
            request.session['arrival_city_id'] = arrival_city_id
            request.session['service'] = service
            request.session['departure'] = departure
            request.session['destination'] = destination
            #
            session_keys = [
                'departure_date', 'take_departure_date', 'depart_country_id', 'depart_city_id',
                'arrival_country_id', 'arrival_city_id', 'service', 'departure', 'destination'
            ]

            if take_departure_date == 'yes':
                # === Check if the proposed date is valid ===
                is_valid_date = utils.DateChecker().departure_date_checker(
                    departure_date
                )
                self.context['departure_date'] = departure_date
                if is_valid_date:
                    self.context['alert_me'] = True
                else:
                    for session_key in session_keys:
                        del request.session[session_key]

                    messages.error(
                        request, 'Hops, vérifier la date du départ: \n {}'.format(
                            self.context['departure_date']
                        )
                    )
            else:
                self.context['alert_me'] = True

        return render(
            request, template.alert_me_html, self.context
        )


class ConfirmAlertMeView(View):
    def __init__(self):
        self.context = {
            'form': forms.AlertMeForm(),
            'df_current_n_posts': pd.DataFrame(),
            'countries': utils.Countries.name(),
            'alert_me': False,
            'alert_me_confirmed': False
        }

    def get(self, request):
        return render(
            request, template.alert_me_html, self.context
        )

    def post(self, request):
        old_alert = utils.QuerySet.using_filter(
            models.AlertMe,
            **{
                'member_id': request.session['user_id'],
                'departure_date': request.session['departure_date'],
                'depart_country_id': request.session['depart_country_id'],
                'depart_city_id': request.session['depart_city_id'],
                'arrival_country_id': request.session['arrival_country_id'],
                'arrival_city_id': request.session['arrival_city_id'],
                'alert_state': 'In progress'
            }
        )

        if not old_alert['query_set']:
            take_departure_date = request.session['take_departure_date']
            if take_departure_date == 'yes':
                take_departure_date = True
            else:
                take_departure_date = False

            threads.CreateNewRecord(
                models.AlertMe,
                **{
                    'member_id': request.session['user_id'],
                    'departure_date': request.session['departure_date'],
                    'depart_country_id': request.session['depart_country_id'],
                    'depart_city_id': request.session['depart_city_id'],
                    'arrival_country_id': request.session['arrival_country_id'],
                    'arrival_city_id': request.session['arrival_city_id'],
                    'service': request.session['service'],
                    'take_departure_date': take_departure_date,
                    'alert_state': 'In progress'
                }
            )
            # Delete this sessions
            session_keys = [
                'departure_date', 'take_departure_date', 'depart_country_id', 'depart_city_id',
                'arrival_country_id', 'arrival_city_id', 'service', 'departure', 'destination'
            ]
            for session_key in session_keys:
                del request.session[session_key]

            messages.success(
                request, 'Votre alerte a été ajoutée avec succès.'
            )
        else:
            messages.error(
                request, 'La proposition: {} VERS {} existe déjà dans notre système.'.format(
                    request.session['departure'], request.session['destination']
                )
            )

        return render(
            request, template.alert_me_html, self.context
        )


class ContactView(View):
    def __init__(self):

        self.context = {
            'df_current_n_posts': pd.DataFrame(),
            'message_send': False,
            'feadback_message': ''
        }

    def get(self, request):
        return render(
            request, template.contact_html, self.context
        )

    def post(self, request):
        if request.method == 'POST':
            first_name = request.POST['first_name']
            last_name = request.POST['last_name']
            email = request.POST['email']
            need = request.POST['need']
            message = request.POST['message']
            # Sending email to helpers
            if int(request.POST['checker']) == 5:
                self.context['message_send'] = True
                self.context['feadback_message'] = ''
                self.context['feadback_message'] = "Votre message a été envoyé !"
                emails.ContactUs(
                    first_name, last_name, email, need, message
                )
            else:
                self.context['feadback_message'] = "Votre message n'a pas été envoyé !"

        return render(
            request, template.contact_html, self.context
        )


class AddNewPatientView(View):
    def __init__(self):
        self.context = {
            'message_send': False,
            'data_added': False,
            'feadback_message': '',
            'valid_form': True,
            'new_patient_data': {
                'full_name': '',
                'date_of_birth': '',
                'email': '',
                'phone_number': '',
                'four_last_digital_of_NNI': '',
                'city': '',
                'quartier': '',
                'list_of_doctors_to_see': {},
                'list_of_medicines': {},
                'vu_par_pharmacien': 'no'
            }
        }

    def get(self, request):
        return render(
            request, template.farl_index_html, self.context
        )

    def post(self, request):
        if request.method == 'POST':
            self.context['new_patient_data']["full_name"] = request.POST['full_name']
            self.context['new_patient_data']["date_of_birth"] = request.POST['birthday']
            self.context['new_patient_data']["email"] = request.POST['email']
            self.context['new_patient_data']["phone_number"] = request.POST['phone_number']
            self.context['new_patient_data']["city"] = request.POST['city']
            self.context['new_patient_data']["four_last_digital_of_NNI"] = request.POST['nni']
            # -----------------------------------------------------------------------
            doctors = request.POST.getlist('checks[]')
            visited_by = {}
            for doctor in doctors:
                visited_by[doctor] = {
                        "vu_par_docteur": "no",
                        "vu_par_pharmacien": "no"
                }

            self.context['new_patient_data']['list_of_doctors_to_see'] = visited_by

            # self.context['new_patient_data']['list_of_doctors_to_see'] = request.POST.getlist('checks[]')

            if len(self.context['new_patient_data']["full_name"].split(' ')) < 2:
                self.context['valid_form'] = False
                self.context['feadback_message'] = 'Saisir le nom et le prénom du patient.'

            if self.context['new_patient_data']["city"] == "None":
                self.context['valid_form'] = False
                self.context['feadback_message'] = 'Sélectionner la ville du patient.'

            if len(list(str(self.context['new_patient_data']["four_last_digital_of_NNI"]))) != 4:
                self.context['valid_form'] = False
                self.context['feadback_message'] = 'Saisir les 4 dernier chiffre du NNI.'

            if not self.context['new_patient_data']['list_of_doctors_to_see']:
                self.context['valid_form'] = False
                self.context['feadback_message'] = 'Sélectionner au minimum 1 spécialiste.'

            if self.context['new_patient_data']["city"] == "None":
                self.context['valid_form'] = False
                self.context['feadback_message'] = 'Sélectionner la ville du patient.'

            if self.context['valid_form']:
                dicts_of_new_data = self.context['new_patient_data']
                # Add a new patient to the file and get the PIN
                patient_pin = loadJsonData.AccessToJsonFile.add_new_patient(dicts_of_new_data)
                # ----------------------------------------------------------
                self.context['patient_pin'] = int(patient_pin.split("_")[1])
                self.context["full_name"] = self.context['new_patient_data']["full_name"]
                self.context["data_added"] = True
                self.context["message_send"] = True

        return render(
            request, template.farl_index_html, self.context
        )


class FindAPatientView(View):
    def __init__(self):
        medicine_data = loadJsonData.AccessToJsonFile.get_medicine_names()
        # print('============================ medicine_data', medicine_data)
        self.context = {
            "find_patient": True,
            "message_send": False,
            "patient_fund": False,
            "medicine_data": medicine_data,
            "days": [i for i in range(1, 32)],
            "months": [i for i in range(1, 13)]
          }

    def get(self, request):
        return render(
            request, template.farl_find_patient, self.context
        )

    def post(self, request):
        if request.method == 'POST':
            action = request.POST['action']
            patient_pin = request.POST['patient_pin']
            dict_of_patient_data, file_data = loadJsonData.AccessToJsonFile.find_a_patient(patient_pin)
            # print('========================dict_of_patient_data=====', dict_of_patient_data)
            if action == "find_patient":
                if dict_of_patient_data:
                    # A patient have been fund
                    self.context["find_patient"] = False
                    self.context["dict_of_patient_data"] = dict_of_patient_data
                    # -----------------------------------------------------------
                    self.context["full_name"] = dict_of_patient_data["full_name"]
                    self.context["date_of_birth"] = dict_of_patient_data["date_of_birth"]
                    self.context["email"] = dict_of_patient_data["email"]
                    self.context["phone_number"] = dict_of_patient_data["phone_number"]
                    self.context["four_last_digital_of_NNI"] = dict_of_patient_data["four_last_digital_of_NNI"]
                    self.context["quartier"] = dict_of_patient_data["quartier"]
                    # -----------------------------------------
                    self.context["list_of_doctors_to_see"] = []
                    for doctor in dict_of_patient_data["list_of_doctors_to_see"].keys():
                        if dict_of_patient_data["list_of_doctors_to_see"][doctor]['vu_par_docteur'] =='no':
                            self.context["list_of_doctors_to_see"].append(doctor)

                    self.context["list_of_medicines"] = dict_of_patient_data["list_of_medicines"]
                    # print('----------------------self.context["list_of_medicines"]', self.context["list_of_medicines"])
                    self.context["city"] = dict_of_patient_data["city"]
                    # -------------------------------------------------
                    request.session['patient_pin'] = patient_pin
                    self.context['patient_pin'] = patient_pin
                    self.context["find_patient"] = False
                    # self.context["patient_fund"] = True
                else:
                    self.context["message_send"] = True
            else:
                patient_pin = "_".join(["PIN", str(request.session['patient_pin'])])
                del request.session['patient_pin']
                # Get the post
                speciality = request.POST['speciality']
                file_data["Patients"][patient_pin]["list_of_doctors_to_see"][speciality]['vu_par_docteur'] = 'yes'

                # loadJsonData.AccessToJsonFile.update_json_file(file_data)
                # print(dict_of_patient_data)
                medicine = request.POST.getlist('checks[]')
                file_data["Patients"][patient_pin]["list_of_medicines"] = medicine
                # -------------------------------------------------------
                loadJsonData.AccessToJsonFile.update_json_file(file_data)

        return render(
            request, template.farl_find_patient, self.context
        )


class PatientMedicineView(View):
    def __init__(self):
        self.medicine_data = loadJsonData.AccessToJsonFile.get_medicine_names()
        self.context = {
            "find_patient": True,
            "message_send": False,
            "patient_fund": False,
            "medicine_data": self.medicine_data
          }

    def get(self, request):
        return render(
            request, template.farl_patient_medicine, self.context
        )

    def post(self, request):
        if request.method == 'POST':
            action = request.POST['action']
            patient_pin = request.POST['patient_pin']
            dict_of_patient_data, file_data = loadJsonData.AccessToJsonFile.find_a_patient(patient_pin)

            if action == "find_patient":
                if dict_of_patient_data:
                    # A patient have been fund
                    self.context["find_patient"] = False
                    self.context["dict_of_patient_data"] = dict_of_patient_data['list_of_doctors_to_see']
                    # -----------------------------------------------------------
                    self.context["full_name"] = dict_of_patient_data["full_name"]
                    self.context["date_of_birth"] = dict_of_patient_data["date_of_birth"]
                    self.context["email"] = dict_of_patient_data["email"]
                    self.context["phone_number"] = dict_of_patient_data["phone_number"]
                    self.context["four_last_digital_of_NNI"] = dict_of_patient_data["four_last_digital_of_NNI"]
                    self.context["quartier"] = dict_of_patient_data["quartier"]

                    self.context["vu_par_pharmacien"] = dict_of_patient_data['vu_par_pharmacien']
                    # -----------------------------------------
                    data = {}
                    for code in dict_of_patient_data["list_of_medicines"]:
                        data[code] = {
                            "qte": self.medicine_data[code]['qte'],
                            "name": self.medicine_data[code]['name']
                        }
                    self.context["code_medicines"] = data
                    self.context["city"] = dict_of_patient_data["city"]
                    # -------------------------------------------------
                    request.session['patient_pin'] = patient_pin
                    self.context['patient_pin'] = patient_pin
                    self.context["find_patient"] = False
                    self.context["find_patient"] = False
                    # self.context["patient_fund"] = True
                else:
                    self.context["message_send"] = True
            else:
                patient_pin = "_".join(["PIN", str(request.session['patient_pin'])])
                del request.session['patient_pin']
                # Get the post
                #speciality = request.POST['speciality']
                file_data["Patients"][patient_pin]["vu_par_pharmacien"] = 'yes'
                # -------------------------------------------
                # medicine = request.POST.getlist('checks[]')
                # file_data["Patients"][patient_pin]["list_of_medicines"] = medicine
                # -------------------------------------------------------
                loadJsonData.AccessToJsonFile.update_json_file(file_data)

        return render(
            request, template.farl_patient_medicine, self.context
        )
