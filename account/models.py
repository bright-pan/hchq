#coding=utf-8
from django.db import models
from django.contrib.auth.models import User
from hchq.service_area.models import ServiceAreaDepartment

# Create your models here.

class UserProfile(models.Model):
    user = models.OneToOneField(User)
    is_checker = models.BooleanField(default=False)
    service_area_department = models.ForeignKey(ServiceAreaDepartment)

    @models.permalink
    def get_absolute_url(self):
        return ('account_show', (), {'account_index': self.id})
