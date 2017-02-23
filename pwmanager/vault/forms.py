from django import forms
from .models import VaultUser


class LoginForm(forms.ModelForm):
    email = forms.CharField(max_length=255,
                            widget=forms.TextInput(attrs={'placeholder': 'Email', 'name': ''}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))

    class Meta:
        model = VaultUser
        fields = [u'email', u'password']


class RegistrationForm(forms.ModelForm):
    email = forms.CharField(max_length=255,
                            widget=forms.TextInput(attrs={
                                'placeholder': 'Email'}))
    username = forms.CharField(max_length=255,
                               widget=forms.TextInput(attrs={'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password'}),
                               max_length=255)

    class Meta:
        model = VaultUser
        fields = [u'email', u'username', u'password']
