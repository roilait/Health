# https://www.youtube.com/watch?v=8VYx-cNF1lU

from django.urls import path

from . import views

from django.conf import settings

from django.conf.urls.static import static

import random


urlpatterns = [
    path(
        '',
        views.HomeViewClass.as_view(),
        name='index'
    )
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
