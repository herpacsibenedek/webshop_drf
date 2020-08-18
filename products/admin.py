from django.contrib import admin

from products.models import Attribute, AttributeProduct, AttributeValue, AttributeVariant, ConnectedProductAttribute, Product, ProductVariant, ProductTemplate

admin.site.register(Attribute)
admin.site.register(AttributeProduct)
admin.site.register(AttributeValue)
admin.site.register(AttributeVariant)
admin.site.register(ConnectedProductAttribute)
admin.site.register(Product)
admin.site.register(ProductVariant)
admin.site.register(ProductTemplate)
