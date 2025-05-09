from django.contrib import admin
from django.urls import path, include
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

# Swagger Schema View
schema_view = get_schema_view(
   openapi.Info(
      title="API Documentation",
      default_version='v1',
      description="API documentation for the Customer Service API",
      contact=openapi.Contact(email="dimatata01@gmail.com"),
      license=openapi.License(name="Derick Ingairo"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,), 
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),  #app's URLs
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),  # Swagger UI
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),  # ReDoc UI
]
