# Generated by Django 4.1.2 on 2022-10-31 23:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shopping_web', '0004_alter_memberorder_transaction_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='description',
            field=models.CharField(blank=True, max_length=1000, null=True),
        ),
    ]
