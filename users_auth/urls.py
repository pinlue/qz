from django.urls import path, include

from users_auth.views import EmailChangeView, EmailVerifyView

urlpatterns = [
    path('registration/', include('dj_rest_auth.registration.urls')),
    path('email/change/', EmailChangeView.as_view(), name='email-change'),
    path('email/verify/', EmailVerifyView.as_view(), name='email-verify'),

    #ToDo OAuth2 integration google, facebook, github

    path('', include('dj_rest_auth.urls')),
]