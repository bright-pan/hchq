#coding=utf-8
from django.db import models
from django.contrib.auth.models import User
import caching.base
# Create your models here.

class Department(caching.base.CachingMixin, models.Model):
    name = models.CharField(max_length=64, unique=True)
    creater = models.ForeignKey(User)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'department'
        ordering = ['-updated_at']
        permissions = (

            (u'unlocal', u'跨区操作'),
            
            (u'account_add', u'系统用户添加'),
            (u'account_modify', u'系统用户修改'),
            (u'account_delete', u'系统用户删除'),
            (u'account_list', u'系统用户查询'),

            (u'sd_management', u'服务区域与单位部门管理'),
            (u'cp_management', u'检查项目管理'),
            (u'role_management', u'角色权限管理'),
            
            (u'co_add', u'检查对象添加'),
            (u'co_modify', u'检查对象修改'),
            (u'co_delete', u'检查对象删除'),
            (u'co_list', u'检查对象查询'),
            
            (u'cr_add', u'检查结果添加'),
            (u'cr_list', u'检查结果查询'),
            (u'report_print', u'检查结果报表导出'),
            (u'ct_print', u'证明导出'),

            )

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('department_show', (), {'department_index': self.id})

    objects = caching.base.CachingManager()
