from django.utils.translation import gettext as _
from django.core.mail import send_mail
from django.views.generic import TemplateView
from django.contrib.auth import get_user_model
from django.shortcuts import redirect, render
from django.http import HttpResponse

from core.forms import ContactForm

User = get_user_model()

# TODO:
# Foreign key = many-to-one
# 1. Embed EZ2Task OR find a free Heroku-like service (fly.io maybe?)
    # 1.1 Check links to authentication system. It needs to be igorsimb's allauth
    # 1.2 In urls.py - check all the links. Need to switch them to accounts/blabla urls (see igorsimb)
    # 1.3 Add all additional fields to User Model from ez2task to igorsimb
# 2. Embed Tortiki
# 3. Embed Blog

class IndexView(TemplateView):
    template_name = 'core/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = ContactForm(self.request.POST or None)
        context['form'] = form

        return context

    def post(self, request, *args, **kwargs):
        form = ContactForm(request.POST)
        context = self.get_context_data()
        data = request.POST
        if form.is_valid():
            name = data.get('name')
            email = data.get('email')
            subject = data.get('subject')
            message = data.get('message')

            str_msg = f'{message}\nSent by: {name} ({email})'

            send_mail(
                subject, str_msg,
                email, ['igor.simbirtsev@gmail.com'],
            )
            return redirect('index')
        else:
            HttpResponse(_('Something went wrong. Please try again.'))

        return render(request, 'core/index.html', context)