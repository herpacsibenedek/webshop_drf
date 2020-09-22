# from django.contrib.auth import get_user_model
# from django.urls import reverse
# from rest_framework import status

# from django.urls import include, path, reverse
# from rest_framework.test import APITestCase, URLPatternsTestCase
# from ..models import *
# from ..api.serializers import *


# class AttributeSerializerTest(APITestCase):

#     def setUp(self):
#         pass

#     def test_create_attribute(self):
#         """
#         Ensure we can create a new Attribute object.
#         """
#         url = reverse('attribute-list')
#         data = {'name': 'ABV'}
#         response = self.client.post(url, data, format='json')
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)
#         self.assertEqual(Attribute.objects.count(), 1)
#         self.assertEqual(Attribute.objects.get().name, 'ABV')
