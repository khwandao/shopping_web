# Generated by Django 4.1.2 on 2022-10-30 07:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shopping_web', '0003_rename_customer_id_memberorder_customer_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='memberorder',
            name='transaction_id',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]