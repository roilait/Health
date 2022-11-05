# Create your tasks here
from celery import shared_task
from django.core.mail import send_mail
from gp_project import settings


@shared_task
def add(x, y):
    #time.sleep(60)
    x + y
    return x + y


@shared_task
def send_email_task():
    """
    Task to send an e-mail notification when an order is successfully created.
    """
    send_from = settings.EMAIL_HOST_USER
    print(11111111)
    Title = 'New Config Django send mail'
    Message = 'This email was sent by the program, please ignore it, using CELERY, heroko url'
    print("I am asynchronous")
    send_to = 'moutraoree@gmail.com'
    send_mail(Title, Message, send_from, [send_to,])
