# Generated by Django 3.1.2 on 2020-10-24 09:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_remove_product_slug'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='discount',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]