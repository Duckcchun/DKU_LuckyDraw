"""URL configuration for lottoproject."""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('lotto.urls_accounts')),
    path('', include('lotto.urls')),
]
