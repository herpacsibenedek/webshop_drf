from pprint import pprint
from copy import deepcopy
from decimal import Decimal, Context

from django.conf import settings
from django.urls import reverse
from djmoney.money import Money
from rest_framework.response import Response
from rest_framework import status
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory, APITestCase

from products.models import *
from products.api.serializers import *


class AttributeSerializerCreateTest(APITestCase):

    def test_attribute_create(self):
        """
        Test Attribute create
        """
        data = {
            "name": "Shoe Size"
        }

        serializer = AttributeSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        serializer.save()
        attr = Attribute.objects.first()
        self.assertEqual(attr.name, data['name'])

    def test_attribute_create_with_values(self):
        """Test attribute creation with values associated"""
        data = {
            "name": "Shoe Size",
            "values": [
                {
                    "name": "39",
                    "value": "39"
                },
                {
                    "name": "40",
                    "value": "40"
                },
                {
                    "name": "41",
                    "value": "41"
                }
            ]
        }

        serializer = AttributeSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        serializer.save()
        attr = Attribute.objects.first()
        av = AttributeValue.objects.all()
        self.assertEqual(attr.values.count(), len(av))


class AttributeSerializerUpdateTest(APITestCase):

    def setUp(self):
        self.attr = Attribute.objects.create(name="Shoe Size")
        AttributeValue.objects.create(name="39", value="39", attribute=self.attr)
        AttributeValue.objects.create(name="40", value="40", attribute=self.attr)
        another = Attribute.objects.create(name="Another Attribute")
        AttributeValue.objects.create(name="v1", value="v1", attribute=another)

        factory = APIRequestFactory()
        request = factory.get('/')
        self.serializer_context = {
            'request': Request(request),
        }
        serializer = AttributeSerializer(
            self.attr,
            context=self.serializer_context
        )

        self.data = serializer.data

    def test_attribute_update_name(self):
        """Test attribute update"""

        data = {
            "name": "Shirt Size"
        }

        serializer = AttributeSerializer(self.attr, data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        serializer.save()
        self.assertEqual(serializer.validated_data["name"], data["name"])

    def test_attribute_update_values(self):
        """Test attribute update, update values"""

        self.data['values'][0]['name'] = "Another Shoe Size"
        self.check_update_validity(data=self.data)

    def test_attribute_update_values_delete(self):
        """Test attribute update, delete values"""

        del self.data['values'][0]
        self.check_update_validity(data=self.data)

    def test_attribute_update_values_add(self):
        """Test attribute update, adding values"""

        self.data['values'].append({"name": "52", "value": "52"})
        self.check_update_validity(data=self.data, original_id=False)

    def check_update_validity(self, data, original_id=True):
        """
        Check given data is valid and has right values

        Original_id is checks if all of data have been
        associated with previously
        """

        serializer2 = AttributeSerializer(
            self.attr,
            context=self.serializer_context,
            data=data
        )
        self.assertTrue(serializer2.is_valid(), serializer2.errors)
        serializer2.save()

        av = AttributeValue.objects.all().filter(attribute=self.attr).count()
        self.assertEqual(len(serializer2.data['values']), av)
        if original_id:
            # Check values are the same thus it is not created again
            original_ids = [item.get('id') for item in self.data['values']]
            for value in serializer2.validated_data['values']:
                self.assertTrue(value.get('id') in original_ids)


class AttributeSerializerDeleteTest(APITestCase):

    def setUp(self):
        self.attr = Attribute.objects.create(name="Shoe Size")
        AttributeValue.objects.create(name="39", value="39", attribute=self.attr)
        AttributeValue.objects.create(name="40", value="40", attribute=self.attr)

    def test_attribute_delete(self):
        self.attr.delete()
        c_attr = Attribute.objects.count()
        c_value = AttributeValue.objects.count()
        self.assertEqual(c_attr, 0)
        self.assertEqual(c_value, 0)


class ProductTemplateSerializerCreateTest(APITestCase):

    def setUp(self):
        self.attr1 = Attribute.objects.create(id=1, name="Bottle Size")
        self.attr2 = Attribute.objects.create(id=2, name="ABV")
        self.attr3 = Attribute.objects.create(id=3, name="Brand")

    def test_template_create(self):
        """Test product template creation"""
        data = {
            "name": "Beer"
        }

        serializer = ProductTemplateSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        serializer.save()
        pt = ProductTemplate.objects.first()
        self.assertEqual(pt.name, data['name'])

    def test_template_create_with_attr_product(self):
        """
        Test product template creation,
        attribute product
        """
        data = {
            "name": "Beer",
            "product_attributes": [
                {"attribute_id": 2},
                {"attribute_id": 3}
            ]
        }

        serializer = ProductTemplateSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        serializer.save()

        pt = ProductTemplate.objects.first()
        ap = AttributeProduct.objects.filter(product_template=pt)
        self.assertEqual(ap.count(), len(data['product_attributes']))

    def test_template_create_with_attr_product_invalid(self):
        """
        Test product template creation,
        invalid attribute product id
        """
        data = {
            "name": "Beer",
            "product_attributes": [
                {"attribute_id": 20}
            ]
        }

        serializer = ProductTemplateSerializer(data=data)
        self.assertFalse(serializer.is_valid())

    def test_template_create_with_attr_variant(self):
        """
        Test product template creation,
        attribute variant
        """
        data = {
            "name": "Beer",
            "variant_attributes": [
                {"attribute_id": 2},
                {"attribute_id": 3}
            ]
        }

        serializer = ProductTemplateSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        serializer.save()

        pt = ProductTemplate.objects.first()
        ap = AttributeVariant.objects.filter(product_template=pt)
        self.assertEqual(ap.count(), len(data['variant_attributes']))

    def test_template_create_with_attr_variant_invalid(self):
        """
        Test product template creation,
        invalid attribute id
        """
        data = {
            "name": "Beer",
            "variant_attributes": [
                {"attribute_id": 20}
            ]
        }

        serializer = ProductTemplateSerializer(data=data)
        self.assertFalse(serializer.is_valid())


class ProductTemplateSerializerUpdateTest(APITestCase):

    def setUp(self):
        # Setup extra data
        pt_other = ProductTemplate.objects.create(name="Other")
        AttributeProduct.objects.create(
            attribute=Attribute.objects.create(name="Other"),
            product_template=pt_other
        )
        AttributeVariant.objects.create(
            attribute=Attribute.objects.create(name="Other2"),
            product_template=pt_other
        )

        # Setup data
        self.pt = ProductTemplate.objects.create(name="Beer")
        self.ap1 = AttributeProduct.objects.create(
            attribute=Attribute.objects.create(name="ABV"),
            product_template=self.pt
        )
        self.ap2 = AttributeProduct.objects.create(
            attribute=Attribute.objects.create(name="Brand"),
            product_template=self.pt
        )
        self.av = AttributeVariant.objects.create(
            attribute=Attribute.objects.create(name="Bottle Size"),
            product_template=self.pt
        )

        factory = APIRequestFactory()
        request = factory.get('/')
        self.serializer_context = {
            'request': Request(request),
        }
        serializer = ProductTemplateSerializer(
            self.pt,
            context=self.serializer_context
        )

        self.data = serializer.data

    def test_template_update_name(self):
        """
        Test ProductTemplate update
        name
        """
        data = {
            "name": "Wine"
        }

        serializer = ProductTemplateSerializer(self.pt, data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        serializer.save()
        self.assertEqual(self.pt.name, data["name"])

    def test_template_update_attr_product_delete(self):
        """
        Test ProductTemplate update
        delete a product attribute
        """

        del self.data['product_attributes'][0]
        self.check_update_product_validity(data=self.data)

    def test_template_update_attr_product_add(self):
        """
        Test ProductTemplate update
        aad a product attribute
        """

        self.data['product_attributes'].append({"attribute_id": 1})
        self.check_update_product_validity(data=self.data, original_id=False)

    def test_template_update_attr_variant_delete(self):
        """
        Test ProductTemplate update
        delete a variant attribute
        """

        del self.data['variant_attributes'][0]
        self.check_update_variant_validity(data=self.data)

    def test_template_update_attr_variant_add(self):
        """
        Test ProductTemplate update
        add a variant attribute
        """

        self.data['variant_attributes'].append({"attribute_id": 1})
        self.check_update_variant_validity(data=self.data, original_id=False)

    def check_update_product_validity(self, data, original_id=True):
        """
        Check given data is valid and has right values
        """

        serializer2 = ProductTemplateSerializer(
            self.pt,
            context=self.serializer_context,
            data=data
        )
        self.assertTrue(serializer2.is_valid(), serializer2.errors)
        serializer2.save()

        ap = AttributeProduct.objects.all().filter(product_template=self.pt).count()
        self.assertEqual(len(serializer2.validated_data['attribute_product']), ap)

        if original_id:
            # Check values are the same thus it is not created again
            original_ids = [item.get('id') for item in self.data['product_attributes']]
            for value in serializer2.validated_data['attribute_product']:
                self.assertTrue(value.get('id').id in original_ids)

    def check_update_variant_validity(self, data, original_id=True):
        """
        Check given data is valid and has right values
        """

        serializer2 = ProductTemplateSerializer(
            self.pt,
            context=self.serializer_context,
            data=data
        )
        self.assertTrue(serializer2.is_valid(), serializer2.errors)
        serializer2.save()

        ap = AttributeVariant.objects.all().filter(product_template=self.pt).count()
        self.assertEqual(len(serializer2.validated_data['attribute_variant']), ap)

        if original_id:
            # Check values are the same thus it is not created again
            original_ids = [item.get('id') for item in self.data['variant_attributes']]
            for value in serializer2.validated_data['attribute_variant']:
                self.assertTrue(value.get('id') in original_ids)


class ProductSerializerCreateTest(APITestCase):

    def setUp(self):
        self.pt = ProductTemplate.objects.create(name="Beer")
        self.data = {
            "name": "Modelo Especial",
            "product_template_id": self.pt.id
        }

    def setup_attributes(self):
        attr1 = Attribute.objects.create(name="ABV")
        attr2 = Attribute.objects.create(name="Brand")
        attr3 = Attribute.objects.create(name="Country of origin")

        AttributeValue.objects.create(
            attribute=attr1,
            name="5,2%",
            value="5.2%"
        )
        AttributeValue.objects.create(
            attribute=attr1,
            name="4.4%",
            value="4.4%"
        )
        AttributeValue.objects.create(
            attribute=attr2,
            name="Modelo",
            value="Modelo"
        )
        AttributeProduct.objects.create(
            attribute=attr1,
            product_template=self.pt
        )
        AttributeProduct.objects.create(
            attribute=attr2,
            product_template=self.pt
        )

    def setup_other_product_attr(self):
        pt = ProductTemplate.objects.create(name="Clothes")
        attr1 = Attribute.objects.create(name="Size")
        AttributeValue.objects.create(
            id=400,
            attribute=attr1,
            name="S",
            value="S"
        )
        AttributeProduct.objects.create(
            id=400,
            attribute=attr1,
            product_template=pt
        )

    def test_product_create(self):
        """
        Test Product create and test for its defaults
        """
        serializer = ProductSerializer(data=self.data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        serializer.save()
        p = Product.objects.first()
        self.assertEqual(p.name, self.data['name'])
        self.assertEqual(p.product_template, self.pt)

        # Check defaults
        self.assertEqual(p.description, None)
        self.assertFalse(p.active)
        self.assertEqual(p.min_price.amount, 0)
        self.assertEqual(p.min_price_currency, settings.DEFAULT_CURRENCY)

    def test_product_create_invalid_name_blank(self):
        """
        Test Product create with
        empty name
        """
        self.data.update({
            "name": ''
        })

        serializer = ProductSerializer(data=self.data)
        self.assertFalse(serializer.is_valid())

    def test_product_create_invalid_name_none(self):

        """
        Test Product create with
        name without value
        """
        self.data.update({
            "name": None
        })

        serializer = ProductSerializer(data=self.data)
        self.assertFalse(serializer.is_valid())

    def test_product_create_invalid_name_nmissing(self):
        """
        Test Product create with
        no name given
        """
        del self.data['name']

        serializer = ProductSerializer(data=self.data)
        self.assertFalse(serializer.is_valid())

    def test_product_create_invalid_template_id(self):
        """
        Test Product create with
        non existent product template id
        """
        self.data.update({
            "product_template_id": 3
        })

        serializer = ProductSerializer(data=self.data)
        self.assertFalse(serializer.is_valid())

    def test_product_create_invalid_template_None(self):
        """
        Test Product create with
        None value product template id
        """
        self.data.update({
            "product_template_id": None
        })

        serializer = ProductSerializer(data=self.data)
        self.assertFalse(serializer.is_valid())

    def test_product_create_description(self):
        """
        Test Product create with
        given description
        """
        self.data.update({
            "description": "Light easy-drinking beer from Mexico"
        })

        serializer = ProductSerializer(data=self.data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        serializer.save()
        p = Product.objects.first()
        self.assertEqual(p.description, self.data['description'])

    def test_product_create_active(self):
        """
        Test Product create with
        given active
        """
        self.data.update({
            "active": True
        })

        serializer = ProductSerializer(data=self.data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        serializer.save()
        p = Product.objects.first()
        self.assertTrue(p.active)

    def test_product_create_price_amount(self):
        """
        Test Product create with
        min price given
        """
        self.data.update({
            "min_price_amount": 10.15
        })

        serializer = ProductSerializer(data=self.data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        serializer.save()
        p = Product.objects.first()
        m = Money(
            amount=self.data['min_price_amount'],
            currency=settings.DEFAULT_CURRENCY
        )
        self.assertEqual(p.min_price, m)

    def test_product_create_price_amount_negative(self):
        """
        Test Product create with
        negative min price given
        """
        self.data.update({
            "min_price_amount": -10
        })

        serializer = ProductSerializer(data=self.data)
        self.assertFalse(serializer.is_valid())

    def test_product_create_price_currency(self):
        """
        Test Product create with
        both min price and price currency
        """
        self.data.update({
            "min_price_amount": 11.11,
            "min_price_currency": 'USD'
        })

        serializer = ProductSerializer(data=self.data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        serializer.save()
        p = Product.objects.first()
        m = Money(
            amount=self.data['min_price_amount'],
            currency=self.data['min_price_currency'],
        )
        self.assertEqual(p.min_price, m)

    def test_product_create_price_currency_blank(self):
        """
        Test Product create with
        both min price and blank price currency
        """
        self.data.update({
            "min_price_amount": 11.11,
            "min_price_currency": ''
        })

        serializer = ProductSerializer(data=self.data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        serializer.save()
        p = Product.objects.first()
        m = Money(
            amount=self.data['min_price_amount'],
            currency=settings.DEFAULT_CURRENCY
        )
        self.assertEqual(p.min_price, m)

    def test_product_create_price_currency_invalid(self):
        """
        Test Product create with
        invalid currency code given
        """
        self.data.update({
            "min_price_amount": 11.11,
            "min_price_currency": 'ASD'
        })

        serializer = ProductSerializer(data=self.data)
        self.assertFalse(serializer.is_valid())

    def test_product_create_price_currency_invalid_none(self):
        """
        Test Product create with
        min price and None value currency
        """
        self.data.update({
            "min_price_amount": 11.11,
            "min_price_currency": None
        })

        serializer = ProductSerializer(data=self.data)
        self.assertFalse(serializer.is_valid())

    def test_product_create_attribute(self):
        """
        Test Product create with
        product attribute given
        """
        self.setup_attributes()
        self.data.update({
            "product_attributes": [{
                "connection": 1,
                "value": 2,
            }]
        })

        serializer = ProductSerializer(data=self.data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        serializer.save()
        p = Product.objects.first()
        cpa = ConnectedProductAttribute.objects.first()
        self.assertEqual(p, cpa.product)
        self.assertEqual(
            p.product_template,
            cpa.connection.product_template
        )
        self.assertEqual(
            cpa.connection.product_template.id,
            self.data['product_template_id']
        )
        self.assertEqual(
            cpa.connection.id,
            self.data['product_attributes'][0]['connection']
        )
        self.assertEqual(
            cpa.value.id,
            self.data['product_attributes'][0]['value']
        )

    def test_product_create_attribute_missing_value(self):
        """
        Test Product create with
        product attribute given but
        no value
        """
        self.setup_attributes()
        self.data.update({
            "product_attributes": [{
                "connection": 1
            }]
        })

        serializer = ProductSerializer(data=self.data)
        self.assertFalse(serializer.is_valid())

    def test_product_create_attribute_missing_connection(self):
        """
        Test Product create with
        product attribute given but
        no connection
        """
        self.setup_attributes()
        self.data.update({
            "product_attributes": [{
                "value": 1
            }]
        })

        serializer = ProductSerializer(data=self.data)
        self.assertFalse(serializer.is_valid())

    def test_product_create_attribute_multiple(self):
        """
        Test Product create with
        product multiple attribute given
        """
        self.setup_attributes()
        self.data.update({
            "product_attributes": [
                {
                    "connection": 1,
                    "value": 2,
                },
                {
                    "connection": 2,
                    "value": 3,
                }]
        })

        serializer = ProductSerializer(data=self.data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        serializer.save()
        p = Product.objects.first()
        cpa = ConnectedProductAttribute.objects.all().filter(product=p)
        self.assertEqual(cpa.count(), 2)
        for i, item in enumerate(cpa):
            self.assertEqual(p, item.product)
            self.assertEqual(
                p.product_template,
                item.connection.product_template
            )
            self.assertEqual(
                item.connection.id,
                self.data['product_attributes'][i]['connection']
            )
            self.assertEqual(
                item.value.id,
                self.data['product_attributes'][i]['value']
            )

    def test_product_create_attribute_multiple_invalid_connection(self):
        """
        Test Product create with
        product attribute given but
        non existent connection
        """
        self.setup_attributes()
        self.data.update({
            "product_attributes": [
                {
                    "connection": 1,
                    "value": 2,
                },
                {
                    "connection": 3,
                    "value": 3,
                }]
        })

        serializer = ProductSerializer(data=self.data)
        self.assertFalse(serializer.is_valid())

    def test_product_create_attribute_multiple_invalid_connection_pt(self):
        """
        Test Product create with
        product attribute given but
        connection has another product template
        """
        self.setup_attributes()
        self.setup_other_product_attr()
        self.data.update({
            "product_attributes": [
                {
                    "connection": 1,
                    "value": 2,
                },
                {
                    "connection": 400,
                    "value": 400,
                }]
        })

        serializer = ProductSerializer(data=self.data)
        self.assertFalse(serializer.is_valid())

    def test_product_create_attribute_multiple_invalid_connection_duplicate(self):
        """
        Test Product create with
        product attribute given but
        connection duplicate
        """
        self.setup_attributes()
        self.data.update({
            "product_attributes": [
                {
                    "connection": 1,
                    "value": 2,
                },
                {
                    "connection": 1,
                    "value": 3,
                }]
        })

        serializer = ProductSerializer(data=self.data)
        self.assertFalse(serializer.is_valid())

    def test_product_create_attribute_multiple_invalid_value(self):
        """
        Test Product create with
        product attribute given but
        non existent value
        """
        self.setup_attributes()
        self.data.update({
            "product_attributes": [
                {
                    "connection": 1,
                    "value": 2,
                },
                {
                    "connection": 2,
                    "value": 30,
                }]
        })

        serializer = ProductSerializer(data=self.data)
        self.assertFalse(serializer.is_valid())

    def test_product_create_attribute_multiple_invalid_value_attribute(self):
        """
        Test Product create with
        product attribute given but
        value's attribute is different form
        connection's one
        """
        self.setup_attributes()
        self.data.update({
            "product_attributes": [
                {
                    "connection": 1,
                    "value": 2,
                },
                {
                    "connection": 2,
                    "value": 2,
                }]
        })

        serializer = ProductSerializer(data=self.data)
        self.assertFalse(serializer.is_valid())


class ProductSerializerUpdateTest(APITestCase):

    def setUp(self):
        self.pt = ProductTemplate.objects.create(name="Beer")
        self.p = Product.objects.create(
            name='Modelo Especial',
            description="It is a beer.",
            product_template_id=self.pt.id,
            min_price=Money(
                amount=12.12,
                currency='USD'
            )
        )

        factory = APIRequestFactory()
        request = factory.get('/')
        self.serializer_context = {
            'request': Request(request),
        }
        serializer = ProductSerializer(
            self.p,
            context=self.serializer_context
        )

        self.data = serializer.data

    def setup_attributes(self):
        attr1 = Attribute.objects.create(name="ABV")
        attr2 = Attribute.objects.create(name="Brand")

        # Settting first CPA
        AttributeValue.objects.create(
            attribute=attr1,
            name="5,2%",
            value="5.2%"
        )
        av1 = AttributeValue.objects.create(
            attribute=attr1,
            name="4.4%",
            value="4.4%"
        )
        ap1 = AttributeProduct.objects.create(
            attribute=attr1,
            product_template=self.pt
        )
        ConnectedProductAttribute.objects.create(
            product=self.p,
            connection=ap1,
            value=av1
        )
        # Setting second CPA
        av2 = AttributeValue.objects.create(
            attribute=attr2,
            name="Modelo",
            value="Modelo"
        )
        ap2 = AttributeProduct.objects.create(
            attribute=attr2,
            product_template=self.pt
        )
        ConnectedProductAttribute.objects.create(
            product=self.p,
            connection=ap2,
            value=av2
        )
        # Add all these data to our serializer
        serializer = ProductSerializer(
            self.p,
            context=self.serializer_context
        )
        self.data = serializer.data

    def setup_other_product(self):
        pt = ProductTemplate.objects.create(name="Clothes")
        p = Product.objects.create(
            name="Other Product",
            product_template=pt
        )
        attr1 = Attribute.objects.create(name="Size")
        av1 = AttributeValue.objects.create(
            id=400,
            attribute=attr1,
            name="S",
            value="S"
        )
        ap = AttributeProduct.objects.create(
            id=400,
            attribute=attr1,
            product_template=pt
        )
        ConnectedProductAttribute.objects.create(
            product=p,
            connection=ap,
            value=av1
        )

    def product_update(self, data, fail=False):
        """
        Serialize product with given data,
        check if its suppose to fail or not
        """
        serializer = ProductSerializer(self.p, data=data)
        if not fail:
            self.assertTrue(serializer.is_valid(), serializer.errors)
            serializer.save()
        else:
            self.assertFalse(serializer.is_valid())

        return serializer

    def test_product_update_name(self):
        """
        Test Product update,
        name change
        """

        self.data['name'] = "Not Bear"

        serializer = self.product_update(self.data)
        self.assertEqual(self.p.name, self.data['name'])

    def test_product_update_name_missing(self):
        """
        Test Product update,
        with no name given
        """

        name = self.data['name']
        del self.data['name']

        serializer = self.product_update(self.data)
        self.assertEqual(self.p.name, name)

    def test_product_update_description(self):
        """
        Test Product update,
        description change
        """

        self.data['description'] = "Its Not Bear, its a BEER"

        serializer = self.product_update(self.data)
        self.assertEqual(self.p.description, self.data['description'])

    def test_product_update_description_missing(self):
        """
        Test Product update,
        with no description given
        """

        description = self.data['description']
        del self.data['description']

        serializer = self.product_update(self.data)
        self.assertEqual(self.p.description, description)

    def test_product_update_active(self):
        """
        Test Product update,
        active change
        """
        self.data['active'] = True
        serializer = self.product_update(self.data)
        self.assertTrue(self.p.active)

        del self.data['active']
        serializer = self.product_update(self.data)
        self.assertTrue(self.p.active)

        self.data['active'] = False
        serializer = self.product_update(self.data)
        self.assertFalse(self.p.active)

        del self.data['active']
        serializer = self.product_update(self.data)
        self.assertFalse(self.p.active)

    def test_product_update_template(self):
        """
        Test Product update,
        template change
        """
        self.setup_other_product()  # another product template id=2
        pt = self.p.product_template.id
        self.data['product_template_id'] = 2

        serializer = self.product_update(self.data)
        self.assertEqual(self.p.product_template.id, pt)

    def test_product_update_minprice(self):
        """
        Test Product update,
        min price amount and currency
        """
        self.data['min_price_amount'] = 10.19
        self.data['min_price_currency'] = 'EUR'

        serializer = self.product_update(self.data)

        self.assertEqual(
            float(self.p.min_price.amount),
            float(self.data['min_price_amount'])
        )
        self.assertEqual(
            self.p.min_price_currency,
            self.data['min_price_currency']
        )

    def test_product_update_minprice_negative(self):
        """
        Test Product update,
        negative min price
        """
        self.data['min_price_amount'] = -10.19

        serializer = self.product_update(self.data, fail=True)

    def test_product_update_minprice_four_places(self):
        """
        Test Product update,
        min price validity
        with 4 decimal places
        """
        self.data['min_price_amount'] = 10.1908
        self.data['min_price_currency'] = 'EUR'

        serializer = self.product_update(self.data)

        self.assertEqual(
            float(self.p.min_price.amount),
            float(self.data['min_price_amount'])
        )
        self.assertEqual(
            self.p.min_price_currency,
            self.data['min_price_currency']
        )

    def test_product_update_minprice_moredecimalplaces(self):
        """
        Test Product update,
        min price validity with
        more than 4 decimal places
        """
        self.data['min_price_amount'] = 10.100959
        self.data['min_price_currency'] = 'EUR'

        serializer = self.product_update(self.data, fail=True)

    def test_product_update_minprice_amount_only(self):
        """
        Test Product update,
        change amount only
        """
        self.data['min_price_amount'] = 10.10

        serializer = self.product_update(self.data)

        self.assertEqual(
            float(self.p.min_price.amount),
            float(self.data['min_price_amount'])
        )
        self.assertEqual(
            self.p.min_price_currency,
            self.data['min_price_currency']
        )

    def test_product_update_minprice_currency_only(self):
        """
        Test Product update,
        change currency only
        """

        min_price = self.data['min_price_amount']
        del self.data['min_price_amount']
        self.data['min_price_currency'] = 'EUR'

        serializer = self.product_update(self.data)
        self.assertEqual(
            float(self.p.min_price.amount),
            float(min_price)
        )
        self.assertEqual(
            self.p.min_price_currency,
            self.data['min_price_currency']
        )

    def test_product_update_minprice_currency_invalid(self):
        """
        Test Product update,
        change currency to an invalid currency code
        """
        self.data['min_price_currency'] = 'ASD'

        serializer = self.product_update(self.data, fail=True)

    def test_product_update_minprice_currency_blank(self):
        """
        Test Product update,
        currency blank
        """
        self.data['min_price_currency'] = ''

        serializer = self.product_update(self.data)

        self.assertEqual(
            self.p.min_price_currency,
            settings.DEFAULT_CURRENCY
        )

    def test_product_update_minprice_currency_none(self):
        """
        Test Product update,
        currency none
        """
        self.data['min_price_currency'] = None

        serializer = self.product_update(self.data, fail=True)

    def test_product_update_attr_add(self):
        """
        Test Product update,
        product attribute addition
        """
        attr = Attribute.objects.create(name="Country of origin")
        av = AttributeValue.objects.create(
            id=200,
            attribute=attr,
            name="Mexico",
            value="Mexico"
        )
        ap = AttributeProduct.objects.create(
            id=200,
            attribute=attr,
            product_template=self.pt
        )

        self.setup_attributes()
        self.data['product_attributes'].append(
            {
                "connection": 200,
                "value": 200
            }
        )

        serializer = self.product_update(self.data)
        self.check_attributes_validity(self.data, original_id=False)

    def test_product_update_attr_add_invalid_connection(self):
        """
        Test Product update,
        product attribute addition
        connection is for another product template
        """
        self.setup_attributes()
        self.setup_other_product()
        self.data['product_attributes'].append(
            {
                "connection": 400,
                "value": 400
            }
        )

        serializer = self.product_update(self.data, fail=True)

    def test_product_update_attr_add_invalid_value(self):
        """
        Test Product update,
        product attribute addition
        value is not associated with connection
        """
        self.setup_attributes()
        self.setup_other_product()
        self.data['product_attributes'].append(
            {
                "connection": 200,
                "value": 400
            }
        )

        serializer = self.product_update(self.data, fail=True)

    def test_product_update_attr_delete(self):
        """
        Test Product update,
        product attribute delete
        """

        self.setup_attributes()
        serializer = self.product_update(self.data)

        del self.data['product_attributes'][0]

        self.check_attributes_validity(self.data)

    def check_attributes_validity(self, data, original_id=True):
        """
        Check given data is valid and has right values
        """

        serializer2 = ProductSerializer(
            self.p,
            context=self.serializer_context,
            data=data
        )
        self.assertTrue(serializer2.is_valid(), serializer2.errors)
        serializer2.save()
        cpa = ConnectedProductAttribute.objects.all().filter(product=self.p).count()
        self.assertEqual(len(serializer2.validated_data['attributes']), cpa)

        if original_id:
            # Check values are the same thus it is not created again
            original_ids = [item.get('id') for item in self.data['product_attributes']]
            for value in serializer2.validated_data['attributes']:
                self.assertTrue(value['connection'].id in original_ids)


class ProductVariantSerializerCreateTest(APITestCase):

    def setUp(self):
        self.pt = ProductTemplate.objects.create(name="Beer")
        self.p = Product.objects.create(
            name='Modelo Especial',
            description="It is a beer.",
            product_template_id=self.pt.id,
            min_price=Money(
                amount=12.12,
                currency='USD'
            )
        )
        self.data = {
            "name": "Modelo Especial - 330ml",
            "product_id": 1
        }

    def variant_create(self, data, fail=False):
        """
        Serialize variant with given data,
        check if its suppose to fail or not
        """
        serializer = ProductVariantSerializer(data=data)
        if not fail:
            self.assertTrue(serializer.is_valid(), serializer.errors)
            serializer.save()
        else:
            self.assertFalse(serializer.is_valid())

        return serializer

    def setup_attributes(self):
        attr1 = Attribute.objects.create(name="Bottle Size")
        AttributeValue.objects.create(
            attribute=attr1,
            name="330 ml",
            value="330 ml"
        )
        AttributeValue.objects.create(
            attribute=attr1,
            name="500 ml",
            value="500 ml"
        )
        AttributeVariant.objects.create(
            attribute=attr1,
            product_template=self.pt
        )

        attr2 = Attribute.objects.create(name="Modelo beer types")
        AttributeValue.objects.create(
            attribute=attr2,
            name="Modelo Especial",
            value="Modelo Especial"
        )
        AttributeValue.objects.create(
            attribute=attr2,
            name="Modelo Negra",
            value="Modelo Negra"
        )
        AttributeVariant.objects.create(
            attribute=attr2,
            product_template=self.pt
        )
        # Invalid option
        attr3 = Attribute.objects.create(name="Invalid")
        AttributeValue.objects.create(
            attribute=attr3,
            name="Invalid",
            value="Invalid"
        )
        AttributeVariant.objects.create(
            attribute=attr3,
            product_template=ProductTemplate.objects.create(name="Invalid")
        )

    def test_variant_create(self):
        """
        Test Variant create
        """
        self.variant_create(self.data)
        v = ProductVariant.objects.first()
        self.assertEqual(self.data['product_id'], v.product.id)
        self.assertEqual(self.data['name'], v.name)
        self.assertFalse(v.active)

    def test_variant_create_no_name(self):
        """
        Test Variant create,
        with no given name
        """
        data = {
            "product_id": 1
        }

        serializer = ProductVariantSerializer(data=data)
        self.assertFalse(serializer.is_valid())

    def test_variant_create_no_p_id(self):
        """
        Test Variant create,
        with no given product id
        """
        data = {
            "name": "Modelo Especial - 330ml"
        }

        serializer = ProductVariantSerializer(data=data)
        self.assertFalse(serializer.is_valid())

    def test_variant_create_active(self):
        """
        Test Variant create,
        with active
        """
        self.data['active'] = True

        self.variant_create(self.data)

        v = ProductVariant.objects.first()
        self.assertTrue(v.active)

    def test_variant_create_price(self):
        """
        Test Variant create,
        both price and currency
        """
        self.data['price_amount'] = 99.99
        self.data['price_currency'] = 'USD'

        self.variant_create(self.data)
        v = ProductVariant.objects.first()
        self.assertEqual(
            float(v.price.amount),
            float(self.data['price_amount'])
        )
        self.assertEqual(
            v.price_currency,
            self.data['price_currency']
        )

    def test_variant_create_price_only(self):
        """
        Test Variant create,
        price only
        """
        self.data['price_amount'] = 99.99

        self.variant_create(self.data)
        v = ProductVariant.objects.first()
        self.assertEqual(
            float(v.price.amount),
            float(self.data['price_amount'])
        )
        self.assertEqual(
            v.price_currency,
            settings.DEFAULT_CURRENCY
        )

    def test_variant_create_price_negative(self):
        """
        Test Variant create,
        price negative
        """
        self.data['price_amount'] = -99.99

        self.variant_create(self.data, fail=True)

    def test_variant_create_price_currency_invalid(self):
        """
        Test Variant create,
        currency invalid code
        """
        self.data['price_amount'] = 99.99
        self.data['price_currency'] = "ASD"

        self.variant_create(self.data, fail=True)

    def test_variant_create_attributes(self):
        """
        Test Variant create,
        variant attribute create
        """
        self.setup_attributes()
        self.data['variant_attributes'] = [
            {
                'connection': 1,
                'value': 1
            }
        ]
        self.variant_create(self.data)

        variant = ProductVariant.objects.first()
        cva = ConnectedVariantAttribute.objects.first()
        self.assertEqual(variant, cva.variant)
        self.assertEqual(
            variant.product.product_template,
            cva.connection.product_template
        )
        self.assertEqual(
            cva.connection.id,
            self.data['variant_attributes'][0]['connection']
        )
        self.assertEqual(
            cva.value.id,
            self.data['variant_attributes'][0]['value']
        )

    def test_variant_create_attributes_multiple(self):
        """
        Test Variant create,
        variant attribute create multiple
        """
        self.setup_attributes()
        self.data['variant_attributes'] = [
            {
                'connection': 1,
                'value': 1
            },
            {
                'connection': 2,
                'value': 3
            }
        ]
        self.variant_create(self.data)

        variant = ProductVariant.objects.first()
        cva = ConnectedVariantAttribute.objects.filter(variant=variant)
        self.assertEqual(cva.count(), 2)
        for i, item in enumerate(cva):
            self.assertEqual(variant, item.variant)
            self.assertEqual(
                variant.product.product_template,
                item.connection.product_template
            )
            self.assertEqual(
                item.connection.id,
                self.data['variant_attributes'][i]['connection']
            )
            self.assertEqual(
                item.value.id,
                self.data['variant_attributes'][i]['value']
            )

    def test_variant_create_attributes_invalid_connection(self):
        """
        Test Variant create,
        variant attribute create,
        connection not associated with variant
        """
        self.setup_attributes()
        self.data['variant_attributes'] = [
            {
                'connection': 3,
                'value': 5
            }
        ]
        self.variant_create(self.data, fail=True)

    def test_variant_create_attributes_invalid_value(self):
        """
        Test Variant create,
        variant attribute create,
        connoction's attribute and
        value's attribute are different
        """
        self.setup_attributes()
        self.data['variant_attributes'] = [
            {
                'connection': 1,
                'value': 3
            }
        ]
        self.variant_create(self.data, fail=True)


class ProductVariantSerializerUpdateTest(APITestCase):

    def setUp(self):
        self.pt = ProductTemplate.objects.create(name="Beer")
        self.p = Product.objects.create(
            name='Modelo Especial',
            description="It is a beer.",
            product_template=self.pt,
            min_price=Money(
                amount=3.12,
                currency='USD'
            )
        )
        self.v = ProductVariant.objects.create(
            name="Modelo Especial - 330ml",
            product=self.p,
        )

        factory = APIRequestFactory()
        request = factory.get('/')
        self.serializer_context = {
            'request': Request(request),
        }
        serializer = ProductVariantSerializer(
            self.v,
            context=self.serializer_context
        )
        self.data = serializer.data

    def setup_price(self):
        self.data['price_amount'] = 850
        self.data['price_currency'] = 'USD'

    def setup_attributes(self):
        attr1 = Attribute.objects.create(name="Bottle Size")
        value1 = AttributeValue.objects.create(
            attribute=attr1,
            name="330 ml",
            value="330 ml"
        )
        av1 = AttributeVariant.objects.create(
            attribute=attr1,
            product_template=self.pt
        )
        ConnectedVariantAttribute.objects.create(
            variant=self.v,
            connection=av1,
            value=value1
        )

        attr2 = Attribute.objects.create(name="Modelo beer types")
        value2 = AttributeValue.objects.create(
            attribute=attr2,
            name="Modelo Especial",
            value="Modelo Especial"
        )
        AttributeValue.objects.create(
            id=202,
            attribute=attr2,
            name="Modelo Negra",
            value="Modelo Negra"
        )
        av2 = AttributeVariant.objects.create(
            attribute=attr2,
            product_template=self.pt
        )
        ConnectedVariantAttribute.objects.create(
            variant=self.v,
            connection=av2,
            value=value2
        )
        # Add all these data to our serializer
        serializer = ProductVariantSerializer(
            self.v,
            context=self.serializer_context
        )
        self.data = serializer.data

    def variant_update(self, data, fail=False):
        """
        Serialize variant with given data,
        check if its suppose to fail or not
        """
        serializer = ProductVariantSerializer(self.v, data=data)
        if not fail:
            self.assertTrue(serializer.is_valid(), serializer.errors)
            serializer.save()
        else:
            self.assertFalse(serializer.is_valid())

        return serializer

    def test_variant_change_name(self):
        """
        Test variant update,
        name changed
        """
        self.data['name'] = "Not a Corona Beer"

        self.variant_update(self.data)
        self.assertEqual(self.v.name, self.data['name'])

    def test_variant_change_product_id(self):
        """
        Test variant update,
        product_id changed
        """
        self.data['product_id'] = 2

        self.variant_update(self.data, fail=True)

    def test_variant_change_price(self):
        """
        Test variant update,
        change price and curency
        """
        self.setup_price()
        self.variant_update(self.data)

        self.assertEqual(self.v.price_currency, self.data['price_currency'])
        self.assertEqual(self.v.price.amount, self.data['price_amount'])

    def test_variant_change_price_amount(self):
        """
        Test variant update,
        change price amount
        """
        self.setup_price()
        self.variant_update(self.data)

        self.data['price_amount'] = 1850
        self.variant_update(self.data)

        self.assertEqual(self.v.price_currency, self.data['price_currency'])
        self.assertEqual(self.v.price.amount, self.data['price_amount'])

    def test_variant_change_price_currency(self):
        """
        Test variant update,
        change currency only
        """
        self.setup_price()
        self.variant_update(self.data)

        self.data['price_currency'] = "GBP"
        self.variant_update(self.data)

        self.assertEqual(self.v.price.amount, self.data['price_amount'])
        self.assertEqual(self.v.price_currency, self.data['price_currency'])

    def test_variant_change_attribute_add(self):
        """
        Test variant update,
        add variant attribute
        """
        attr = Attribute.objects.create(name="Shape of bottle")
        avalue = AttributeValue.objects.create(
            id=2000,
            attribute=attr,
            name="Mexico",
            value="Mexico"
        )
        avariant = AttributeVariant.objects.create(
            id=2000,
            attribute=attr,
            product_template=self.pt
        )

        self.setup_attributes()
        self.data['variant_attributes'].append(
            {
                "connection": 2000,
                "value": 2000
            }
        )

        serializer = self.variant_update(self.data)
        self.check_attributes_validity(self.data, original_id=False)

    def test_variant_change_attribute_delete(self):
        """
        Test variant update,
        delete variant attribute
        """
        self.setup_attributes()
        del self.data['variant_attributes'][0]

        serializer = self.variant_update(self.data)
        self.check_attributes_validity(self.data, original_id=True)

    def test_variant_change_attribute_modify(self):
        """
        Test variant update,
        modify value of variant attribute
        """
        self.setup_attributes()
        self.data['variant_attributes'][1]['value'] = 202

        serializer = self.variant_update(self.data)
        self.check_attributes_validity(self.data, original_id=True)
        self.assertTrue(ConnectedVariantAttribute.objects
            .filter(
                variant=self.v,
                value=202
            ).exists()
        )

    def check_attributes_validity(self, data, original_id=True):
        """
        Check given data is valid and has right values
        """

        serializer = self.variant_update(data=data)
        cva = ConnectedVariantAttribute.objects.all().filter(variant=self.v).count()
        self.assertEqual(len(serializer.validated_data['attributes']), cva)

        if original_id:
            # Check values are the same thus it is not created again
            original_ids = [item.get('id') for item in self.data['variant_attributes']]
            for value in serializer.validated_data['attributes']:
                self.assertTrue(value['connection'].id in original_ids)
