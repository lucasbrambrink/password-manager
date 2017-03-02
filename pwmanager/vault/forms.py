from django import forms
from .models import VaultUser


class LoginForm(forms.ModelForm):
    email = forms.CharField(max_length=255,
                            widget=forms.TextInput(attrs={
                                'placeholder': 'Email',
                                'data-validate': 'required,email'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password', 'data-validate': 'required'}))

    class Meta:
        model = VaultUser
        fields = [u'email', u'password']


class RegistrationForm(forms.ModelForm):
    email = forms.CharField(max_length=255,
                            widget=forms.TextInput(attrs={
                                'placeholder': 'Email',
                            'data-validate': 'required,email'}))
    username = forms.CharField(max_length=255,
                               widget=forms.TextInput(attrs={'placeholder': 'Username',
                                                             'data-validate': 'required'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password',
                                                                 'data-validate': 'required'}),
                               max_length=255)

    class Meta:
        model = VaultUser
        fields = [u'email', u'username', u'password']
