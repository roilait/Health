# https://simpleisbetterthancomplex.com/tutorial/2016/07/22/how-to-extend-django-user-model.html#abstractuser
# https://stackoverflow.com/questions/44109/extending-the-user-model-with-custom-fields-in-django
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager
)
from datetime import datetime, date
from phonenumber_field.modelfields import PhoneNumberField

from django_resized import ResizedImageField
from django.utils.text import slugify


class UsersManager(BaseUserManager):
    """ custom user model """
    def create_user(
            self, email, full_name,
            password=None,
            is_staff=False,
            is_admin=False,
            is_active=False
    ):
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
            email, full_name,
            password=password,
            is_staff=True
        )

        return user

    def create_superuser(self, email, full_name, password):
        user = self.create_user(
            email, full_name,
            password=password,
            is_staff=True,
            is_admin=True,
            is_active=True
        )
        return user


# You should add this model to settings as (AUTH_USER_MODEL = 'gp_app.Users')
class Users(AbstractBaseUser):  # User = MyUser
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
        verbose_name = 'User Model'
        verbose_name_plural = 'Users Model'

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


class Profiles(models.Model):
    objects = None
    ACCOUNTS = [
        ('Perso', 'Personnel (Gratuit)'),
        ('Prof', 'Professionel (Gratuit)')
    ]
    LANGUAGES = [
            ('Français', 'Français'),
            ('Anglais', 'Anglais'),
            ('Arabe', 'Arabe')
    ]
    GENDER = [
        ('Femme', 'Femme'),
        ('Homme', 'Homme')
    ]
    user = models.OneToOneField(
        Users, related_name='user_id', on_delete=models.CASCADE
    )
    gender = models.CharField(
        max_length=50, blank=True, default='Femme', choices=GENDER
    )
    phone_number = PhoneNumberField(blank=False)
    language = models.CharField(
        max_length=50, default='Français', blank=True, choices=LANGUAGES
    )
    country = models.CharField(
        max_length=50, blank=True, null=True
    )
    city = models.CharField(max_length=50, blank=True, null=True)
    account_type = models.CharField(
        max_length=50, blank=True,
        default='Personnel (Gratuit)', choices=ACCOUNTS
    )
    notes = models.CharField(max_length=10, blank=True, default=5)
    accept_rate = models.CharField(max_length=10, blank=True, default=100)
    cancel_rate = models.CharField(max_length=10, blank=True, default=0)
    # image = models.ImageField(
    #     upload_to='profile_img',
    #     default='avatar.jpeg',
    #     blank=True
    # )
    image = ResizedImageField(
        size=[500, 300],
        upload_to='profile_img',
        default='avatar.jpeg',
        blank=True
    )
    is_updated = models.BooleanField(default=False)

    def __str__(self):
        return self.user.email


class Countries(models.Model):
    objects = None
    name = models.CharField(max_length=50)
    phone_code = models.CharField(max_length=5)
    currency = models.CharField(max_length=10)
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Cities(models.Model):
    objects = None
    country = models.ForeignKey(Countries, default=None, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Aeroports(models.Model):
    city = models.ForeignKey(Cities, default=None, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Posts(models.Model):
    objects = None
    poster = models.ForeignKey(Users, default=None, on_delete=models.CASCADE)
    departure_date = models.DateField("Date d depart", default=date.today)
    depart_country = models.ForeignKey(
        Countries, on_delete=models.CASCADE, related_name='depart_c'
    )
    depart_city = models.ForeignKey(
        Cities, on_delete=models.CASCADE, related_name='depart_v'
    )
    arrival_country = models.ForeignKey(
        Countries, on_delete=models.CASCADE, related_name='arrival_c'
    )
    arrival_city = models.ForeignKey(
        Cities, on_delete=models.CASCADE, related_name='arrival_v'
    )
    number_of_kg = models.IntegerField(default=0, blank=True)
    price_of_kg = models.IntegerField(default=0, blank=True)
    currency_used = models.CharField(max_length=10, blank=True, null=True)
    post_code = models.CharField(max_length=50, null=True, blank=True)
    post_state = models.CharField(
        max_length=50, default='In progress', null=True, blank=True
    )
    gp_sent_by = models.CharField(max_length=10, blank=True, null=True)
    service = models.CharField(max_length=10, null=True, blank=True)
    comment = models.TextField(max_length=100, blank=True, null=True)
    deposit_address = models.CharField(max_length=100, null=True, blank=True)
    recovery_address = models.CharField(max_length=100, null=True, blank=True)
    publish_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return '{}-{}'.format(self.depart_country, self.arrival_country)


class Research(models.Model):
    departure_date = models.DateField("Date of departure", default=date.today)
    depart_country = models.ForeignKey(
        Countries, on_delete=models.CASCADE, related_name='depart_Country'
    )
    depart_city = models.ForeignKey(
        Cities, on_delete=models.CASCADE, related_name='depart_City'
    )
    arrival_country = models.ForeignKey(
        Countries, on_delete=models.CASCADE, related_name='arrival_Country'
    )
    arrival_city = models.ForeignKey(
        Cities, on_delete=models.CASCADE, related_name='arrival_City'
    )


class AlertMe(models.Model):
    member = models.ForeignKey(Users, default=None, on_delete=models.CASCADE)
    departure_date = models.DateField("Date of departure", default=date.today)
    depart_country = models.ForeignKey(
        Countries, on_delete=models.CASCADE, related_name='depart_Country_alert'
    )
    depart_city = models.ForeignKey(
        Cities, on_delete=models.CASCADE, related_name='depart_City_alert'
    )
    arrival_country = models.ForeignKey(
        Countries, on_delete=models.CASCADE, related_name='arrival_Country_alert'
    )
    arrival_city = models.ForeignKey(
        Cities, on_delete=models.CASCADE, related_name='arrival_City_alert'
    )
    service = models.CharField(max_length=10, null=True, blank=True)
    alert_state = models.CharField(max_length=20, null=True, blank=True)
    take_departure_date = models.BooleanField()  # staff user non superuser
    publish_date = models.DateField(auto_now_add=True)


# class Comments(models.Model):
#     gd_id = models.CharField(max_length=50, null=True)
#     reservation_id = models.CharField(max_length=50, null=True)
#     comment_from_id = models.CharField(max_length=50, null=True)
#     comment_to_id = models.CharField(max_length=50, null=True)
#     comment = models.CharField(max_length=50, null=True)
#     note = models.CharField(max_length=50, null=True)
#     comment_state = models.CharField(max_length=50, null=True)
#     publish_date = models.CharField(max_length=50, null=True)


class Reservations(models.Model):
    post = models.ForeignKey(Posts, default=None, on_delete=models.CASCADE, related_name='post_id')
    poster = models.ForeignKey(Users, default=None, on_delete=models.CASCADE, related_name='poster_id')
    reserver = models.ForeignKey(Users, default=None, on_delete=models.CASCADE, related_name='reserver_id')
    nbr_kilos = models.IntegerField(default=0, blank=True)
    total_price = models.IntegerField(default=0, blank=True)
    post_code = models.CharField(max_length=10, null=True, blank=True)
    reserv_state = models.CharField(max_length=20, null=True, blank=True)
    canceled_by = models.CharField(max_length=50, null=True, blank=True)
    reserver_comment = models.CharField(max_length=150, null=True, blank=True)
    # poster_comment = db.Column(db.String(5), nullable=False)
    publish_date = models.DateTimeField(auto_now_add=True)
    # def __reper__(self):
    #     return '<Reservations {}>'.format(self.reserver_id)


class Comments(models.Model):
    objects = None
    post_id_com = models.ForeignKey(Posts, default=None, on_delete=models.CASCADE, related_name='post_id_1')
    post_id1 = models.ForeignKey(Posts, default=None, on_delete=models.CASCADE, related_name='post_id_11')
    post_id11 = models.ForeignKey(Posts, default=None, on_delete=models.CASCADE, related_name='post_id_111')
    poster_id = models.ForeignKey(Users, default=None, on_delete=models.CASCADE, related_name='poster_id_1')
    reserver_id = models.ForeignKey(Users, default=None, on_delete=models.CASCADE, related_name='reserver_id_1')
    sender_id = models.ForeignKey(Users, default=None, on_delete=models.CASCADE, related_name='sender_id')
    recepter_id = models.ForeignKey(Users, default=None, on_delete=models.CASCADE, related_name='recepter_id')
    comment = models.TextField(max_length=100, blank=True, null=True)
    note = models.IntegerField(default=0, blank=True)
    com_state = models.CharField(max_length=10, null=True, blank=True)
    publish_date = models.DateTimeField(auto_now_add=True)