# Generated by Django 3.2.4 on 2021-07-03 03:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ccsapplication', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='RawTransaction',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('MachineOperatorID', models.CharField(default='-', max_length=50)),
                ('MachineOperatorStart', models.DateTimeField(default=None, null=True)),
                ('MachineOperatorStop', models.DateTimeField(default=None, null=True)),
                ('MachineOperatorTime', models.CharField(default='-1', max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='WorkCenterGroup',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(default='-', max_length=50)),
            ],
        ),
        migrations.RemoveField(
            model_name='machine',
            name='machinename',
        ),
        migrations.RemoveField(
            model_name='machine',
            name='machinenumber',
        ),
        migrations.RemoveField(
            model_name='machine',
            name='processcode',
        ),
        migrations.AddField(
            model_name='machine',
            name='name',
            field=models.CharField(default='-', max_length=50),
        ),
        migrations.AlterField(
            model_name='machine',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
        migrations.AddField(
            model_name='machine',
            name='wcg',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='ccsapplication.workcentergroup'),
            preserve_default=False,
        ),
    ]