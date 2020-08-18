from rest_framework import serializers


from ..models import Attribute, AttributeProduct, AttributeValue, AttributeVariant, ConnectedProductAttribute, Product, ProductTemplate, ProductVariant


class AttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attribute
        fields = '__all__'


class AttributeProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttributeProduct
        fields = '__all__'


class AttributeValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttributeValue
        fields = '__all__'


class AttributeVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttributeVariant
        fields = '__all__'


class ConnectedProductAttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConnectedProductAttribute
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'


class ProductTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductTemplate
        fields = '__all__'


class ProductVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariant
        fields = '__all__'
