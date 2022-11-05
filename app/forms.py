from django import forms
from django.contrib.auth import get_user_model

# from django.urls import reverse, reverse_lazy

# https://django-betterforms.readthedocs.io/en/latest/multiform.html#betterforms.multiform.MultiForm
# https://stackoverflow.com/questions/569468/django-multiple-models-in-one-template-using-forms
# https://blog.khophi.co/extending-django-user-model-userprofile-like-a-pro/
# from django.contrib.auth.models import User

from crispy_forms.bootstrap import Field, InlineRadios, TabHolder, Tab
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Div, Fieldset, HTML
from crispy_forms.bootstrap import (
    PrependedText, AppendedText, PrependedAppendedText, InlineRadios,
    Tab, TabHolder, AccordionGroup, Accordion, Alert, InlineCheckboxes,
    FieldWithButtons, StrictButton, FormActions
)

from bootstrap_datepicker_plus import DatePickerInput  #, TimePickerInput
# from betterforms.multiform import MultiModelForm

# from jsons import get_list_of_all_countries
from . import models
# from gp_project.settings import RECAPTCHA_PUBLIC_KEY
# from commun import functions as func

User = get_user_model()


def v_helper_css(obj):
    obj.form_class = 'form-vertical'
    obj.label_class = 'col-12'
    obj.field_class = 'col-11'
    obj.form_class = 'blueForms'
    obj.form_method = 'post'


def h_helper_css(obj):
    obj.form_action = 'submit_survey'
    obj.form_class = 'container-fluid'
    obj.wrapper_class = 'row'
    obj.label_class = 'col-12'
    obj.field_class = 'col-12'
    obj.form_class = 'blueForms'


# Registration form
class RegisterForm(forms.models.ModelForm):
    password1 = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = models.Users
        fields = ['full_name', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)
        # add custom error messages
        self.helper = FormHelper(self)
        # Remove all form labels
        self.helper.form_show_labels = False
        # This allow you to add some custom html to your form
        self.helper.form_tag = False
        self.helper.layout = Layout(
            PrependedText(
                'full_name',
                "<i class='fa fa-user'></i>",
                placeholder='Nom et Prénom'
            ),
            PrependedText(
                'email',
                "<i class='fa fa-envelope' aria-hidden='true'></i>",
                placeholder='Adresse Email'
            ),
            PrependedText(
                'password1',
                '<i class="fa fa-unlock-alt"> </i>',
                placeholder="Choisir un Mot de Passe"
            ),
            PrependedText(
                'password2',
                '<i class="fa fa-lock"></i>',
                placeholder='Confirmer votre mot de passe'
            ),
        )


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = models.Profiles

        fields = [
            'gender', 'language', 'phone_number', 'country', 'city',
            'account_type', 'image'
        ]

    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        # add custom error messages
        self.helper = FormHelper(self)
        self.helper.form_show_labels = False
        # This allow you to add some custom html to your form
        self.helper.form_tag = False
        self.helper.layout = Layout(
            PrependedText(
                'gender',
                "<i class='fa fa-venus-mars' style='margin-right:5px'></i> "
                "Sexe <i style='margin-right:37px'></i>",
                css_class="inputblock-level",
                placeholder='Sexe'
            ),
            PrependedText(
                'language',
                "<i class='fa fa-users' style='margin-right:5px'></i> "
                "Langue <i style='margin-right:17px'></i>",
                placeholder='Langue de contact'
            ),
            PrependedText(
                'phone_number',
                "<i class='fa fa-phone' style='margin-right:5px'></i> Téléphone",
                css_class='inputblock-level',
                placeholder='+22234567890'
            ),
            PrependedText(
                'country',
                "<i class='fa fa-flag' style='margin-right:5px'></i> "
                "Pays <i style='margin-right:40px'></i>",
                placeholder='Pays de résidence'
            ),
            PrependedText(
                'city',
                "<i class='fa fa-home fa-fw' style='margin-right:5px'></i> "
                "Ville <i style='margin-right:38px'></i>",
                placeholder="Ville de résidence"
            ),
            PrependedText(
                'account_type',
                "<i class='fa fa-cog' style='margin-right:5px'></i> "
                "Compte <i style='margin-right:16px'></i>",
                placeholder='Type de compte'
            ),
            # Field('remember_me'),
            FormActions(Submit('update', 'Mettre à jour', css_class="btn-primary btn-md btn-block"))
        )


# def person_update_view(request, pk):
#     person = get_object_or_404(Person, pk=pk)
#     form = PersonCreationForm(instance=person)
#     if request.method == 'POST':
#         form = PersonCreationForm(request.POST, instance=person)
#         if form.is_valid():
#             form.save()
#             return redirect('person_change', pk=pk)
#     return render(request, 'persons/home.html', {'form': form})


class LoginForm(forms.Form):
    email = forms.EmailField(
        max_length=64,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'style': 'max-width: 20em; height: 3em;',
                'placeholder': 'example@example.com'
            }
        ),
        required=True
    )

    password = forms.CharField(
        max_length=150,
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'style': 'max-width: 20em; height: 3em;',
                'placeholder': 'Votre mot de passe'
            }
        ),
        required=True
    )

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        # Remove all form labels
        self.helper.form_show_labels = False
        # This allows you to add some custom html to your form
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Field("email"),
            Field("password"),
            Fieldset(
                '',
                HTML(""),
                Field('resume'),
            )
        )


class ForgotPasswordForm(forms.Form):
    email = forms.EmailField(
        label='Adresse email',
        max_length=100,
        required=True,
    )

    def __init__(self, *args, **kwargs):
        super(ForgotPasswordForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        # Remove all form labels
        self.helper.form_show_labels = False
        # This allow you to add some custom html to your form
        self.helper.form_tag = False
        self.helper.layout = Layout(
            PrependedText(
                'email',
                "<i class='fa fa-envelope'> </i>",
                placeholder="Adresse Email"
            ),
            HTML(
                '<a href={}> <p style="font-size:18px;color:blue">'
                "<i> Se connecter maintenant </i> </p></a>".format(
                    ("{% url 'login' %}"))),  # accounts:password-reset
            # Field('remember_me'),
            FormActions(Submit('forgot_password',
                               'Envoyer', css_class="btn-primary"))
        )


class DateInput(forms.DateInput):
    input_type = 'date'


# class PostForm(forms.ModelForm):
class NewPostForm(forms.ModelForm):
    class Meta:
        model = models.Posts
        fields = [
            'departure_date', 'depart_country', 'depart_city', 'arrival_country',
            'arrival_city', 'number_of_kg', 'price_of_kg', 'post_code',
            'post_state', 'gp_sent_by', 'service', 'comment'
        ]
        widgets = {
            'departure_date': DateInput(),  # ignore this too
            'bootstrap_date': DatePickerInput(),  # this is the focus part
        }

    def __init__(self, *args, **kwargs):
        super(NewPostForm, self).__init__(*args, **kwargs)
        self.fields['depart_city'].queryset = models.Cities.objects.none()
        self.fields['arrival_city'].queryset = models.Cities.objects.none()
        if 'depart_country' in self.data:
            try:
                country_id = int(self.data.get('depart_country'))
                self.fields['depart_city'].queryset = \
                    models.Cities.objects.filter(
                        country_id=country_id
                    ).order_by('name')
            except (ValueError, TypeError):
                pass  # invalid input from the client; ignore and fallback to empty City queryset
        elif self.instance.pk:
            self.fields['depart_city'].queryset = \
                self.instance.depart_country.cities_set.order_by('name')

        if 'arrival_country' in self.data:
            try:
                country_id = int(self.data.get('arrival_country'))
                self.fields['arrival_city'].queryset = \
                    models.Cities.objects.filter(
                        country_id=country_id
                    ).order_by('name')
            except (ValueError, TypeError):
                pass  # invalid input from the client; ignore and fallback to empty City queryset
        elif self.instance.pk:
            self.fields['arrival_city'].queryset = \
                self.instance.arrival_country.cities_set.order_by('name')

        self.helper = FormHelper()
        # Remove all form labels
        self.helper.form_show_labels = False
        # This allow you to add some custom html to your form
        self.helper.form_tag = False
        self.helper.layout = Layout(
            PrependedText(
                'departure_date',
                'Départ le <i style="color:red">*</i>'
                '<i style="margin-right:15px"></i>'
            ),
            PrependedText(
                'depart_country',
                '<i style="color:red"> De *</i> '
                '<i style="margin-right:56px"></i>'
            ),
            PrependedText(
                'depart_city',
                ' <i class="fas fa-plane-departure" style="margin-right:10px"></i>'
                ' A <i style="color:red">*</i>'
                '<i style="margin-right:40px"></i>'
            ),
            PrependedText(
                'arrival_country',
                '<i style="color:red"> Vers *</i> '
                '<i style="margin-right:44px"></i>'
            ),
            PrependedText(
                'arrival_city',
                '<i class="fas fa-plane-arrival" style="margin-right:10px"></i>'
                'A <i style="color:red">*</i>'
                '<i style="margin-right:40px"></i>'
            ),
        )


class ContactForm(forms.Form):
    full_name = forms.CharField(
        label='Nom et prénom',
        max_length=100,
        required=True,
    )
    email = forms.EmailField(
        label='Adresse email',
        max_length=100,
        required=True,
    )
    message = forms.CharField(
        label='Message',
        max_length=150,
        required=True,
        widget=forms.Textarea()
    )

    def __init__(self, *args, **kwargs):
        super(ContactForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'container-fluid'
        self.helper.wrapper_class = 'row'
        self.helper.label_class = 'col-5'
        self.helper.field_class = 'col-7'
        self.helper.form_class = 'form-horizontal'
        self.helper.layout = Layout(
            Fieldset(
                'Nous contacter',
                Div(
                    'full_name',
                    'email',
                    'message',
                ), style='color: brown;',
            ),
        )


class ResearchForm(forms.ModelForm):
    class Meta:
        model = models.Research
        fields = [
            'departure_date', 'depart_country', 'depart_city', 'arrival_country', 'arrival_city'
        ]
        widgets = {
            'departure_date': DateInput(),        # ignore this too
            'bootstrap_date': DatePickerInput(),  # this is the focus part
        }

    def __init__(self, *args, **kwargs):
        super(ResearchForm, self).__init__(*args, **kwargs)
        self.fields['depart_city'].queryset = models.Cities.objects.none()
        self.fields['arrival_city'].queryset = models.Cities.objects.none()
        if 'depart_country' in self.data:
            try:
                country_id = int(self.data.get('depart_country'))
                self.fields['depart_city'].queryset = \
                    models.Cities.objects.filter(
                        country_id=country_id
                    ).order_by('name')
            except (ValueError, TypeError):
                pass  # invalid input from the client; ignore and fallback to empty City queryset
        elif self.instance.pk:
            self.fields['depart_city'].queryset = \
                self.instance.depart_country.cities_set.order_by('name')

        if 'arrival_country' in self.data:
            try:
                country_id = int(self.data.get('arrival_country'))
                self.fields['arrival_city'].queryset = \
                    models.Cities.objects.filter(
                        country_id=country_id
                    ).order_by('name')
            except (ValueError, TypeError):
                pass  # invalid input from the client; ignore and fallback to empty City queryset
        elif self.instance.pk:
            self.fields['arrival_city'].queryset = \
                self.instance.arrival_country.cities_set.order_by('name')

        self.helper = FormHelper()
        # Remove all form labels
        self.helper.form_show_labels = False
        # This allows you to add some custom html to your form
        self.helper.form_tag = False
        self.helper.layout = Layout(
            PrependedText(
                'departure_date',
                'Départ le <i style="color:red">*</i>'
                '<i style="margin-right:10px"></i>'
            ),
            PrependedText(
                'depart_country',
                '<i style="color:red"> De *</i> '
                '<i style="margin-right:48px"></i>'
            ),
            PrependedText(
                'depart_city',
                ' <i class="fas fa-plane-departure" style="margin-right:10px"></i>'
                ' A <i style="color:red">*</i>'
                '<i style="margin-right:34px"></i>'
            ),
            PrependedText(
                'arrival_country',
                '<i style="color:red"> Vers *</i> '
                '<i style="margin-right:38px"></i>'
            ),
            PrependedText(
                'arrival_city',
                '<i class="fas fa-plane-arrival" style="margin-right:10px"></i>'
                'A <i style="color:red">*</i>'
                '<i style="margin-right:36px"></i>'
            ),
        )


class AlertMeForm(forms.ModelForm):
    class Meta:
        model = models.AlertMe
        fields = [
            'departure_date', 'depart_country', 'depart_city', 'arrival_country', 'arrival_city'
        ]
        widgets = {
            'departure_date': DateInput(),  # ignore this too
            'bootstrap_date': DatePickerInput(),  # this is the focus part
        }

    def __init__(self, *args, **kwargs):
        super(AlertMeForm, self).__init__(*args, **kwargs)
        self.fields['depart_city'].queryset = models.Cities.objects.none()
        self.fields['arrival_city'].queryset = models.Cities.objects.none()
        if 'depart_country' in self.data:
            try:
                country_id = int(self.data.get('depart_country'))
                self.fields['depart_city'].queryset = \
                    models.Cities.objects.filter(
                        country_id=country_id
                    ).order_by('name')
            except (ValueError, TypeError):
                pass  # invalid input from the client; ignore and fallback to empty City queryset
        elif self.instance.pk:
            self.fields['depart_city'].queryset = \
                self.instance.depart_country.cities_set.order_by('name')

        if 'arrival_country' in self.data:
            try:
                country_id = int(self.data.get('arrival_country'))
                self.fields['arrival_city'].queryset = \
                    models.Cities.objects.filter(
                        country_id=country_id
                    ).order_by('name')
            except (ValueError, TypeError):
                pass  # invalid input from the client; ignore and fallback to empty City queryset
        elif self.instance.pk:
            self.fields['arrival_city'].queryset = \
                self.instance.arrival_country.cities_set.order_by('name')

        self.helper = FormHelper()
        # Remove all form labels
        self.helper.form_show_labels = False
        # This allows you to add some custom html to your form
        self.helper.form_tag = False
        self.helper.layout = Layout(
            PrependedText(
                'departure_date',
                'Départ le <i style="color:red">*</i>'
                '<i style="margin-right:50px"></i>'
            ),
            PrependedText(
                'depart_country',
                '<i style="color:red"> Pays de départ *</i> '
                '<i style="margin-right:5px"></i>'
            ),
            PrependedText(
                'depart_city',
                '<i style="color:red"> Ville de départ *</i> '
                '<i style="margin-right:10px"></i>'
            ),
            PrependedText(
                'arrival_country',
                "<i style='color:red'> Pays d'arrivé *</i> "
                '<i style="margin-right:20px"></i>'
            ),
            PrependedText(
                'arrival_city',
                "Ville d'arrivée  <i style='color:red'> *</i>"
                '<i style="margin-right:20px"></i>'
            ),
        )


class SignUpForm1(forms.Form):
   first_name = forms.CharField(required=True, max_length=255)
   last_name = forms.CharField(required=True, max_length=255)
   email = forms.EmailField(required=True)
   phone = forms.CharField(required=True, max_length=200)
   address = forms.CharField(max_length=1000, widget=forms.Textarea())
   more_info = forms.CharField(max_length=1000, widget=forms.Textarea())
   color = forms.TypedChoiceField(
       label='Choose color',
       choices=((0, 'Red'), (1, 'Blue'), (2, 'Green')),
       coerce=lambda x: bool(int(x)),
       widget=forms.RadioSelect,
       initial='0',
       required=True)

   def __init__(self, *args, **kwargs):
       super(SignUpForm1, self).__init__(*args, **kwargs)
       self.helper = FormHelper()
       self.helper.form_id = 'id-personal-data-form'
       self.helper.form_method = 'post'
       #self.helper.form_action = reverse_lazy('submit_form')
       self.helper.add_input(Submit('submit', 'Submit', css_class='btn-success'))
       self.helper.form_class = 'form-horizontal'
       self.helper.layout = Layout(
           Fieldset('Name',
                    Field('first_name', placeholder='Your first name', css_class="some-class"),
                    Div('last_name', title="Your last name"),),
           Fieldset('Contact data', 'email', 'phone', style="color: brown;"),
           InlineRadios('color'),
           TabHolder(Tab('Address', 'address'),
                     Tab('More Info', 'more_info')))