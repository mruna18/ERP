# Generated by Django 5.2.4 on 2025-07-14 12:04

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0004_alter_company_owner_alter_company_user'),
        ('invoice', '0012_remove_cashtransaction_company_and_more'),
        ('parties', '0003_remove_party_is_active_party_deleted'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='invoice',
            name='company',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='invoices', to='companies.company'),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='created_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='party',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='parties.party'),
        ),
        migrations.AlterField(
            model_name='invoiceitem',
            name='invoice',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='items', to='invoice.invoice'),
        ),
    ]
