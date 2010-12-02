#coding=utf-8
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
# Create your models here.

class ServiceArea(models.Model):
    name = models.CharField(max_length=64, unique=True)
    creater = models.ForeignKey(User)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'service_area'
        ordering = ['-created_at']

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('service_area_show', (), {'service_area_id': self.id})
