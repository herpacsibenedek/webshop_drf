from pprint import pprint

from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from ..models import *
from .fields import AttributeHIField, ConnectedAttributeHIField


class AttributeValueSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)

    class Meta:
        model = AttributeValue
        fields = ['id', 'name', 'value', ]
        ordering = ['-id']


class AttributeSerializer(serializers.HyperlinkedModelSerializer):
    values = AttributeValueSerializer(many=True)

    class Meta:
        model = Attribute
        fields = ['id', 'name', 'slug', 'url', 'values']
        read_only_fields = ['slug']
        ordering = ['-id']

    def create(self, validated_data):
        """
        Create the Attribute instance and create AttributeValue(s)
        associated with it
        """

        # Create the Attribute instance
        attribute = Attribute.objects.create(
            name=validated_data['name']
        )

        # Create each AttributeValue instance
        for item in validated_data['values']:
            AttributeValue.objects.create(
                name=item['name'],
                value=item['value'],
                attribute=attribute)

        return attribute

    def update(self, instance, validated_data):
        """
        Update the Attribute instance and update/create
        AttributeValue(s) associated with it and delete
        unwanted AttributeValue(s).
        """

        # Update the Attribute instance
        instance.name = validated_data.get('name', instance.name)
        instance.save()

        # Delete any AttributeValue not included in the request
        value_ids = [item.get('id') for item in validated_data['values']]
        for value in instance.values.all():
            if value.id not in value_ids:
                value.delete()

        # Create or update AttributeValue instances that are in the request
        for item in validated_data['values']:
            value = AttributeValue(
                id=item.get('id'),
                name=item['name'],
                value=item['value'],
                attribute=instance)
            value.save()

        return instance


class AttributeProductSerializer(serializers.ModelSerializer):
    name = serializers.CharField(
        source='attribute.name',
        read_only=True,
    )
    url = AttributeHIField(
        view_name='attribute-detail',
        read_only=True,
    )

    class Meta:
        model = AttributeProduct
        fields = ['id', 'attribute', 'name', 'url']


class AttributeVariantSerializer(serializers.ModelSerializer):
    attribute_id = serializers.IntegerField(source='attribute.id')
    title = serializers.CharField(
        source='attribute.name',
        required=False,
    )
    url = AttributeHIField(
        view_name='attribute-detail',
        read_only=True,
    )

    class Meta:
        model = AttributeVariant
        fields = ['attribute_id', 'title', 'url']


class ProductTemplateSerializer(serializers.HyperlinkedModelSerializer):
    product_attributes = AttributeProductSerializer(
        source='attribute_product',
        many=True
    )
    variant_attributes = AttributeVariantSerializer(
        source='attribute_variant',
        many=True
    )

    class Meta:
        model = ProductTemplate
        fields = ['id', 'name', 'slug', 'url',
                  'product_attributes', 'variant_attributes', 'slug']
        ordering = ['-id']

    def create(self, validated_data):
        """
        Create the ProductTemplate instance and create
        association with attribute(s) which connect to its
        Products and Varriants associated with
        ProductTemplate itself
        """

        # Create the Attribute instance
        # Creates an instance regardless errors happen later
        template = ProductTemplate.objects.create(
            name=validated_data['name']
        )

        # Create each AttributeProduct instance
        for item in validated_data['attribute_product']:
            AttributeProduct.objects.create(
                # validation needed for Foreign key not exist error
                attribute=item['attribute'],
                product_template=template
            )

        # Create each AttributeProduct instance
        for item in validated_data['attribute_variant']:
            AttributeVariant.objects.create(
                # validation needed for Foreign key not exist error
                attribute=item['attribute'],
                product_template=template
            )

        return template

    def update(self, instance, validated_data):
        """
        Update the ProductTemplate instance and update/create
        association with attribute(s) which connect to its
        Products and Varriants associated with
        ProductTemplate itself and delete
        unwanted connections.
        """

        # Update the Attribute instance
        instance.name = validated_data.get('name', instance.name)
        instance.slug = validated_data.get('slug', instance.slug)
        instance.save()

        # Update AttributeProduct
        self.update_attributes(instance, validated_data,
                               field_name="attribute_product",
                               attr_model=AttributeProduct,
                               attr_all=instance.attribute_product.all())

        # Update AttributeVariant
        self.update_attributes(instance, validated_data,
                               field_name="attribute_variant",
                               attr_model=AttributeVariant,
                               attr_all=instance.attribute_variant.all()
                               )

        return instance

    def update_attributes(self, instance, validated_data,
                          field_name, attr_model, attr_all):
        # Delete any AttributeProduct/AttributeVariant not included in the request
        ap_ids = [item.get('id') for item in validated_data[field_name]]
        for item in attr_all:
            if item.id not in ap_ids:
                item.delete()

        # Create or update AttributeProduct/AttributeVariant
        # instances that are in the request
        for item in validated_data[field_name]:
            ap = attr_model(
                id=item.get('id'),
                # validation needed for Foreign key not exist error
                attribute=item['attribute'],
                product_template=instance
            )
            ap.save()

        # Return if there was an error
        return instance


class ConnectedProductAttributeSerializer(serializers.ModelSerializer):
    url = ConnectedAttributeHIField(
        view_name='attribute-detail',
        read_only=True,
    )

    class Meta:
        model = ConnectedProductAttribute
        fields = ['id', 'connection', 'value', 'url']


class ConnectedVariantAttributeSerializer(serializers.ModelSerializer):
    url = ConnectedAttributeHIField(
        view_name='attribute-detail',
        read_only=True,
    )

    class Meta:
        model = ConnectedVariantAttribute
        fields = ['id', 'connection', 'value', 'url']


class ProductVariantSerializer(serializers.HyperlinkedModelSerializer):
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        source='product.id',
        write_only=True
    )
    variant_attributes = ConnectedVariantAttributeSerializer(
        source='attributes',
        many=True,
        required=False
    )

    class Meta:
        model = ProductVariant
        fields = ['id', 'name', 'slug', 'price',
                  'active', 'created', 'modified', 'url', 'product', 'product_id', 'variant_attributes']
        read_only_fields = ['created', 'modified', 'product', 'slug']
        ordering = ['-id']

    def create(self, validated_data):

        variant = ProductVariant(
            name=validated_data['name'],
            product=validated_data['product']['id'],
            price=validated_data.get('price', None),
            active=validated_data.get('active', False)
        )
        variant.save()

        # Create each ConnectedVariantAttribute instance associated with it
        for item in validated_data.get('attributes', []):
            ConnectedVariantAttribute.objects.create(
                variant=variant,
                connection=item['connection'],
                value=item['value']
            )

        return variant

    def update(self, instance, validated_data):
        """
        """

        instance.name = validated_data.get('name', instance.name)
        instance.price = validated_data.get('price', instance.price)
        instance.active = validated_data.get('active', instance.active)
        instance.save()

        # ConnectedVariantAttribute
        # 1. create a list of ids out of passed data
        attributes_ids = [item.get('id') for item in validated_data['attributes']]

        # 2. delete any association
        # which is not included in passed data
        for attribute in instance.attributes.all():
            if attribute.id not in attributes_ids:
                attribute.delete()

        # 3. create or update all association
        for item in validated_data['attributes']:
            attribute = ConnectedVariantAttribute(
                id=item.get('id'),
                variant=instance,
                connection=item['connection'],
                value=item['value']
            )
            attribute.save()

        return instance


class ProductVariantSerializerForProduct(serializers.HyperlinkedModelSerializer):
    id = serializers.IntegerField(required=False)

    class Meta:
        model = ProductVariant
        fields = ['id', 'name', 'slug', 'price',
                  'active', 'url', 'product']
        read_only_fields = ['created', 'modified', 'product', 'slug']


class ProductSerializer(serializers.HyperlinkedModelSerializer):
    product_template_id = serializers.PrimaryKeyRelatedField(
        queryset=ProductTemplate.objects.all(),
        source='product_template.id'
    )
    product_attributes = ConnectedProductAttributeSerializer(
        source='attributes',
        many=True,
        required=False
    )
    product_variants = ProductVariantSerializerForProduct(
        source='variants',
        many=True,
        required=False
    )

    class Meta:
        model = Product
        fields = ['id', 'name', 'slug',
                  'product_template', 'description', 'price', 'active',
                  'created', 'modified', 'url',
                  'product_attributes',
                  'product_variants',
                  'product_template_id']
        read_only_fields = ['created', 'modified', 'product_template', 'slug']
        ordering = ['-id']

    def create(self, validated_data):
        """
        Create the Product instance and
        its connectedProductAttribute
        """

        # Create the Attribute instance
        product = Product.objects.create(
            name=validated_data['name'],
            product_template=validated_data['product_template']['id'],
            price=validated_data.get('price', 0),
            active=validated_data.get('active', False)
        )

        # Create each ConnectedProductAttribute instance associated with it
        for item in validated_data.get('attributes', []):
            ConnectedProductAttribute.objects.create(
                product=product,
                connection=item['connection'],
                value=item['value']
            )

        # Create each Variant instance associated with it
        for item in validated_data.get('variants', []):
            ProductVariant.objects.create(
                name=item['name'],
                product=product,
                price=item.get('price', None),
                active=item.get('active', False)
            )

        return product

    def update(self, instance, validated_data):
        """
        Update the Attribute instance and update/create
        AttributeValue(s) associated with it and delete
        unwanted AttributeValue(s).
        Product Template cannot be changed.
        """

        # Update the Product instance
        instance.name = validated_data.get('name', instance.name)
        instance.price = validated_data.get('price', instance.price)
        instance.active = validated_data.get('active', instance.active)
        instance.save()

        # ConnectedProductAttribute
        # 1. create a list of ids out of passed data
        attributes_ids = [item.get('id') for item in validated_data['attributes']]

        # 2. delete any association
        # which is not included in passed data
        for attribute in instance.attributes.all():
            if attribute.id not in attributes_ids:
                attribute.delete()

        # 3. create or update all association
        for item in validated_data['attributes']:
            attribute = ConnectedProductAttribute(
                id=item.get('id'),
                product=instance,
                connection=item['connection'],
                value=item['value']
            )
            attribute.save()

        # ProductVariant
        # 1. create a list of ids out of passed data
        variants_ids = [item.get('id') for item in validated_data['variants']]

        # 2. delete any association
        # which is not included in passed data
        for variant in instance.variants.all():
            if variant.id not in variants_ids:
                variant.delete()

        # 3. create or update all association
        for item in validated_data['variants']:
            variant = ProductVariant(
                id=item.get('id'),
                name=item['name'],
                product=instance,
                price=item.get('price', None),
                active=item.get('active', False)
            )
            variant.save()

        return instance

    def validate(self, data):
        # check correctness of ConnectedProductAttribute
        for attr in data.get('attributes', []):
            if data['product_template']['id'] != attr['connection'].product_template:
                raise serializers.ValidationError(_("ProductTemplate is not same."))
            if attr['value'].attribute != attr['connection'].attribute:
                raise serializers.ValidationError(_("Attribute is not same."))
        return data
