from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect
from environs import Env

from django.contrib.auth import login, authenticate, logout
from store_users.forms import RegisterForm

env = Env()
env.read_env()


def logout_view(request):
    logout(request)
    return redirect('index')


class CustomLoginForm(AuthenticationForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': 'Email'}
        )
        self.fields['password'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': 'Пароль'}
        )


def registration_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            email = form.cleaned_data.get('email')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(email=email, password=raw_password)
            login(request, user)
            return redirect('index')
    else:
        form = RegisterForm()

    context = {'form': form}
    return render(request, 'users/register.html', context)


def demo_user_login_view(request):
    demo_user = authenticate(email=env('DEMO_ADMIN_LOGIN'), password=env('DEMO_ADMIN_PASSWORD'))
    login(request, demo_user)
    return redirect('index')
