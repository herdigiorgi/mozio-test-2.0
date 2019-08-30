from django.contrib import admin
from django.conf.urls import include
from django.urls import path
from rest_framework.routers import DefaultRouter as RESTRouter
from rest_framework import permissions
from mozio.views import ProviderViewSet, ServiceViewSet
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


schema_view = get_schema_view(
   openapi.Info(
      title="API Documentation",
      default_version='v1',
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

router = RESTRouter()
router.register(r'provider', ProviderViewSet)
router.register(r'service', ServiceViewSet)

urlpatterns = [
    path('', schema_view.with_ui('swagger', cache_timeout=0), name='schema-redoc'),
    path('', include(router.urls)),
    path('admin/', admin.site.urls),
]
