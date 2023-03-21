from django.urls import path
from django.contrib.auth import views as auth_views

from store_users.views import logout_view, registration_view, CustomLoginForm

urlpatterns = [
    # next_page "index" = store_users/index.html
    path('store/login/', auth_views.LoginView.as_view(template_name='users/login.html',
                                                   authentication_form=CustomLoginForm,
                                                redirect_authenticated_user=True, next_page='index'), name='login'),
    path('store/logout/', logout_view, name='logout'),  # store_users/logout.html
    path('store/register/', registration_view, name='register'),
    path('store/password-reset/',
         auth_views.PasswordResetView.as_view(template_name='users/password_reset.html'),
         name='password_reset'),
    path('store/password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='users/password_reset_done.html'), name='password_reset_done'),
    path('store/password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='users/password_reset_confirm.html'), name='password_reset_confirm'),
    path('store/password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='users/password_reset_complete.html'), name='password_reset_complete'),
]
