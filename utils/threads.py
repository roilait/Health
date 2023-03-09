import threading
# Import from
from app import models
from commun import emails, utils

CONFIRM_EMAIL_BODY = 'emails/acc_active_email.html'

BOOKER_EMAIL_AFTER_CANCELLATION = 'emails/cancellation_email_to_reserver.html'


class UpdateModel:
    def __init__(self, model_name, row_id=None, user_id=None, **dict_of_values):
        UpdateModelUsingThread(model_name, row_id, user_id, **dict_of_values).start()


class UpdateModelUsingThread(threading.Thread):
    def __init__(self, model_name, row_id, user_id, **dict_of_values):
        self.model = model_name
        self.row_id = row_id
        self.user_id = user_id
        self.dict_of_values = dict_of_values
        # Call the threading function
        threading.Thread.__init__(self)

    def run(self):
        if self.row_id is not None:
            obj, created = self.model.objects.update_or_create(
                id=self.row_id, defaults=self.dict_of_values
            )

        if self.user_id is not None:
            obj, created = self.model.objects.update_or_create(
                user_id=self.user_id, defaults=self.dict_of_values
            )


class CreateNewRecord:
    def __init__(self, model_name, **values):
        CreateNewRecordUsingThread(model_name, **values).start()


class CreateNewRecordUsingThread(threading.Thread):
    def __init__(self, model_name, **values):
        self.model = model_name
        self.values = values
        # Call the threading function
        threading.Thread.__init__(self)

    def run(self):
        new_record = self.model(**self.values)
        new_record.save()


class SendAlert:
    def __init__(self, user_id, **kwargs):
        SendAlertUsingThread(user_id, **kwargs).start()


class SendAlertUsingThread(threading.Thread):
    def __init__(self, user_id, **kwargs):
        key_list = [
            'departure_date', 'depart_country_id', 'depart_city_id', 'arrival_country_id', 'arrival_city_id'
        ]
        self.kwargs = {key: val for key, val in kwargs.items() if key in key_list}
        self.kwargs['alert_state'] = 'In progress'
        self.kwargs['departure'] = utils.GetCityAndCountry.names(
            self.kwargs['depart_city_id'], self.kwargs['depart_country_id']
        )
        self.kwargs['destination'] = utils.GetCityAndCountry.names(
            self.kwargs['arrival_city_id'], self.kwargs['arrival_country_id']
        )
        self.user_id = user_id
        # Calling the threading function
        threading.Thread.__init__(self)

    def run(self):
        # key_list = ['departure_date', 'departure', 'destination']
        try:
            # Find members who want to be alerted for this post
            # kwargs = {key: val for key, val in self.kwargs.items() if key not in key_list}
            keys_list = ['departure_date', 'departure', 'destination']
            members = utils.QuerySet.using_filter(
                models.AlertMe,
                **{
                    key: val for key, val in self.kwargs.items() if key not in keys_list
                }
            )
            members = members['query_set']
            if members:
                for member in members:
                    member_id = member.member_id
                    user = utils.QuerySet.using_get(
                        models.Users, **{'id': member_id}
                    )
                    user_email = user.email
                    user_full_name = user.full_name
                    # Check if the member is fixed the departure date
                    if member.take_departure_date:
                        # Verify if the departure date is same
                        departure_date = str(member.departure_date)
                        if (departure_date == self.kwargs['departure_date']) and (member_id != self.user_id):
                            # Send a email to asker
                            emails.SendAlertEmail(user_email, user_full_name, **self.kwargs)
                    else:
                        # Send a email to asker
                        emails.SendAlertEmail(user_email, user_full_name, **self.kwargs)
        except Exception as e:
            pass
