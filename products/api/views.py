from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from .serializers import *
from ..models import *


class AttributeViewSet(viewsets.ModelViewSet):
    queryset = Attribute.objects.all()
    serializer_class = AttributeSerializer


class AttributeProductViewSet(viewsets.ModelViewSet):
    queryset = AttributeProduct.objects.all()
    serializer_class = AttributeProductSerializer


class AttributeValueViewSet(viewsets.ModelViewSet):
    queryset = AttributeValue.objects.all()
    serializer_class = AttributeValueSerializer


class AttributeVariantViewSet(viewsets.ModelViewSet):
    queryset = AttributeVariant.objects.all()
    serializer_class = AttributeVariantSerializer


class ConnectedProductAttributeViewSet(viewsets.ModelViewSet):
    queryset = ConnectedProductAttribute.objects.all()
    serializer_class = ConnectedProductAttributeSerializer


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class ProductTemplateViewSet(viewsets.ModelViewSet):
    queryset = ProductTemplate.objects.all()
    serializer_class = ProductTemplateSerializer


class ProductVariantViewSet(viewsets.ModelViewSet):
    queryset = ProductVariant.objects.all()
    serializer_class = ProductVariantSerializer
