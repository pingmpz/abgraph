from django.db import models
from datetime import datetime

class WorkCenterGroup(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, default="-")
    exp_hrs = models.CharField(max_length=50, default="8") # Expect Hour

class Machine(models.Model):
    no = models.CharField(max_length=50, primary_key=True)
    name = models.CharField(max_length=50, default="-")
    exp_hrs = models.CharField(max_length=50, default="8") # Expect Hour
    wcg = models.ForeignKey(WorkCenterGroup, on_delete=models.CASCADE)

class Transaction(models.Model):
    id = models.AutoField(primary_key=True)
    mc = models.ForeignKey(Machine, on_delete=models.CASCADE)
    start_datetime = models.DateTimeField(null=True, default=None)
    stop_datetime = models.DateTimeField(null=True, default=None)
    operate_time = models.CharField(max_length=50, default="0")

class Runtime(models.Model):
    id = models.AutoField(primary_key=True)
    mc = models.ForeignKey(Machine, on_delete=models.CASCADE)
    date = models.DateField(null=True, default=None)
    opt_day = models.CharField(max_length=50, default="0")
    opt_night = models.CharField(max_length=50, default="0")
