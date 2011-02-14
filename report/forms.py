#coding=utf-8
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import *
from django.db.models import ObjectDoesNotExist, Sum, Count
from hchq.untils import gl
from hchq.department.models import Department
from hchq.check_object.models import *
from hchq.check_result.models import *
from hchq.report.check_project_report import check_project_report
from hchq import settings
import re
import datetime


    
class ReportStatisticsForm(forms.Form):

    profit = forms.DecimalField(
        required=True,
        label=_(u'加班工资/天'),
        help_text=_(u'例如:100.54天的加班工资为100.54元。'),
        max_digits=9,
        decimal_places=2,
        )

    start_time = forms.DateField(
        required=False,
        label=_(u'开始时间'),
        help_text=_(u'例如：2010-10-1'),
        input_formats = ('%Y-%m-%d',)
        )
    end_time  = forms.DateField(
        required=False,
        label=_(u'结束时间'),
        help_text=_(u'例如：2010-10-31'),
        input_formats = ('%Y-%m-%d',)
        )
    def query_start_time(self, query_set=None):
        start_time = self.cleaned_data['start_time']

        if query_set is None:
            return query_set

        if start_time == None:
            pass
        else:
            start_time = datetime.datetime(start_time.year, start_time.month, start_time.day)
            query_set = query_set.filter(check_time__gte=start_time)
        
        return query_set

    def query_end_time(self, query_set=None):
        end_time = self.cleaned_data['end_time']
        if query_set is None:
            return query_set

        if end_time == None:
            pass
        else:
            end_time = datetime.datetime(end_time.year, end_time.month, end_time.day, 23, 59, 59)
            print end_time
            print query_set
            query_set = query_set.filter(check_time__lte=end_time)
        return query_set

    def report(self, request=None):
        profit = self.cleaned_data['profit']
        query_set_check_result = CheckResult.objects.all()
        query_set_check_result = self.query_start_time(query_set_check_result)
        query_set_check_result = self.query_end_time(query_set_check_result)
        query_set_check_object = CheckObject.objects.all().order_by('name')
        query_set = []
        for check_object in query_set_check_object:
            qs = query_set_check_result.filter(check_object=check_object)
            dict_check_object = {}
            dict_check_object['id'] = check_object.id
            dict_check_object['name'] = check_object.name
            dict_check_object['department_name'] = check_object.department.name
            dict_check_object['check_result_counts'] = qs.count()
            dict_check_object['check_result_days'] = qs.aggregate(days=Sum('days'))['days']
            dict_check_object['profit'] = profit * dict_check_object['check_result_days']
            query_set.append(dict_check_object)

        return check_project_report(query_set, request)
