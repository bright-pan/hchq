#coding=utf-8
from django.db import models
from django.contrib.auth.models import User
from hchq.department.models import Department
import caching.base
# Create your models here.

class ServiceArea(caching.base.CachingMixin, models.Model):
    name = models.CharField(max_length=64, unique=True)
    creater = models.ForeignKey(User)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'service_area'
        ordering = ['-updated_at']
        
    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('service_area_show', (), {'service_area_index': self.id})
    
    objects = caching.base.CachingManager()

class ServiceAreaDepartment(caching.base.CachingMixin, models.Model):
    service_area = models.ForeignKey(ServiceArea, related_name='service_area_to_department')
    department = models.ForeignKey(Department, related_name='department_to_service_area')
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'service_area_department'

    objects = caching.base.CachingManager()
