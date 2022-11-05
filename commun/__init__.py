#from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string, get_template
from django.shortcuts import render, redirect, reverse
from django.core.mail import send_mail, EmailMessage, EmailMultiAlternatives

from app import models
from commun.tokens import user_tokenizer
from sante_project.settings import EMAIL_HOST_USER
#from datetime import date
#import random

CONFIRM_EMAIL_BODY = 'emails/acc_active_email.html'


def get_all_posts(n=None, state=None):
    if n is None:
        if state is None:
            post_set = models.Post.objects.all()
        else:
            post_set = models.Post.objects.filter(post_state=state)
    else:
        if state is None:
            post_set = models.Post.objects.all()[:n][::-1]
        else:
            post_set = models.Post.objects.filter(post_state=state)[:n][::-1]

    return post_set



