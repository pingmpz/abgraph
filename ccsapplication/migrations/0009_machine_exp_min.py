# Generated by Django 3.2.4 on 2021-08-24 08:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ccsapplication', '0008_remove_transaction_shift'),
    ]

    operations = [
        migrations.AddField(
            model_name='machine',
            name='exp_min',
            field=models.CharField(default='0', max_length=50),
        ),
    ]
