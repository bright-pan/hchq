#coding=utf-8
from django.db import models
from django.contrib.auth.models import User
from hchq.service_area.models import ServiceAreaDepartment
import caching.base
# Create your models here.

class UserProfile(caching.base.CachingMixin, models.Model):
    user = models.OneToOneField(User)
    is_checker = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    service_area_department = models.ForeignKey(ServiceAreaDepartment)

    @models.permalink
    def get_absolute_url(self):
        return ('account_show', (), {'account_index': self.id})

    objects = caching.base.CachingManager()
