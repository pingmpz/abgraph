# Generated by Django 3.2.4 on 2021-08-24 08:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ccsapplication', '0009_machine_exp_min'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='machine',
            name='exp_min',
        ),
    ]
