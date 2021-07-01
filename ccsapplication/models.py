from django.db import models
from datetime import datetime

class Section(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, default="-")

class Machine(models.Model):
    no = models.CharField(max_length=50, primary_key=True)
    section = models.ForeignKey(Section, null=True, on_delete=models.SET_NULL)

class Transaction(models.Model):
    id = models.AutoField(primary_key=True)
    machine = models.ForeignKey(Machine, on_delete=models.CASCADE)
    type = models.CharField(max_length=50, default="-") #DAY #NIGHT
    action_date = models.DateTimeField(null=True, default=None)
    created_date = models.DateTimeField(default=datetime.now())
