from rest_framework import serializers
from rest_framework.reverse import reverse


class AttributeHIField(serializers.HyperlinkedIdentityField):

    def get_url(self, obj, view_name, request, format):
        kwargs = {'pk': obj.attribute_id, }
        return reverse(view_name, kwargs=kwargs, request=request, format=format)


class ConnectedAttributeHIField(serializers.HyperlinkedIdentityField):

    def get_url(self, obj, view_name, request, format):
        kwargs = {'pk': obj.connection.attribute.id, }
        return reverse(view_name, kwargs=kwargs, request=request, format=format)
