#coding=utf-8
from django.db import models
from django.contrib.auth.models import User
from hchq.check_object.models import CheckObject

class CheckResult(models.Model):

    check_object = models.ForeignKey(CheckObject, related_name='check_result')
    days = models.DecimalField(max_digits=9,decimal_places=1)
    desc = models.CharField(max_length=200, blank=True)
    recorder = models.ForeignKey(User, related_name='check_result_recorder')
    check_time = models.DateTimeField(auto_now_add=True)
#    check_time = models.DateTimeField()
    
    class Meta:
        db_table = 'check_result'
        ordering = ['-check_time']

    @models.permalink
    def get_absolute_url(self):
        return ('check_result_show', (), {'check_result_index': self.check_object.id})

