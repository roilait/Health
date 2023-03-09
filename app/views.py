from django.shortcuts import render, redirect
import django
# from django.utils.encoding import force_text
from django.utils.encoding import force_str
from django.views import View
from utils import html_files as template
django.utils.encoding.force_text = force_str

import locale

locale.setlocale(locale.LC_TIME, '')


class HomeViewClass(View):
    def __init__(self):
        # Get the current post as Dataframe
        self.context = {

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

