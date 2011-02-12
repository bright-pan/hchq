#coding=utf-8
from django.db import models
from django.contrib.auth.models import User
from hchq.department.models import Department
# Create your models here.

class CheckObject(models.Model):
    name = models.CharField(max_length=128, unique=True)
    department = models.ForeignKey(Department, related_name='check_object')

    creater = models.ForeignKey(User)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'check_object'
        ordering = ['-updated_at']

    @models.permalink
    def get_absolute_url(self):
        return ('check_object_show', (), {'check_object_index': self.id})
