from django.urls import path, include

from users_auth.views import (
    EmailChangeView,
    EmailVerifyView,
    GitHubLoginView,
    GoogleLoginView,
)

urlpatterns = [
    path('registration/', include('dj_rest_auth.registration.urls')),
    path('email/change/', EmailChangeView.as_view(), name='email-change'),
    path('email/verify/', EmailVerifyView.as_view(), name='email-verify'),

    path('login/github/callback/', GitHubLoginView.as_view(), name='github_login'),
    path('login/google/callback/', GoogleLoginView.as_view(), name='google_login'),

    path("accounts/", include("allauth.urls")),

    path('', include('dj_rest_auth.urls')),
]