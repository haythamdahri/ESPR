from django.urls import path,re_path
from django.conf.urls import include,url
from . import views
from django.contrib.auth import views as auth_views

app_name = "main_app"

urlpatterns = [
    path('test/', views.test, name='test'),
    path('home/', views.home, name='home'),

    path('signup/', views.signup, name='signup'),
    path('confirm_email/<int:id_user>/<str:token_email>/', views.confirm_email_signup, name='confirm_email_signup'),#traitement pour confirmer un email via le lien envoyé par mail
    path('login/', views.log_in, name='log_in'),
    path('logout/', views.log_out, name='log_out'),
    path('confirm_mail/resend/', views.confirm_mail_resend, name='confirm_mail_resend'),# renvoyer un autre mail de confirmation
    path('contactus/', views.contactus, name='contactus'),

    # Views pour reset password
    path('reset-password/', views.password_reset, name='password_reset'),
    path('reset-password/done/', auth_views.password_reset_done,
        {'template_name': 'authentification/reset_password_done_ESPR.html/'},name='password_reset_done'),
    re_path('reset-password/confirm/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$', auth_views.password_reset_confirm,
        {'template_name': 'authentification/reset_password_confirm_ESPR.html',
         'post_reset_redirect': 'main_app:password_reset_complete'}, name='password_reset_confirm'),
    path('reset-password/complete/', auth_views.password_reset_complete,
        {'template_name': 'authentification/reset_password_complete_ESPR.html'}, name='password_reset_complete'),

    path('', views.home, name='home'),
]