from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django.forms import EmailInput, TextInput, PasswordInput

User = get_user_model()


class RegisterForm(UserCreationForm):
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(
            attrs={'class': 'form-control', 'type': 'password', 'align': 'center', 'placeholder': 'Пароль'}),
    )
    password2 = forms.CharField(
        label="Confirm password",
        widget=forms.PasswordInput(
            attrs={'class': 'form-control', 'type': 'password', 'align': 'center', 'placeholder': 'Подтверждение пароля'}),
    )

    class Meta:
        model = User
        fields = ('email', 'name', 'password1', 'password2')

        widgets = {
            'email': EmailInput(attrs={
                'class': "form-control",
                'placeholder': 'Email'
            }),
            'name': TextInput(attrs={
                'class': "form-control",
                'placeholder': 'Имя'
            })
        }
