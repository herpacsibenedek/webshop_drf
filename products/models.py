from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from djmoney.models.fields import MoneyField, CurrencyField
from djmoney.models.validators import MinMoneyValidator


from .managers import *
from webshop_drf.utils import unique_random_string_generator


class ProductTemplate(models.Model):
    """
    Container model for a product template
    which used for grouping together products.
    """
    name = models.CharField(max_length=255)
    slug = models.SlugField(blank=True, unique=True)
    has_variants = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Product(models.Model):
    """
    Container model for a product
    which stores information common to all of its variations.
    """
    name = models.CharField(max_length=255)
    slug = models.SlugField(blank=True, unique=True)
    description = models.TextField(blank=True)

    product_template = models.ForeignKey(
        ProductTemplate,
        related_name="products",
        on_delete=models.CASCADE
    )
    price = MoneyField(
        max_digits=19,
        decimal_places=4,
        validators=[
            MinMoneyValidator(0),
        ]
    )
    """There is an CurrencyField named 'price_currency'
    associated with price field which stores a choice of currency"""
    active = models.BooleanField(default=False)
    created = models.DateTimeField(editable=False, default=timezone.now)
    modified = models.DateTimeField(default=timezone.now)

    objects = ProductManager()

    def save(self, *args, **kwargs):
        """
        Update timestamps.
        """
        if not self.id:
            self.created = timezone.now()
        self.modified = timezone.now()
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class ProductVariant(models.Model):
    """
    Container model for a product variant
    which stores information specific to a product variation.
    This is a sellable item.
    """
    name = models.CharField(max_length=255)
    slug = models.SlugField(blank=True, unique=True)
    product = models.ForeignKey(
        Product,
        related_name="variants",
        on_delete=models.CASCADE
    )
    price = MoneyField(
        max_digits=19,
        decimal_places=4,
        null=True,
        validators=[
            MinMoneyValidator(0),
        ]
    )
    active = models.BooleanField(default=False)
    created = models.DateTimeField(editable=False, default=timezone.now)
    modified = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        """
        Update timestamps.
        """
        if not self.id:
            self.created = timezone.now()
        self.modified = timezone.now()
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class AttributeProduct(models.Model):
    """
    Junction model
    which uniquely connects a product template to an attribute.
    This is used to specify which attributes can be taken by
    a product (through product template)
    """
    attribute = models.ForeignKey(
        "Attribute",
        related_name="attribute_product",
        on_delete=models.CASCADE
    )
    product_template = models.ForeignKey(
        ProductTemplate,
        related_name="attribute_product",
        on_delete=models.CASCADE
    )

    connected_products = models.ManyToManyField(
        Product,
        blank=True,
        through="ConnectedProductAttribute",
        through_fields=("connection", "product"),
        related_name="attributesrelated",
    )

    class Meta:
        unique_together = ('attribute', 'product_template',)


class AttributeVariant(models.Model):
    """
    Junction model
    which uniquely connects a product template to an attribute.
    This is used to specify which attributes can be taken by
    a product variant (through product template)
    """
    attribute = models.ForeignKey(
        "Attribute",
        related_name="attribute_variant",
        on_delete=models.CASCADE
    )
    product_template = models.ForeignKey(
        ProductTemplate,
        related_name="attribute_variant",
        on_delete=models.CASCADE
    )

    connected_variants = models.ManyToManyField(
        ProductVariant,
        blank=True,
        through="ConnectedVariantAttribute",
        through_fields=("connection", "variant"),
        related_name="attributesrelated",
    )

    class Meta:
        unique_together = ('attribute', 'product_template',)


class Attribute(models.Model):
    """
    Container model for an attribute.
    """
    name = models.CharField(max_length=255)
    slug = models.SlugField(blank=True, unique=True)

    def __str__(self):
        return self.name


class AttributeValue(models.Model):
    """
    Container model for a value
    which belongs to an attribute.
    """
    name = models.CharField(max_length=255)
    value = models.CharField(max_length=100)
    attribute = models.ForeignKey(
        Attribute,
        related_name="values",
        on_delete=models.CASCADE
    )

    def __str__(self):
        return self.name


class AbstractConnectedAttribute(models.Model):
    """
    Abstract model which stores an attribute value
    which specific product thou
    """
    connection = None
    value = models.ForeignKey(
        AttributeValue,
        on_delete=models.CASCADE
    )

    class Meta:
        abstract = True


class ConnectedProductAttribute(AbstractConnectedAttribute):
    """
    """
    product = models.ForeignKey(
        Product,
        related_name="attributes",
        on_delete=models.CASCADE
    )

    connection = models.ForeignKey(
        AttributeProduct,
        related_name="connectedattributes",
        on_delete=models.CASCADE
    )

    class Meta:
        unique_together = ('product', 'connection',)


class ConnectedVariantAttribute(AbstractConnectedAttribute):
    """
    """
    variant = models.ForeignKey(
        ProductVariant,
        related_name="attributes",
        on_delete=models.CASCADE
    )

    connection = models.ForeignKey(
        AttributeVariant,
        related_name="connectedattributes",
        on_delete=models.CASCADE
    )

    class Meta:
        unique_together = ('variant', 'connection',)


@ receiver(pre_save, sender=ProductTemplate)
@ receiver(pre_save, sender=Product)
@ receiver(pre_save, sender=ProductVariant)
@ receiver(pre_save, sender=Attribute)
def slug_pre_save(sender, instance, *args, **kwargs):
    """
    Create a slug
    """
    if not instance.slug:
        instance.slug = unique_random_string_generator(instance, size=10)
