from django.shortcuts import render, redirect
# from django.shortcuts import get_object_or_404
# web: gunicorn gp_project.wsgi --preload --log-file -
from django.contrib import messages
from django.contrib import auth
import os  # re
import django
import time
# from django.utils.encoding import force_text
from django.utils.encoding import force_str
django.utils.encoding.force_text = force_str
from django.utils.http import urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site
from django.views import View
from django.contrib.sessions.models import Session


class HomeViewClass(View):
    def __init__(self):
        # Get the current post as Dataframe
        self.context = {}
        self.template = "index.html"

    def get(self, request):
        # send_email_task.delay()
        return render(
            request, "{}".format("index.html"), self.context
        )

    def post(self, request):
        return render(
            request, "{}".format("index.html"), self.context
        )


# add following to mysite/myapp/templatetags/myapp_tags.py
class RegisterViewClass(View):  # Registration class for a new member
    def __init__(self):
        # This is the class context
        self.context = {
            "current_date": time.strftime("%A %d/%m/%Y %H:%M:%S"),
        }

    def get(self, request):
        # Go to the registration form for a new member,
        return render(
            request, "{}".format("register.html"), self.context
        )

    def post(self, request):

        return render(
            request, "".format("register.html"), self.context
        )


class LoginViewClass(View):
    def __init__(self):
        self.context = {
            "current_date": time.strftime("%A %d/%m/%Y %H:%M:%S"),
        }
    def get(self, request):
        return render(
            request, "{}".format("login.html"), self.context
        )

    def post(self, request):
        # First displayed page
        return render(
            request, "{}".format("profile.html"), self.context
        )


class ResetPasswordViewClass(View):
    def __init__(self):
        self.context = {
            "current_date": time.strftime('%A %d/%m/%Y %H:%M:%S'),
        }

    def get(self, request):
        #
        return render(
            request, "{}".format("resetpassword.html"), self.context
        )

    def post(self, request):

        return render(
            request, "{}".format("resetpassword.html"), self.context
        )


class LogoutViewClass(View):
    def __init__(self):
        self.context = {}

    def get(self, request):
        auth.logout(request)

        return render(
            request, "{}".format("index.html"), self.context
        )

