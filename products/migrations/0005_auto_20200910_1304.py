# Generated by Django 3.0.8 on 2020-09-10 11:04

from decimal import Decimal
import django.core.validators
from django.db import migrations
import djmoney.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0004_auto_20200908_1341'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productvariant',
            name='price',
            field=djmoney.models.fields.MoneyField(decimal_places=4, max_digits=19, null=True, validators=[django.core.validators.MinValueValidator(Decimal('0'))]),
        ),
    ]
