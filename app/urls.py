# https://www.youtube.com/watch?v=8VYx-cNF1lU

from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

import random


urlpatterns = [
    path('', views.HomeViewClass.as_view(), name='index'),
    path('inscription/', views.RegisterViewClass.as_view(), name='register'),
    path('connexion/', views.LoginViewClass.as_view(), name='login'),
    path('deconnexion/', views.LogoutViewClass.as_view(), name='logout'),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
