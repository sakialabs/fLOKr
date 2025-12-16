"""
URL configuration for flokr project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    
    # API endpoints
    path('api/auth/', include('users.urls')),
    path('api/inventory/', include('inventory.urls')),
    path('api/reservations/', include('reservations.urls')),
    path('api/hubs/', include('hubs.urls')),
    path('api/community/', include('community.urls')),
    path('api/partners/', include('partners.urls')),
    path('api/ori/', include('ori_ai.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
