#coding=utf-8
from django.db import models
from django.contrib.auth.models import User
import caching.base
# Create your models here.

class Department(caching.base.CachingMixin, models.Model):
    name = models.CharField(max_length=64, unique=True)
    creater = models.ForeignKey(User)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'department'
        ordering = ['-updated_at']

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('department_show', (), {'department_index': self.id})

    objects = caching.base.CachingManager()
