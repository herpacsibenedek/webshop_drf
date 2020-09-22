from decimal import Decimal
from pprint import pprint

from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from djmoney.money import Money
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
    values = AttributeValueSerializer(
        many=True,
        required=False
    )

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
        for item in validated_data.get('values', []):
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

        # If there is no supplied values then do nothing with it
        if validated_data.get('values'):
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
    id = serializers.PrimaryKeyRelatedField(
        queryset=AttributeProduct.objects.all(),
        required=False
    )
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
        model = AttributeProduct
        fields = ['id', 'attribute_id', 'title', 'url']


class AttributeVariantSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=AttributeVariant.objects.all(),
        required=False
    )
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
        fields = ['id', 'attribute_id', 'title', 'url']


class ProductTemplateSerializer(serializers.HyperlinkedModelSerializer):
    product_attributes = AttributeProductSerializer(
        source='attribute_product',
        many=True,
        required=False
    )
    variant_attributes = AttributeVariantSerializer(
        source='attribute_variant',
        many=True,
        required=False
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
        if validated_data.get('attribute_product'):
            for item in validated_data['attribute_product']:
                AttributeProduct.objects.create(
                    attribute=Attribute(item['attribute']['id']),
                    product_template=template
                )

        # Create each AttributeProduct instance
        if validated_data.get('attribute_variant'):
            for item in validated_data['attribute_variant']:
                AttributeVariant.objects.create(
                    attribute=Attribute(item['attribute']['id']),
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
                               attr_all=instance.attribute_variant.all())

        return instance

    def update_attributes(self, instance, validated_data, field_name, attr_model, attr_all):
        if validated_data.get(field_name) is not None:
            # 1. create a list of ids out of passed data
            ids = [item['attribute']['id'] for item in validated_data[field_name]]

            # 2. delete any association
            # which is not included in passed data
            for item in attr_all:
                if item.attribute_id not in ids:
                    item.delete()

            # 3. create or update all association
            for item in validated_data[field_name]:
                if item.get('id'):
                    attr = attr_model(
                        id=item.get('id').id,
                        product_template=instance,
                        attribute=Attribute(item['attribute']['id'])
                    )
                else:
                    attr = attr_model(
                        product_template=instance,
                        attribute=Attribute(item['attribute']['id'])
                    )
                attr.save()

        return instance

    def validate_product_attributes(self, data):
        self.check_if_valid_attribute(data)
        return data

    def validate_variant_attributes(self, data):
        self.check_if_valid_attribute(data)
        return data

    def check_if_valid_attribute(self, data):
        for item in data:
            if item.get('attribute'):
                if not Attribute.objects.filter(
                    id=item['attribute']['id']
                ).exists():
                    raise serializers.ValidationError(
                        _("No attribute with given ID can be found")
                    )


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
    id = serializers.IntegerField(
        required=False
    )

    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        source='product.id',
        write_only=True,
        required=False  # required for create only
    )
    variant_attributes = ConnectedVariantAttributeSerializer(
        source='attributes',
        many=True,
        required=False
    )
    price_currency = serializers.CharField(
        required=False,
        allow_blank=True,
    )
    price_amount = serializers.DecimalField(
        source='price.amount',
        max_digits=19,
        decimal_places=4,
        required=False,
        default=None,
        allow_null=True,
    )

    class Meta:
        model = ProductVariant
        fields = ['id', 'name', 'slug', 'price_amount', 'price_currency',
                  'active', 'created', 'modified', 'url',
                  'product', 'product_id', 'variant_attributes']
        read_only_fields = ['created', 'modified', 'product', 'slug']
        ordering = ['-id']

    def create(self, validated_data):
        variant = ProductVariant(
            name=validated_data['name'],
            product=validated_data['product']['id'],
            active=validated_data.get('active', False)
        )
        if validated_data['price'].get('amount'):
            variant.price = Money(
                amount=validated_data['price'].get('amount', Decimal(0.0)),
                currency=validated_data.get('price_currency', settings.DEFAULT_CURRENCY),
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
        instance.active = validated_data.get('active', instance.active)

        if validated_data.get('price'):
            if validated_data['price'].get('amount'):
                instance.price = Money(
                    amount=validated_data['price']['amount'],
                    currency=validated_data.get('price_currency', instance.price_currency),
                )
            elif validated_data.get('price_currency'):
                instance.price = Money(
                    amount=instance.price.amount,
                    currency=validated_data['price_currency'],
                )

        instance.save()

        if validated_data.get('attributes'):
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

    def validate(self, data):
        if not data.get('product'):
            self.validate_product_id(data=None)

        if self.instance:
            pt_id = self.instance.product.product_template
        else:
            pt_id = data['product']['id'].product_template

        # check correctness of ConnectedVariantAttribute
        for attr in data.get('attributes', []):
            if pt_id != attr['connection'].product_template:
                raise serializers.ValidationError(_("ProductTemplate is not same."))
            if attr['value'].attribute != attr['connection'].attribute:
                raise serializers.ValidationError(_("Attribute is not same."))
        return data

    def validate_price_currency(self, data):
        if data and data not in (cc := [str(x[0]) for x in settings.CURRENCY_CHOICES]):
            raise serializers.ValidationError(
                _(f"Currency({data}) is not one of the permitted values: {', '.join(cc)}")
            )
        else:
            return data

    def validate_price_amount(self, data):
        if data and data < 0:
            raise serializers.ValidationError(
                _(f"Price cannot be negative")
            )
        return data

    def validate_product_id(self, data):
        if not data:
            if not self.instance:
                raise serializers.ValidationError(
                    _(f"Name must be set.")
                )
        return data


class ProductSerializer(serializers.HyperlinkedModelSerializer):
    name = serializers.CharField(
        required=False
    )
    product_template_id = serializers.PrimaryKeyRelatedField(
        queryset=ProductTemplate.objects.all(),
        source='product_template.id'
    )
    product_attributes = ConnectedProductAttributeSerializer(
        source='attributes',
        many=True,
        required=False
    )
    product_variants = ProductVariantSerializer(
        source='variants',
        many=True,
        required=False
    )

    min_price_currency = serializers.CharField(
        required=False,
        allow_blank=True
    )
    min_price_amount = serializers.DecimalField(
        source='min_price.amount',
        max_digits=19,
        decimal_places=4,
        required=False,
        default=0,
        allow_null=True,
    )

    class Meta:
        model = Product
        fields = ['id', 'name', 'slug',
                  'product_template', 'description',
                  'min_price_amount', 'min_price_currency', 'active',
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
        product = Product(
            name=validated_data['name'],
            product_template=validated_data['product_template']['id'],
            description=validated_data.get('description'),
            active=validated_data.get('active', False)
        )
        if validated_data['min_price'].get('amount'):
            product.min_price = Money(
                amount=validated_data['min_price'].get('amount', Decimal(0.0)),
                currency=validated_data.get('min_price_currency', settings.DEFAULT_CURRENCY),
            )
        product.save()

        # Create each ConnectedProductAttribute instance associated with it
        for item in validated_data.get('attributes', []):
            ConnectedProductAttribute.objects.create(
                product=product,
                connection=item['connection'],
                value=item['value']
            )
        # # Fully working, commented for make structure easier
        # # by allowing variants created only at one location
        # # Create each Variant instance associated with it
        # for item in validated_data.get('variants', []):
        #     variant = ProductVariant(
        #         name=item['name'],
        #         product=product,
        #         active=item.get('active', False)
        #     )
        #     if item.get('price'):
        #         if item['price'].get('amount'):
        #             variant.price = Money(
        #                 amount=item['price'].get('amount', Decimal(0.0)),
        #                 currency=item.get('price_currency', settings.DEFAULT_CURRENCY),
        #             )
        #     variant.save()

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
        instance.description = validated_data.get('description', instance.description)
        instance.active = validated_data.get('active', instance.active)
        if validated_data.get('min_price'):
            if validated_data['min_price'].get('amount'):
                instance.min_price = Money(
                    amount=validated_data['min_price'].get('amount', instance.min_price.amount),
                    currency=validated_data.get('min_price_currency', instance.min_price_currency),
                )
            elif validated_data.get('min_price_currency'):
                instance.min_price = Money(
                    amount=instance.min_price.amount,
                    currency=validated_data['min_price_currency'],
                )
        instance.save()

        if validated_data.get('attributes'):
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

        # # Fully working, see above at create
        # # ProductVariant
        # # 1. create a list of ids out of passed data
        # variants_ids = [item.get('id') for item in validated_data['variants']]

        # # 2. delete any association
        # # which is not included in passed data
        # for variant in instance.variants.all():
        #     if variant.id not in variants_ids:
        #         variant.delete()

        # # 3. create or update all association
        # for item in validated_data['variants']:
        #     variant = ProductVariant(
        #         id=item.get('id'),
        #         name=item['name'],
        #         product=instance,
        #         active=item.get('active', False)
        #     )
        #     if item.get('price'):
        #         if item['price'].get('amount'):
        #             variant.price = Money(
        #                 amount=item['price']['amount'],
        #                 currency=item.get('price_currency', settings.DEFAULT_CURRENCY),
        #             )
        #     elif item.get('price_currency'):
        #         variant.price = Money(
        #             amount=variant.price.amount,
        #             currency=item['price_currency'],
        #         )
        #     variant.save()

        return instance

    def validate(self, data):
        # Check if name set if not run validator
        if not data.get('name'):
            self.validate_name(data=None)

        # check correctness of ConnectedProductAttribute
        for attr in data.get('attributes', []):
            if data['product_template']['id'] != attr['connection'].product_template:
                raise serializers.ValidationError(_("ProductTemplate is not same."))
            if attr['value'].attribute != attr['connection'].attribute:
                raise serializers.ValidationError(_("Attribute is not same."))
        return data

    def validate_min_price_currency(self, data):
        if not data:
            data = settings.DEFAULT_CURRENCY
        if data not in (cc := [str(x[0]) for x in settings.CURRENCY_CHOICES]):
            raise serializers.ValidationError(
                _(f"Currency({data}) is not one of the permitted values: {', '.join(cc)}")
            )
        else:
            return data

    def validate_min_price_amount(self, data):
        if data and data < 0:
            raise serializers.ValidationError(
                _(f"Price cannot be negative")
            )
        return data

    def validate_name(self, data):
        if not data:
            if self.instance:
                data = self.instance.name
            else:
                raise serializers.ValidationError(
                    _(f"Name must be set.")
                )
        return data
