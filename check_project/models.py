#coding=utf-8
from django.db import models
from django.contrib.auth.models import User
import caching.base
# Create your models here.

class CheckProject(caching.base.CachingMixin, models.Model):
    name = models.CharField(max_length=64, unique=True)
    creater = models.ForeignKey(User)
    is_active = models.BooleanField(default=True)
    is_setup = models.BooleanField(default=False)
    start_time = models.DateField()
    end_time = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'check_project'
        ordering = ['-updated_at']

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('check_project_show', (), {'check_project_index': self.id})

    objects = caching.base.CachingManager()
