# Generated by Django 3.2.4 on 2021-08-30 10:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ccsapplication', '0014_rename_exp_min_machine_exp_hrs'),
    ]

    operations = [
        migrations.AddField(
            model_name='workcentergroup',
            name='exp_hrs',
            field=models.CharField(default='8', max_length=50),
        ),
        migrations.CreateModel(
            name='Runtime',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('date', models.DateField(default=None, null=True)),
                ('opt_day', models.CharField(default='0', max_length=50)),
                ('opt_night', models.CharField(default='0', max_length=50)),
                ('mc', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ccsapplication.machine')),
            ],
        ),
    ]
