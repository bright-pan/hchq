#coding=utf-8
from django.db import models
from django.contrib.auth.models import User
from service_area.models import ServiceAreaDepartment
import caching.base
# Create your models here.

class CheckObject(caching.base.CachingMixin, models.Model):
    name = models.CharField(max_length=128)
    id_number = models.CharField(max_length=18, unique=True)
    service_area_department = models.ForeignKey(ServiceAreaDepartment, related_name='check_object')
    photo = models.ImageField(upload_to='images/photos')
    thumbnail = models.ImageField(upload_to='images/thumbnails')
    is_family = models.BooleanField(default=False)
    address = models.CharField(max_length=128, null=True)
    mate_name = models.CharField(max_length=128)
    mate_id_number = models.CharField(max_length=18, null=True)
    mate_service_area_department = models.ForeignKey(ServiceAreaDepartment, related_name='check_object_mate')
    wedding_time = models.DateField(null=True)
    ctp_method = models.CharField(max_length=10, null=True)
    ctp_method_time = models.DateField(null=True)
    creater = models.ForeignKey(User)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    children_1_name = models.CharField(max_length=128, null=True)
    children_1_sex = models.CharField(max_length=10, null=True)
    children_1_id_number = models.CharField(max_length=18, null=True)

    children_2_name = models.CharField(max_length=128, null=True)
    children_2_sex = models.CharField(max_length=10, null=True)
    children_2_id_number = models.CharField(max_length=18, null=True)

    children_3_name = models.CharField(max_length=128, null=True)
    children_3_sex = models.CharField(max_length=10, null=True)
    children_3_id_number = models.CharField(max_length=18, null=True)
    
    
    class Meta:
        db_table = 'check_object'
        ordering = ['-updated_at']

    @models.permalink
    def get_absolute_url(self):
        return ('check_object_show', (), {'check_object_index': self.id, 'success': u'false'})

    objects = caching.base.CachingManager()
