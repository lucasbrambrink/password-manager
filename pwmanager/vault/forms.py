from django import forms


class LoginForm(forms.ModelForm):
    username = forms.CharField(label=u'Username', max_length=255)
    password = forms.PasswordInput()
