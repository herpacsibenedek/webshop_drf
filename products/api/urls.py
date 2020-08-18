from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'attributes', views.AttributeViewSet)
router.register(r'attributesproducts', views.AttributeProductViewSet)
router.register(r'attributevalues', views.AttributeValueViewSet)
router.register(r'attributevariants', views.AttributeVariantViewSet)
router.register(r'connectedproductattribute', views.ConnectedProductAttributeViewSet)
router.register(r'products', views.ProductViewSet)
router.register(r'producttemplates', views.ProductTemplateViewSet)
router.register(r'productvariants', views.ProductVariantViewSet)

# The API URLs are now determined automatically by the router.
urlpatterns = [
    path('', include(router.urls)),
]
