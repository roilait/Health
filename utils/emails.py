from django.template.loader import get_template
# from django.core.mail import EmailMessage
import re
import threading
from django.core.mail import EmailMessage
from django.conf import settings
from gp_project.settings import EMAIL_HOST_USER
from commun.tokens import user_tokenizer
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.shortcuts import reverse

CONFIRM_EMAIL_BODY = "emails/acc_active.html"

BOOKER_EMAIL_AFTER_CANCELLATION = "emails/cancellation_to_reserver.html"

ALERT_ME = "emails/alert.html"

HELPER_EMAIL = "moussalemoussa@gmail.com"

EMAIL_AFTER_RESERVATION = "emails/after_reservation.html"


class EmailThread(threading.Thread):
    def __init__(self, email_message):
        self.email_message = email_message
        # Call the threading function
        threading.Thread.__init__(self)

    def run(self):
        self.email_message.send()


class SendEmail:
    def __init__(self, email_subject, message, send_to_email):
        email_message = EmailMessage(
            email_subject, message, to=[send_to_email], from_email=EMAIL_HOST_USER
        )
        email_message.content_subtype = "html"
        # Send The email
        EmailThread(email_message).start()


class SendAlertEmail:
    def __init__(self, send_to_email, full_name, **kwargs):
        message = get_template(ALERT_ME).render(
            {
                "departure_date": kwargs["departure_date"],
                "departure": kwargs["departure"],
                "destination": kwargs["destination"],
                "full_name": full_name,
            }
        )
        email_subject = "Vitexpro vous avertit un GP"
        # email_subject = 'Vitexpro - annulation'
        SendEmail(
            email_subject, message, send_to_email
        )


class CancellationEmail:
    def __init__(self, action, send_to_email, df, full_name, language=None):
        if action == "canceled_by_pro":
            canceler_full_name = df["p_full_name"].values[0]
            canceler_language = df["p_language"].values[0]
            reciver_full_name = full_name
            canceled_by_pro = True
        else:
            canceler_full_name = full_name
            canceler_language = language
            reciver_full_name = df["p_full_name"].values[0]
            canceled_by_pro = False

        message = get_template(BOOKER_EMAIL_AFTER_CANCELLATION).render(
            {
                "departure_date": df["departure_date"].values[0],
                "departure": "{}, {}".format(
                    df["depart_city"].values[0], df["depart_country"].values[0]
                ),
                "destination": '{}, {}'.format(
                    df["arrival_city"].values[0], df["arrival_country"].values[0]
                ),
                "canceler_full_name": canceler_full_name,
                "canceler_language": canceler_language,
                "reciver_full_name": reciver_full_name,
                "canceled_by_pro": canceled_by_pro
            }
        )

        email_subject = "Vitexpro - annulation"
        SendEmail(
            email_subject, message, send_to_email
        )


class ContactUs:
    def __init__(self, first_name, last_name, email, need, message):
        email_subject = "Vitexpro - Help me",
        message = "Message de la part de {} {} à propos de son {}: {} ({})".format(
                        first_name, last_name, need, message, email
                  )
        SendEmail(
            email_subject, message, HELPER_EMAIL
        )


class ResetPassword:
    def __init__(self, full_name, user_email, security_code):
        email_subject = "Vitexpro - Réinitialiser votre mot de passe",
        message = "Bonjour {}, voici votre code de sécurité pour " \
                  "réinitialiser votre mot de passe. Code: {}".format(
                        full_name, security_code
                  )

        SendEmail(
            email_subject, message, user_email
        )


class SendActivationMail:
    def __init__(self, user, domain_name):
        user_email = user.email  # 'moutraoree@gmail.com'  # user.email
        http = "http://"
        if not settings.DEBUG:
            http = "https://"
        url = http + domain_name + reverse(
            "confirm_email",
            kwargs={
                "user_id": urlsafe_base64_encode(force_bytes(user.id)),
                "token": user_tokenizer.make_token(user)
            }
        )
        email_subject = "Confirme votre email"
        message = get_template(CONFIRM_EMAIL_BODY).render(
            {
                "confirm_url": url
            }
        )
        # Sending email in background
        SendEmail(
            email_subject, message, user_email
        )


class Checker:
    @staticmethod
    def is_valid(email):
        reg = "^[a-zA-Z0-9_+&*-]+(?:\\.[a-zA-Z0-9_+&*-]+)*@(?:[a-zA-Z0-9-]+\\.)+[a-zA-Z]{2,7}$"
        if re.match(reg, str(email)) is not None:
            return True
        return False


class ToReserverAndPoster:
    def __init__(self, **kwargs):
        # Send a summer email to poster
        SendEmailsAfterReservation(
            email_to_poster=True, **kwargs
        )
        # Send email to reserver
        SendEmailsAfterReservation(
            email_to_reserver=True, **kwargs
        )


class SendEmailsAfterReservation:
    def __init__(self, email_to_poster=False, email_to_reserver=False, **kwargs):
        language, receiver_full_name = None, None
        full_name, phone, email, send_to_email = None, None, None, None

        if email_to_poster:
            send_to_email = kwargs["poster_email"]
            receiver_full_name = kwargs["poster_full_name"]
            # Get poster's information
            email = kwargs["reserver_email"]
            full_name = kwargs["reserver_full_name"]
            phone = kwargs["reserver_phone_number"]
            language = kwargs["reserver_language"]

        if email_to_reserver:
            send_to_email = kwargs["reserver_email"]
            receiver_full_name = kwargs["reserver_full_name"]
            # Get reserver's information
            email = kwargs["poster_email"]
            full_name = kwargs["poster_full_name"]
            phone = kwargs["poster_phone_number"]
            language = kwargs["poster_language"]

        message = get_template(EMAIL_AFTER_RESERVATION).render(
            {
                "departure_date": kwargs["departure_date"],
                "departure": kwargs["departure"],
                "destination": kwargs["destination"],
                "kg_reserved": kwargs["kg_reserved"],
                "total_price": kwargs["total_price"],
                "currency": kwargs["currency"],
                "post_code": kwargs["post_code"],
                "poste_code": kwargs["post_code"],
                "email_to_poster": email_to_poster,
                "email_to_reserver": email_to_reserver,
                # Receiver information
                "receiver_language": language,
                "receiver_full_name": receiver_full_name,
                "full_name": full_name,
                "phone": phone,
                "email": email
            }
        )

        email_subject = "Vitexpro - nouvelle réservation"
        SendEmail(
            email_subject, message, send_to_email
        )
