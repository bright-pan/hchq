#coding=utf-8
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.db.models import ObjectDoesNotExist
from django.db import IntegrityError

from hchq.service_area.models import ServiceArea
from hchq.untils import gl
import re

class ServiceAreaAddForm(forms.Form):
    """
    服务区域添加表单
    """
    service_area_name_set = None
    service_area_name = forms.CharField(
        max_length=500,
        required=True, 
        label=_(u'服务区域名称'), 
        widget=forms.Textarea(attrs={'class':'',
                                      'size':'30',}), 
        help_text=_(u'例如：周田，周田乡/西江镇/文武坝乡/...'),
        error_messages = gl.service_area_name_error_messages,
        )
    
    def clean_service_area_name(self):
        try:
            service_area_name_copy = self.data.get('service_area_name')
#            print service_area_name_copy
            if re.match(gl.service_area_name_add_re_pattern, service_area_name_copy) is None:
                raise forms.ValidationError(gl.service_area_name_error_messages['format_error'])
            self.service_area_name_set = set(filter(gl.filter_null_string, service_area_name_copy.split(u'/')))
        except ObjectDoesNotExist:
            raise forms.ValidationError(gl.service_area_name_error_messages['form_error'])
        return self.service_area_name_set

    def service_area_add(self, user=None):
        service_area_name_list = []
        service_area_name_obj = None
        created = None
        if user is not None and user.is_authenticated() and self.service_area_name_set is not None:
            for service_area_name_copy in self.service_area_name_set:
                service_area_name_obj, created = ServiceArea.objects.get_or_create(name=service_area_name_copy, creater=user)
                if created is True:
                    service_area_name_list.append(service_area_name_obj)
                else:
                    if service_area_name_obj.is_active == False:
                        service_area_name_obj.is_active = True
                        service_area_name_obj.save()
        return service_area_name_list

class ServiceAreaModifyForm(forms.Form):
    """
    服务区域修改表单
    """
    service_area_name_copy = None
    service_area_id_copy = None
    service_area_object = None
    service_area_id_object = None

    service_area_name = forms.CharField(
        max_length=128,
        required=True,
        label=_(u'新服务区域名称'), 
        widget=forms.TextInput(attrs={'class':'',
                                      'size':'30',}), 
        help_text=_(u'例如：周田，周田乡...'),
        error_messages = gl.service_area_name_error_messages,
        )
    
    def clean_service_area_name(self):
        try:
            self.service_area_name_copy = self.data.get('service_area_name')
            try:
                self.service_area_id_copy = int(self.data.get('service_area_id'))
            except ValueError:
                raise forms.ValidationError(gl.service_area_name_error_messages['form_error'])
            self.service_area_id_object = ServiceArea.objects.get(pk=self.service_area_id_copy)
        except ObjectDoesNotExist:
            raise forms.ValidationError(gl.service_area_name_error_messages['form_error'])
#            print self.service_area_name_copy
#            print type(self.service_area_id_copy)
        if re.match(gl.service_area_name_modify_re_pattern, self.service_area_name_copy) is None:
            raise forms.ValidationError(gl.service_area_name_error_messages['format_error'])
        try:
            self.service_area_object = ServiceArea.objects.get(name=self.service_area_name_copy)
        except ObjectDoesNotExist:
            self.service_area_object = None
            return self.service_area_name_copy
        if self.service_area_object.id == self.service_area_id_copy:
            raise forms.ValidationError(gl.service_area_name_error_messages['already_error'])
        else:
            if self.service_area_object.is_active is True:
                raise forms.ValidationError(gl.service_area_name_error_messages['already_error'])
        return self.service_area_name_copy

    def service_area_modify(self):

        if self.service_area_object is not None:
            if self.service_area_object.is_active is False:
                self.service_area_object.is_active = True
                self.service_area_object.save()
                self.service_area_id_object.is_active = False
                self.service_area_id_object.save()
                return True
            else:
                return False
        else:
            self.service_area_id_object.name = self.service_area_name_copy
            self.service_area_id_object.save()
            return True

class ServiceAreaDeleteForm(forms.Form):
    """
    服务区域修改表单
    """
    service_area_id_copy = None
    service_area_id_object = None

    service_area_id = forms.CharField(
        widget=forms.HiddenInput(),
        error_messages = gl.service_area_name_error_messages,
        )
    
    def clean_service_area_id(self):
        try:
            try:
                self.service_area_id_copy = int(self.data.get('service_area_id'))
            except ValueError:
                raise forms.ValidationError(gl.service_area_name_error_messages['form_error'])
            self.service_area_id_object = ServiceArea.objects.get(pk=self.service_area_id_copy)
        except ObjectDoesNotExist:
            raise forms.ValidationError(gl.service_area_name_error_messages['form_error'])
        return self.service_area_id_copy

    def service_area_delete(self):

        if self.service_area_id_object is not None:
            self.service_area_id_object.is_active = False
            self.service_area_id_object.save()
        else:
            return False
