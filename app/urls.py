# https://www.youtube.com/watch?v=8VYx-cNF1lU

from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
import random

random_links = 'abcdefghijklmnoprstuvwxyzABCDEFGHIJKLMNPQRSTUVWXYZ123456789@&'

link_word = 40

# from autoslug.fields import AutoSlugField

current_link = ''.join(random.choices(
    list(random_links), k=link_word)
)

# app_name = gp_app
urlpatterns = [
    path('', views.HomeView.as_view(), name='index'),
    path('inscription/', views.RegisterView.as_view(), name='register'),
    path('connexion/', views.LoginView.as_view(), name='login'),
    path('deconnexion/', views.LogoutView.as_view(), name='logout'),
    path('user_profile/', views.UserProfileView.as_view(), name='user_profile'),
    path('faire-une-mise-a-jour-de-mon-profile/<int:user_id>', views.EditUserProfileView.as_view(), name='edit_user'),
    path('reinitialiser-mon-mot-de-passe/', views.ResetPasswordView.as_view(), name='forgotten_password'),
    path('proposer-un-service/', views.RegisterNewPostView.as_view(), name='proposition'),
    path('voir-les-detail-de-ce-gp/<int:post_id>/edit/', views.PostDetailView.as_view(), name='post_detail'),
    path('faire-des-mises-a-jours-sur-les-services/', views.UserActions.as_view(), name='user_actions'),
    path('faire-une-reservation', views.ReservationView.as_view(), name='confirm_reservation'),
    path('alerte-moi-si-un-co-valiseur-propose-ce-gp/', views.AlertMeView.as_view(), name='alert_me'),
    path('confirm-alert-me/', views.ConfirmAlertMeView.as_view(), name='confirm_alert_me'),
    path('trouver-un-service/', views.ResearchView.as_view(), name='research'),
    path('nous-contacter/', views.ContactView.as_view(), name='contact_us'),
    path('email-de-confirmiation/<user_id>/<token>', views.ConfirmationEmailView.as_view(), name='confirm_email'),
    path('televerser/', views.UploadUserPictureView.as_view(), name='upload_picture'),
    path('ajax/load-cities', views.AjaxLoadCitiesView.as_view(), name='ajax_load_cities'),
    path('ajouter-un-patient/', views.AddNewPatientView.as_view(), name='addNewpatient'),
    path('trouver-un-patient/', views.FindAPatientView.as_view(), name='findAPatient'),
    path('medicament-pour-le-patient/', views.PatientMedicineView.as_view(), name='patientMedicine')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)