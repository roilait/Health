# https://simpleisbetterthancomplex.com/tutorial/2016/07/22/how-to-extend-django-user-model.html#abstractuser
# https://stackoverflow.com/questions/44109/extending-the-user-model-with-custom-fields-in-django

# python manage.py migrate
# python manage.py makemigrations
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager
)
#from datetime import datetime, date
from phonenumber_field.modelfields import PhoneNumberField
# pip install django-phonenumber-field
# pip install django-phonenumbers

from django_resized import ResizedImageField
from django.utils.text import slugify


class UsersManager(BaseUserManager):
    """ custom user model """
    def create_user(self, email, full_name, password=None, is_staff=False, is_admin=False, is_active=False):
        """ Create user."""
        if not email:
            raise ValueError("Un membre doit avoir un email.")

        if not password:
            raise ValueError("Un membre doit avoir un mot de passe.")

        if not full_name:
            raise ValueError("Un membre doit avoir un nom et prénom.")

        user = self.model(
            email=self.normalize_email(email.strip()),
            full_name=" ".join(full_name.strip().split())
        )
        # Create a new user
        user.set_password(password.strip())
        user.staff = is_staff
        user.admin = is_admin
        user.active = is_active
        user.last_login = timezone.now()
        user.date_joined = timezone.now()
        # Save the new user
        user.save(using=self._db)
        ## Create a profile for the new user
        profile = Profiles.objects.create(user=user)
        profile.save()

        return user

    def create_staffuser(self, email, full_name, password):
        user = self.create_user(
            email, full_name, password=password, is_staff=True
        )

        return user

    def create_superuser(self, email, full_name, password):
        user = self.create_user(
            email, full_name, password=password, is_staff=True, is_admin=True, is_active=True
        )
        return user


# You should add this model to settings as (AUTH_USER_MODEL = 'gp_app.Users')
class Members(AbstractBaseUser):  # User = MyUser
    id = models.AutoField(primary_key=True)
    full_name = models.CharField(max_length=50, null=True)
    email = models.EmailField(max_length=255, unique=True)
    password = models.CharField(max_length=128, blank=True)
    active = models.BooleanField(default=True)  # can login
    staff = models.BooleanField(default=False)  # staff user non superuser
    admin = models.BooleanField(default=False)  # Superuser
    date_joined = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    # Adding the obj of the user manager
    objects = UsersManager()
    # In this case the username is the user email
    USERNAME_FIELD = 'email'
    # This is the required fields, by default username and password are required
    REQUIRED_FIELDS = ['full_name']

    class Meta:
        verbose_name = 'Member'
        verbose_name_plural = 'Members'

    def __str__(self):
        return self.email

    def get_full_name(self):
        return self.full_name

    def get_short_name(self):
        return self.full_name

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_admin(self):
        return self.admin

    @property
    def is_active(self):
        return self.active

    @property
    def is_staff(self):
        return self.staff


class Countries(models.Model):
    # objects = None
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    phone_code = models.CharField(max_length=5)
    currency = models.CharField(max_length=10)
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Cities(models.Model):
    # objects = None
    id = models.AutoField(primary_key=True)
    country = models.ForeignKey(Countries, default=None, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Profiles(models.Model):
    # objects = None
    ACCOUNTS = [('', 'Le compte est:'), ('Perso', 'Personnel'), ('Prof', 'Professionel')]
    LANGUAGES = [('', 'Choisir langue...'), ('fr', 'Français'), ('en', 'Anglais'), ('ar', 'Arabe')]
    GENDER = [('', 'Sexe...'), ('F', 'Femme'), ('H', 'Homme')]
    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(Members, related_name='user_id', on_delete=models.CASCADE)
    country = models.ForeignKey(Countries, on_delete=models.CASCADE, null=True, related_name="res_country")
    city = models.ForeignKey(Cities, on_delete=models.CASCADE, null=True, related_name="res_city")
    gender = models.CharField(max_length=50, blank=True, default='Femme', choices=GENDER)
    phone_number = PhoneNumberField(blank=False)
    language = models.CharField(max_length=50, default='Français', blank=True, choices=LANGUAGES)
    account_type = models.CharField(max_length=50, blank=True, default='Personnel (Gratuit)', choices=ACCOUNTS)
    notes = models.CharField(max_length=10, blank=True, default=5)
    accept_rate = models.CharField(max_length=10, blank=True, default=100)
    cancel_rate = models.CharField(max_length=10, blank=True, default=0)
    image = ResizedImageField(size=[500, 300], upload_to='profile_img', default='avatar.jpeg', blank=True)
    is_updated = models.BooleanField(default=False)
    last_connexion = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return self.account_type

