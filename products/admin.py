from django.contrib import admin

from products.models import *

admin.site.register(Attribute)
admin.site.register(AttributeProduct)
admin.site.register(AttributeValue)
admin.site.register(AttributeVariant)
admin.site.register(ConnectedProductAttribute)
admin.site.register(ConnectedVariantAttribute)
admin.site.register(Product)
admin.site.register(ProductVariant)
admin.site.register(ProductTemplate)
