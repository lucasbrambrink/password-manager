from django import forms
from .models import VaultUser


class LoginForm(forms.ModelForm):
    email = forms.CharField(label=u'Email', max_length=255)
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = VaultUser
        fields = [u'email', u'password']


class RegistrationForm(forms.ModelForm):
    email = forms.CharField(label='Email', max_length=255)
    username = forms.CharField(label=u'Username', max_length=255)
    password = forms.CharField(label=u'Password', widget=forms.PasswordInput(), max_length=255)

    class Meta:
        model = VaultUser
        fields = [u'email', u'username', u'password']
