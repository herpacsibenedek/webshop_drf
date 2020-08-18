from django.core.validators import MaxValueValidator
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import m2m_changed, post_save
from django.dispatch import receiver
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _


from .managers import ProductManager


class ProductTemplate(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, allow_unicode=True)
    has_variants = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Product(models.Model):
    """
    Container model for a product which stores information common to all of its variations.
    """
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, allow_unicode=True)
    description = models.TextField(blank=True)

    product_template = models.ForeignKey(
        ProductTemplate,
        related_name="products",
        on_delete=models.CASCADE
    )
    price = models.PositiveIntegerField(default=0)
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

    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, allow_unicode=True)
    product = models.ForeignKey(
        Product,
        related_name="variants",
        on_delete=models.CASCADE
    )
    price = models.PositiveIntegerField(blank=True, null=True)
    active = models.BooleanField(default=False)
    created = models.DateTimeField(editable=False, default=timezone.now)
    modified = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name


class AttributeProduct(models.Model):
    attribute = models.ForeignKey(
        "Attribute", related_name="attribute_product", on_delete=models.CASCADE
    )
    product_template = models.ForeignKey(
        ProductTemplate, related_name="attribute_product", on_delete=models.CASCADE
    )
    connected_products = models.ManyToManyField(
        Product,
        blank=True,
        through="ConnectedProductAttribute",
        through_fields=("connection", "product"),
        related_name="connectedattributes",
    )

    def __str__(self):
        return f"T:{self.product_template}, A:{self.attribute}"


class AttributeVariant(models.Model):
    attribute = models.ForeignKey(
        "Attribute", related_name="attribute_variant", on_delete=models.CASCADE
    )
    product_template = models.ForeignKey(
        ProductTemplate, related_name="attribute_variant", on_delete=models.CASCADE
    )

    def __str__(self):
        return f"T:{self.product_template}, A:{self.attribute}"


class Attribute(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, allow_unicode=True)

    product_templates = models.ManyToManyField(
        ProductTemplate,
        blank=True,
        related_name="product_attributes",
        through=AttributeProduct,
        through_fields=("attribute", "product_template"),
    )

    def __str__(self):
        return self.name


class AttributeValue(models.Model):
    name = models.CharField(max_length=255)
    value = models.CharField(max_length=100)
    slug = models.SlugField(max_length=255, unique=True, allow_unicode=True)
    attribute = models.ForeignKey(
        Attribute,
        related_name="values",
        on_delete=models.CASCADE
    )

    def __str__(self):
        return self.name


class AbstractConnectedAttribute(models.Model):
    connection = None
    value = models.ManyToManyField(
        AttributeValue,
        related_name="v",
    )

    class Meta:
        abstract = True

    @property
    def attribute(self):
        return self.connection.attribute


class ConnectedProductAttribute(AbstractConnectedAttribute):
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

    def __str__(self):
        return f"C:{self.connection}, P:{self.product}"

    def save(self, *args, **kwargs):
        # if not self.product in self.connection.product_template.prodAucts.all():
        #     raise ValidationError('Product is not in a correct ProductTemplate')
        # if not self.value in self.connection.attribute.values.all():
        #     raise ValidationError(f'This Value cannot be choosen for this Product, {self.value}')
        return super().save(*args, **kwargs)


@receiver(post_save, sender=ConnectedProductAttribute)
def asd(sender, instance, *args, **kwargs):
    print(instance.value)
    print(instance.product)
    print(instance.connection)
