from django.contrib import admin
from django.urls import path, include
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Swagger Schema View
schema_view = get_schema_view(
   openapi.Info(
      title="API Documentation",
      default_version='v1',
      description="API documentation for the Customer and Order endpoints",
      terms_of_service="https://www.yourapi.com/terms/",
      contact=openapi.Contact(email="contact@yourapi.com"),
      license=openapi.License(name="MIT License"),
   ),
   public=True,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),  # Your app's URLs
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),  # Swagger UI
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),  # ReDoc UI
]
