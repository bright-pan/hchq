#coding=utf-8
from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class ServiceArea(models.Model):
    name = models.CharField(max_length=128, unique=True)
    creater = models.ForeignKey(User)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

