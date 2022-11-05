from django.contrib import admin
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import ReadOnlyPasswordHashField
# from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin


from . import models
# Register your models here.
Users = get_user_model()

# list other models here
MODELS = [
    models.Profiles,
    models.Research,
    models.Countries,
    models.Cities,
    models.Aeroports,
    models.Posts,
    models.Reservations,
    models.Comments,
    models.AlertMe,
]


# class GpProjectAdmin(admin.ModelAdmin):
#     fieldsets = [
#
#     ]


class UserAdminCreationForm(forms.ModelForm):
    """
    A form for creating new users. Includes all the required
    fields, plus a repeated password.
    """
    password1 = forms.CharField(
        label='Mot de passe', widget=forms.PasswordInput
    )
    password2 = forms.CharField(
        label='Confirmer le mot de passe', widget=forms.PasswordInput
    )

    class Meta:
        model = Users
        fields = ['full_name', 'email']  # full_name

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                "Les deux mots de passe ne sont pas identiques"
            )
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(UserAdminCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserAdminChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = Users
        fields = ['full_name', 'email', 'password', 'active', 'admin']

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]


class UserAdmin(BaseUserAdmin):
    # The forms to add and change user instances
    form = UserAdminChangeForm
    add_form = UserAdminCreationForm
    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    search_fields = ('email',)
    ordering = ('email',)
    filter_horizontal = ()
    list_display = ['email', 'active', 'staff', 'admin']
    list_filter = ['admin', 'staff', 'active']

    fieldsets = (
        (
            None, {
                'fields': (
                    'full_name', 'email', 'last_login', 'password'
                )
            }
        ),
        # ('Personal info', {'fields': ()}),
        (
            'Permissions',
            {
                'fields': (
                    'admin', 'staff', 'active'
                )
            }
        ),
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (
            None,
            {
                'classes': (
                    'wide',
                ),
                'fields': (
                    'full_name', 'email', 'password1', 'password2'
                )
            }
        ),
    )


# Remove Group Model from admin. We're not using it.
admin.site.unregister(Group)

admin.site.register(Users, UserAdmin)

for model in MODELS:
    admin.site.register(model)

