# Generated by Django 3.2.4 on 2021-08-24 08:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ccsapplication', '0012_remove_machine_exp_min'),
    ]

    operations = [
        migrations.AddField(
            model_name='machine',
            name='exp_min',
            field=models.CharField(default='8', max_length=50),
        ),
    ]
