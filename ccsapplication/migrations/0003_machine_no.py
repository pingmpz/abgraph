# Generated by Django 3.2.4 on 2021-07-03 06:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ccsapplication', '0002_auto_20210703_1058'),
    ]

    operations = [
        migrations.AddField(
            model_name='machine',
            name='no',
            field=models.CharField(default='-1', max_length=50),
        ),
    ]
