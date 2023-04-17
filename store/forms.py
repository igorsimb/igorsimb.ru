from django import forms


class ContactForm(forms.Form):
    name = forms.CharField(label="Name", required=True, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'ФИО',
        'name': 'name',
        'id': 'name',
    }))
    email = forms.EmailField(label="Email", required=True, widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'Email',
        'name': 'name',
        'id': 'email'
    }))
    subject = forms.CharField(label="Subject", required=True, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Заголовок',
        'name': 'subject',
        'id': 'subject',
    }))
    message = forms.CharField(label="Message)", widget=forms.Textarea(attrs={
        'class': 'form-control',
        'placeholder': 'Сообщение',
        'name': 'message',
        'id': 'message',
    }))


# https://medium.com/analytics-vidhya/how-to-create-fully-functional-e-commerce-website-with-django-7205d250e76f
# We can do if user.is_authenticated, use this, else - use existing on on checkout.html
class OrderCreateForm(forms.Form):
    name = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'id': 'name',
        'name': 'name',
    }))
    phone_number = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': '(905) 123-45-67',
        'x-mask:': '(999) 999-99-99',
        'id': 'phone',
    }))
    address = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'id': 'address',
    }))
    zipcode = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'maxlength': '6',
        'id': 'zipcode',
    }))
    city = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'id': 'city',
    }))
