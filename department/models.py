#coding=utf-8
from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Department(models.Model):
    name = models.CharField(max_length=64, unique=True)
    creater = models.ForeignKey(User)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'department'
        ordering = ['-updated_at']
        permissions = (
            (u'account_management', u'帐户管理'),
            (u'department_management', u'单位管理'),
            (u'service_area_management', u'服务区域管理'),
            )

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('department_show', (), {'department_index': self.id})
