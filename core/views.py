from django.contrib import messages
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.utils.translation import gettext as _
from django.views.generic import TemplateView

from core.forms import ContactForm

User = get_user_model()


class IndexView(TemplateView):
    template_name = "core/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = ContactForm(self.request.POST or None)
        context["form"] = form

        return context

    def post(self, request, *args, **kwargs):
        form = ContactForm(request.POST)
        context = self.get_context_data()
        data = request.POST
        if form.is_valid():
            name = data.get("name")
            email = data.get("email")
            subject = data.get("subject")
            message = data.get("message")

            str_msg = f"{message}\nSent by: {name} ({email})"

            send_mail(
                subject,
                str_msg,
                email,
                ["igor.simbirtsev@gmail.com"],
            )

            messages.success(self.request, _("Email has been successfully sent"))
            return redirect("core:main")
        else:
            HttpResponse(_("Something went wrong. Please try again."))

        return render(request, "core/index.html", context)


class MPMonitorView(TemplateView):
    template_name = "core/projects/mp_monitor_project.html"


class Ez2TaskView(TemplateView):
    template_name = "core/projects/ez2task_project.html"


class StoreProjectView(TemplateView):
    template_name = "core/projects/store_project.html"
