# Generated by Django 3.0.8 on 2020-09-01 14:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='connectedvariantattribute',
            old_name='product',
            new_name='variant',
        ),
        migrations.AddField(
            model_name='attributeproduct',
            name='connected_products',
            field=models.ManyToManyField(blank=True, related_name='attributesrelated', through='products.ConnectedProductAttribute', to='products.Product'),
        ),
        migrations.AddField(
            model_name='attributevariant',
            name='connected_variants',
            field=models.ManyToManyField(blank=True, related_name='attributesrelated', through='products.ConnectedVariantAttribute', to='products.ProductVariant'),
        ),
        migrations.AlterUniqueTogether(
            name='connectedvariantattribute',
            unique_together={('variant', 'connection')},
        ),
    ]
