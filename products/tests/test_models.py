from time import sleep

from django.test import TestCase
from django.utils import timezone
from djmoney.money import Money

from ..models import *


class ProductTemplateTest(TestCase):
    """
    Test module For ProductTemplate model
    """

    def setUp(self):
        ProductTemplate.objects.create(
            name="Beer"
        )

    def test_slug(self):
        a = ProductTemplate.objects.get(name="Beer")
        self.assertNotEqual(a.slug, None)

    def test_name(self):
        a = ProductTemplate.objects.get(name="Beer")
        self.assertEqual(str(a), "Beer")


class ProductTest(TestCase):
    """
    Test module For Product model
    """

    def setUp(self):
        pt = ProductTemplate.objects.create(
            name="Beer"
        )
        self.now_before = timezone.now()
        Product.objects.create(
            name="Shipyard's American Pale Ale",
            description="An easy drinking hoppy ale.",
            product_template=pt,
            min_price=Money(1200, 'HUF')
        )
        self.now_after = timezone.now()

    def test_slug(self):
        p = Product.objects.get(name="Shipyard's American Pale Ale")
        self.assertNotEqual(p.slug, None)

    def test_name(self):
        p = Product.objects.get(name="Shipyard's American Pale Ale")
        self.assertEqual(str(p), "Shipyard's American Pale Ale")

    def test_created(self):
        p = Product.objects.get(name="Shipyard's American Pale Ale")
        self.assertTrue(self.now_before <= p.created)
        self.assertTrue(p.created <= self.now_after)

    def test_created_not_change(self):
        p = Product.objects.get(name="Shipyard's American Pale Ale")
        original = p.created
        sleep(0.001)
        p.save()
        self.assertEqual(original, p.created)

    def test_modified(self):
        p = Product.objects.get(name="Shipyard's American Pale Ale")
        self.assertTrue(self.now_before <= p.modified)
        self.assertTrue(p.modified <= self.now_after)

    def test_modified_changed(self):
        p = Product.objects.get(name="Shipyard's American Pale Ale")
        original = p.modified
        sleep(0.001)
        p.save()
        self.assertTrue(original < p.modified)


class ProductVariantTest(TestCase):
    """
    Test module For ProductVariant model
    """

    def setUp(self):
        pt = ProductTemplate.objects.create(
            name="Beer"
        )
        p = Product.objects.create(
            name="Shipyard's American Pale Ale",
            description="An easy drinking hoppy ale.",
            product_template=pt,
            min_price=Money(1200, 'USD')
        )
        self.now_before = timezone.now()
        ProductVariant.objects.create(
            name="Shipyard's American Pale Ale - 330ml",
            product=p,
        )
        self.now_after = timezone.now()

    def test_slug(self):
        p = ProductVariant.objects.get(
            name="Shipyard's American Pale Ale - 330ml"
        )
        self.assertNotEqual(p.slug, None)

    def test_name(self):
        p = ProductVariant.objects.get(
            name="Shipyard's American Pale Ale - 330ml"
        )
        self.assertEqual(
            str(p),
            "Shipyard's American Pale Ale - 330ml"
        )

    def test_created(self):
        p = ProductVariant.objects.get(
            name="Shipyard's American Pale Ale - 330ml"
        )
        self.assertTrue(self.now_before <= p.created)
        self.assertTrue(p.created <= self.now_after)

    def test_created_not_change(self):
        p = ProductVariant.objects.get(
            name="Shipyard's American Pale Ale - 330ml"
        )
        original = p.created
        sleep(0.001)
        p.save()
        self.assertEqual(original, p.created)

    def test_modified(self):
        p = ProductVariant.objects.get(
            name="Shipyard's American Pale Ale - 330ml"
        )
        self.assertTrue(self.now_before <= p.modified)
        self.assertTrue(p.modified <= self.now_after)

    def test_modified_changed(self):
        p = ProductVariant.objects.get(
            name="Shipyard's American Pale Ale - 330ml"
        )
        original = p.modified
        sleep(0.001)
        p.save()
        self.assertTrue(original < p.modified)


class AttributeTest(TestCase):
    """
    Test module For Attribute model
    """

    def setUp(self):
        Attribute.objects.create(
            name="ABV"
        )

    def test_slug(self):
        a = Attribute.objects.get(name="ABV")
        self.assertNotEqual(a.slug, None)

    def test_name(self):
        a = Attribute.objects.get(name="ABV")
        self.assertEqual(str(a), "ABV")


class AttributeValueTest(TestCase):
    """
    Test module For AttributeValue model
    """

    def setUp(self):
        a = Attribute.objects.create(
            name="ABV"
        )
        AttributeValue.objects.create(
            name="5.2%",
            value="5.2%",
            attribute=a
        )

    def test_name(self):
        a = AttributeValue.objects.get(name="5.2%")
        self.assertEqual(str(a), "5.2%")
