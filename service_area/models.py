#coding=utf-8
from django.db import models

# Create your models here.

class ServiceArea(models.Model):
    name = models.CharField(max_length=128, unique=True)
