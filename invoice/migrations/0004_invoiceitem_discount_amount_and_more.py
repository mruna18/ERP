# Generated by Django 5.2.4 on 2025-07-09 11:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('invoice', '0003_invoiceitem_rate'),
    ]

    operations = [
        migrations.AddField(
            model_name='invoiceitem',
            name='discount_amount',
            field=models.FloatField(default=0.0),
        ),
        migrations.AddField(
            model_name='invoiceitem',
            name='discount_percent',
            field=models.FloatField(default=0.0),
        ),
    ]
