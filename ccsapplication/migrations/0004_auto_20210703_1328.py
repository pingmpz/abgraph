# Generated by Django 3.2.4 on 2021-07-03 06:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ccsapplication', '0003_machine_no'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='machine',
            name='id',
        ),
        migrations.AlterField(
            model_name='machine',
            name='no',
            field=models.CharField(max_length=50, primary_key=True, serialize=False),
        ),
    ]
