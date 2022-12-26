from django import forms
from django.utils.translation import gettext_lazy as _


class ContactForm(forms.Form):
    name = forms.CharField(label="_(Name)", required=True)
    email = forms.EmailField(label="_(Email)", required=True)
    subject = forms.CharField(label="_(Subject)", required=True)
    message = forms.CharField(label="_(Message)", widget=forms.Textarea())
