#coding=utf-8
from django.db import models
from django.contrib.auth.models import User
from hchq.service_area.models import ServiceAreaDepartment
import caching.base
# Create your models here.

class CheckObject(caching.base.CachingMixin, models.Model):
    name = models.CharField(max_length=128)
    id_number = models.CharField(max_length=18, unique=True)
    service_area_department = models.ForeignKey(ServiceAreaDepartment, related_name='check_object')
    photo = models.ImageField(upload_to='images/photos')
    is_family = models.BooleanField(default=False)
    mate_name = models.CharField(max_length=128)
    mate_id_number = models.CharField(max_length=18)
    mate_service_area_department = models.ForeignKey(ServiceAreaDepartment, related_name='check_object_mate')
    wedding_time = models.DateField(null=True)
    ctp_method = models.CharField(max_length=10, null=True)
    ctp_method_time = models.DateField(null=True)
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

    objects = caching.base.CachingManager()
        
class CheckObjectChildren(caching.base.CachingMixin, models.Model):
    name = models.CharField(max_length=128)
    sex = models.CharField(max_length=1)
    id_number = models.CharField(max_length=18, null=True)
    check_object = models.ForeignKey(CheckObject, related_name='check_object_children')
    
    class Meta:
        db_table = 'check_object_children'
        
    objects = caching.base.CachingManager()
