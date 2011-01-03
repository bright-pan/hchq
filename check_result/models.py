#coding=utf-8
from django.db import models
from django.contrib.auth.models import User
from hchq.check_object.models import CheckObject
from hchq.check_project.models import CheckProject
import caching.base
# Create your models here.

class CheckResult(caching.base.CachingMixin, models.Model):

    check_object = models.ForeignKey(CheckObject)
    check_project = models.ForeignKey(CheckProject)
    result = models.CharField(max_length=128)
    checker = models.ForeignKey(User, related_name='check_result_checker')
    recorder = models.ForeignKey(User, related_name='check_result_recorder')
    check_time = models.DateTimeField(auto_now_add=True)
    is_latest = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'check_result'
        ordering = ['-check_time']

    @models.permalink
    def get_absolute_url(self):
        return ('check_result_show', (), {'check_result_index': self.id})

    objects = caching.base.CachingManager()
        
