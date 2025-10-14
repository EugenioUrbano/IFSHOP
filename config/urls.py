from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic import RedirectView
from django.urls import path, include

urlpatterns = [
    path("", include("ifshop.urls")),
    path('admin/login/', RedirectView.as_view(url='/registration/login/', query_string=True)),
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),  # URLs do allauth
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)