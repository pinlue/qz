"""
URL configuration for qz project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/auth/", include("users_auth.urls")),
    path("api/v1/languages/", include("languages.urls")),
    path("api/v1/topics/", include("topics.urls")),
    path("api/v1/deepl/", include("integration.urls")),
    path("api/v1/folders/", include("folders.urls")),
    path("api/v1/", include("modules.urls")),

    # docs
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "swagger/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"
    ),
    path("redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),

    # debugging tool
    path("silk/", include("silk.urls", namespace="silk")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
