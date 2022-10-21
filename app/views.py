from django.shortcuts import render, redirect

from django.contrib import messages

from django.contrib import auth

import os

import pandas as pd

from django.utils.encoding import force_text

from django.utils.http import urlsafe_base64_decode

from django.contrib.sites.shortcuts import get_current_site

from django.views import View

from utils import html_file_name


class HomeViewClass(View):
    def __init__(self):
        # Get the current post as Dataframe
        self.context = {
            'df_current_n_posts': pd.DataFrame()
        }

    def get(self, request):
        # send_email_task.delay()
        return render(
            request, html_file_name.index_html, self.context
        )

    def post(self, request):
        return render(
            request, template.index_html, self.context
        )

