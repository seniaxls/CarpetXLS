from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('', admin.site.urls),
    path('payroll/', include('payroll.urls')),  # Include payroll URLs here
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)