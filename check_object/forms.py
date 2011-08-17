#coding=utf-8
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import *
from django.db.models import ObjectDoesNotExist
from PIL import Image,ImageDraw,ImageFont
from StringIO import StringIO
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from hchq.untils import gl
from hchq.service_area.models import ServiceArea, ServiceAreaDepartment
from hchq.department.models import Department
from hchq.check_object.models import *
from hchq.check_project.models import *
from hchq.check_result.models import *
from hchq import settings
import re
import datetime



class CheckObjectAddForm(forms.Form):
    """
    检查对象添加表单
    """

    service_area_department_object = None
    mate_service_area_department_object = None
    ctp_method_time_copy = None
    wedding_time_copy = None
    
    name = forms.CharField(
        max_length=64,
        required=True, 
        label=_(u'妻子姓名(*)'), 
        widget=forms.TextInput(attrs={'class':'',
                                     'size':'30',
                                     }
                              ), 
        help_text=_(u'例如：张三、李四'),
        error_messages = gl.check_object_name_error_messages,
        )
    id_number = forms.CharField(
        max_length=18,
        required=True,
        label=_(u'身份证号(*)'),
        help_text=_(u'例如：360733199009130025'),
        error_messages = gl.check_object_id_number_error_messages,
        )
    service_area_name = forms.CharField(
        max_length=128,
        required=True,
        label=_(u'服务区域(*)'),
        widget=forms.TextInput(attrs={'class':'',
                                      'size':'30',}), 
        help_text=_(u'例如：西江镇、周田乡'),
        error_messages = gl.service_area_name_error_messages,
        )
    department_name = forms.CharField(
        max_length=128,
        required=True, 
        label=_(u'单位部门(*)'), 
        widget=forms.TextInput(attrs={'class':'',
                                     'size':'30',
                                     }
                              ), 
        help_text=_(u'例如：县委、政法委、公安局'),
        error_messages = gl.department_name_error_messages,
        )
    is_family = forms.CharField(
        required=True,
        label =_(u'家属(*)'),
        help_text=_(u'例如：对象没有单位则打勾'),
        widget=forms.CheckboxInput(attrs={'class':'',
                                          'value':'is_family',
                                          }, 
                                   check_test=None,
                                   ),
        )
    mate_name = forms.CharField(
        max_length=64,
        required=True,
        label=_(u'丈夫姓名(*)'),
        widget=forms.TextInput(attrs={'class':'',
                                     'size':'30',
                                     }
                              ), 
        help_text=_(u'例如：张三、李四'),
        error_messages = gl.check_object_name_error_messages,
        )
    mate_id_number = forms.CharField(
        max_length=18,
        required=False,
        label=_(u'身份证号'),
        help_text=_(u'例如：360733199009130025'),
        error_messages = gl.check_object_id_number_error_messages,
        )
    mate_service_area_name = forms.CharField(
        max_length=128,
        required=True,
        label=_(u'服务区域(*)'), 
        widget=forms.TextInput(attrs={'class':'',
                                      'size':'30',}), 
        help_text=_(u'例如：西江镇、周田乡'),
        error_messages = gl.service_area_name_error_messages,
        )
    mate_department_name = forms.CharField(
        max_length=128,
        required=True, 
        label=_(u'单位部门(*)'), 
        widget=forms.TextInput(attrs={'class':'',
                                     'size':'30',
                                     }
                              ), 
        help_text=_(u'例如：县委、政法委、公安局'),
        error_messages = gl.department_name_error_messages,
        )

    ctp_method = forms.ChoiceField(
        required=True,
        label =_(u'避孕措施'),
        choices=((u'method_0', u'未使用'),
                 (u'method_1', u'避孕环方式'),
                 (u'method_2', u'避孕药方式'),
                 (u'method_3', u'其他方式'),
                 ),
        help_text=_(u'例如：上环选避孕环方式'),
        )
    ctp_method_time = forms.DateField(
        required=False,
        label=_(u'实施时间'),
        help_text=_(u'例如：2010-10-25'),
        error_messages = gl.check_object_ctp_method_time_error_messages,
        input_formats = ('%Y-%m-%d',)
        )
    wedding_time = forms.DateField(
        required=False,
        label=_(u'结婚时间'),
        help_text=_(u'例如：1985-1-1'),
        error_messages = gl.check_object_wedding_time_error_messages,
        input_formats = ('%Y-%m-%d',)
        )
    address = forms.CharField(
        max_length=128,
        required=False,
        label=_(u'家庭住址'),
        widget=forms.TextInput(attrs={'class':'',
                                     'size':'30',
                                     }
                              ), 
        error_messages = gl.department_name_error_messages,
        )

    children_1_name = forms.CharField(
        max_length=64,
        required=False, 
        label=_(u'姓名'), 
        widget=forms.TextInput(attrs={'class':'',
                                     'size':'30',
                                     }
                              ), 
        error_messages = gl.check_object_name_error_messages,
        )
    children_1_sex = forms.ChoiceField(
        required=True,
        label =_(u'性别'),
        choices=((u'm', u'男'),
                 (u'w', u'女'),
                 ),
        )

    children_1_id_number = forms.CharField(
        max_length=18,
        required=False,
        label=_(u'身份证号'),
        error_messages = gl.check_object_id_number_error_messages,
        )
    children_2_name = forms.CharField(
        max_length=64,
        required=False, 
        label=_(u'姓名'), 
        widget=forms.TextInput(attrs={'class':'',
                                     'size':'30',
                                     }
                              ), 
        error_messages = gl.check_object_name_error_messages,
        )
    children_2_sex = forms.ChoiceField(
        required=True,
        label =_(u'性别'),
        choices=((u'm', u'男'),
                 (u'w', u'女'),
                 ),
        )

    children_2_id_number = forms.CharField(
        max_length=18,
        required=False,
        label=_(u'身份证号'),
        error_messages = gl.check_object_id_number_error_messages,
        )
    children_3_name = forms.CharField(
        max_length=64,
        required=False, 
        label=_(u'姓名'), 
        widget=forms.TextInput(attrs={'class':'',
                                     'size':'30',
                                     }
                              ), 
        error_messages = gl.check_object_name_error_messages,
        )
    children_3_sex = forms.ChoiceField(
        required=True,
        label =_(u'性别'),
        choices=((u'm', u'男'),
                 (u'w', u'女'),
                 ),
        )

    children_3_id_number = forms.CharField(
        max_length=18,
        required=False,
        label=_(u'身份证号'),
        error_messages = gl.check_object_id_number_error_messages,
        )
    def clean_name(self):
        try:
            name_copy = self.data.get('name')
            if re.match(gl.check_object_name_add_re_pattern, name_copy) is None:
                raise forms.ValidationError(gl.check_object_name_error_messages['format_error'])
        except ObjectDoesNotExist:
            raise forms.ValidationError(gl.check_object_name_error_messages['form_error'])
        return name_copy
    
    def clean_id_number(self):
        try:
            id_number_copy = self.data.get('id_number')
        except ObjectDoesNotExist:
            raise forms.ValidationError(gl.check_object_id_number_error_messages['form_error'])
        if re.match(gl.check_object_id_number_add_re_pattern, id_number_copy) is None:
            raise forms.ValidationError(gl.check_object_id_number_error_messages['format_error'])
        try:
            self.role_object = CheckObject.objects.get(id_number=id_number_copy, is_active=True)
        except ObjectDoesNotExist:
            return id_number_copy
        raise forms.ValidationError(gl.check_object_id_number_error_messages['already_error'])
        
    def clean_service_area_name(self):
        try:
           service_area_name_copy = self.data.get('service_area_name')
        except ObjectDoesNotExist:
            raise forms.ValidationError(gl.service_area_name_error_messages['form_error'])

        if re.match(gl.service_area_name_add_re_pattern, service_area_name_copy) is None:
            raise forms.ValidationError(gl.service_area_name_error_messages['format_error'])

        try:
            ServiceArea.objects.get(name=service_area_name_copy, is_active=True)
        except ObjectDoesNotExist:
            raise forms.ValidationError(gl.service_area_name_error_messages['not_exist_error'])

        return service_area_name_copy

    def clean_department_name(self):
        try:
            department_name_copy = self.data.get('department_name')
            service_area_name_copy = self.data.get('service_area_name')
        except ObjectDoesNotExist:
            raise forms.ValidationError(gl.department_name_error_messages['form_error'])
        if re.match(gl.department_name_add_re_pattern, department_name_copy) is None:
            raise forms.ValidationError(gl.department_name_error_messages['format_error'])
        try:
            department_object = Department.objects.get(name=department_name_copy, is_active=True)
        except ObjectDoesNotExist:
            raise forms.ValidationError(gl.department_name_error_messages['not_exist_error'])
        try:
            service_area_object = ServiceArea.objects.get(name=service_area_name_copy, is_active=True)
        except ObjectDoesNotExist:
            raise forms.ValidationError(gl.service_area_name_error_messages['not_exist_error'])
        try:
            self.service_area_department_object = ServiceAreaDepartment.objects.get(service_area=service_area_object, department=department_object)
        except ObjectDoesNotExist:
            raise forms.ValidationError(gl.department_name_error_messages['not_match_error'])
        return department_name_copy
    def clean_mate_name(self):
        try:
            mate_name_copy = self.data.get('mate_name')
            if re.match(gl.check_object_name_add_re_pattern, mate_name_copy) is None:
                raise forms.ValidationError(gl.check_object_name_error_messages['format_error'])
        except ObjectDoesNotExist:
            raise forms.ValidationError(gl.check_object_name_error_messages['form_error'])
        return mate_name_copy
    
    def clean_mate_id_number(self):
        try:
            mate_id_number_copy = self.data.get('mate_id_number')
        except ObjectDoesNotExist:
            raise forms.ValidationError(gl.check_object_id_number_error_messages['form_error'])
        if re.match(gl.check_object_id_number_add_re_pattern, mate_id_number_copy) is None:
            raise forms.ValidationError(gl.check_object_id_number_error_messages['format_error'])
        return mate_id_number_copy

    def clean_mate_service_area_name(self):
        try:
           mate_service_area_name_copy = self.data.get('mate_service_area_name')
        except ObjectDoesNotExist:
            raise forms.ValidationError(gl.service_area_name_error_messages['form_error'])

        if re.match(gl.service_area_name_add_re_pattern, mate_service_area_name_copy) is None:
            raise forms.ValidationError(gl.service_area_name_error_messages['format_error'])

        try:
            ServiceArea.objects.get(name=mate_service_area_name_copy, is_active=True)
        except ObjectDoesNotExist:
            raise forms.ValidationError(gl.service_area_name_error_messages['not_exist_error'])

        return mate_service_area_name_copy

    def clean_mate_department_name(self):
        try:
            mate_department_name_copy = self.data.get('mate_department_name')
            mate_service_area_name_copy = self.data.get('mate_service_area_name')
        except ObjectDoesNotExist:
            raise forms.ValidationError(gl.department_name_error_messages['form_error'])
        if re.match(gl.department_name_add_re_pattern, mate_department_name_copy) is None:
            raise forms.ValidationError(gl.department_name_error_messages['format_error'])
        try:
            mate_department_object = Department.objects.get(name=mate_department_name_copy, is_active=True)
        except ObjectDoesNotExist:
            raise forms.ValidationError(gl.department_name_error_messages['not_exist_error'])
        try:
            mate_service_area_object = ServiceArea.objects.get(name=mate_service_area_name_copy, is_active=True)
        except ObjectDoesNotExist:
            raise forms.ValidationError(gl.service_area_name_error_messages['not_exist_error'])
        try:
            self.mate_service_area_department_object = ServiceAreaDepartment.objects.get(service_area=mate_service_area_object, department=mate_department_object)
        except ObjectDoesNotExist:
            raise forms.ValidationError(gl.department_name_error_messages['not_match_error'])
        return mate_department_name_copy
        
    def clean_ctp_method_time(self):
        try:
            ctp_method_time_copy = self.cleaned_data.get('ctp_method_time')
        except ObjectDoesNotExist:
            raise forms.ValidationError(gl.check_project_ctp_method_time_error_messages['form_error'])
        if ctp_method_time_copy is not None:
            if ctp_method_time_copy > datetime.datetime.now().date():
                raise forms.ValidationError(gl.check_project_ctp_method_time_error_messages['logic_error'])
        return ctp_method_time_copy
    
    def clean_wedding_time(self):
        try:
            wedding_time_copy = self.cleaned_data.get('wedding_time')
#            print wedding_time_copy
        except ObjectDoesNotExist:
            raise forms.ValidationError(gl.check_object_wedding_time_error_messages['form_error'])
        if wedding_time_copy is not None:
            if wedding_time_copy > datetime.datetime.now().date():
                raise forms.ValidationError(gl.check_object_wedding_time_error_messages['logic_error'])
        return wedding_time_copy
    def clean_children_1_name(self):
        try:
            children_name_copy = self.data.get('children_1_name')
            if re.match(gl.check_object_name_search_re_pattern, children_name_copy) is None:
                raise forms.ValidationError(gl.check_object_name_error_messages['format_error'])
        except ObjectDoesNotExist:
            raise forms.ValidationError(gl.check_object_name_error_messages['form_error'])
        return children_name_copy
    
    def clean_children_1_id_number(self):
        try:
            children_id_number_copy = self.data.get('children_1_id_number')
        except ObjectDoesNotExist:
            raise forms.ValidationError(gl.check_object_id_number_error_messages['form_error'])
        if re.match(gl.check_object_id_number_search_re_pattern, children_id_number_copy) is None:
            raise forms.ValidationError(gl.check_object_id_number_error_messages['format_error'])
        return children_id_number_copy
    def clean_children_2_name(self):
        try:
            children_name_copy = self.data.get('children_2_name')
            if re.match(gl.check_object_name_search_re_pattern, children_name_copy) is None:
                raise forms.ValidationError(gl.check_object_name_error_messages['format_error'])
        except ObjectDoesNotExist:
            raise forms.ValidationError(gl.check_object_name_error_messages['form_error'])
        return children_name_copy
    
    def clean_children_2_id_number(self):
        try:
            children_id_number_copy = self.data.get('children_2_id_number')
        except ObjectDoesNotExist:
            raise forms.ValidationError(gl.check_object_id_number_error_messages['form_error'])
        if re.match(gl.check_object_id_number_search_re_pattern, children_id_number_copy) is None:
            raise forms.ValidationError(gl.check_object_id_number_error_messages['format_error'])
        return children_id_number_copy
    def clean_children_3_name(self):
        try:
            children_name_copy = self.data.get('children_3_name')
            if re.match(gl.check_object_name_search_re_pattern, children_name_copy) is None:
                raise forms.ValidationError(gl.check_object_name_error_messages['format_error'])
        except ObjectDoesNotExist:
            raise forms.ValidationError(gl.check_object_name_error_messages['form_error'])
        return children_name_copy
    
    def clean_children_3_id_number(self):
        try:
            children_id_number_copy = self.data.get('children_3_id_number')
        except ObjectDoesNotExist:
            raise forms.ValidationError(gl.check_object_id_number_error_messages['form_error'])
        if re.match(gl.check_object_id_number_search_re_pattern, children_id_number_copy) is None:
            raise forms.ValidationError(gl.check_object_id_number_error_messages['format_error'])
        return children_id_number_copy

    def init_permission(self, user=None):
        if user is not None:
            if user.has_perm('department.unlocal'):
                return False
            else:
                self.fields['service_area_name'].widget.attrs['value'] = user.get_profile().service_area_department.service_area.name
                self.fields['service_area_name'].widget.attrs['readonly'] = True
                return True
        else:
            return None
    
    def add(self, user = None):
        if user is not None and self.service_area_department_object is not None and self.mate_service_area_department_object is not None:
            if self.cleaned_data['is_family'] == u'is_family':
                is_family_value = True
            else:
                is_family_value = False
            try:
                file_temp = default_storage.open(u'images/photos/temp/%s.temp' % user.username)
            except IOError:
                return None
            file_path = u'images/photos/%s.jpg' % self.cleaned_data['id_number']
            default_storage.delete(file_path)
            file_temp_name = file_temp.name.decode('utf-8').replace('\\', '/')
            font = ImageFont.truetype('%s/static/fonts/MSYH.TTF' % settings.CURRENT_PATH,12)
            try:
                img = Image.open(file_temp_name)
            except IOError:
                img = Image.open('%s/static/images/photo.jpg' % settings.CURRENT_PATH)
                if img.mode != "RGB":
                    img = img.convert("RGB")
                img.resize(gl.check_object_image_size,Image.ANTIALIAS)
            draw = ImageDraw.Draw(img)
            draw.rectangle([gl.check_object_id_mark, gl.check_object_image_size], fill=gl.check_object_id_mark_bottom_color)
            draw.text(gl.check_object_id_mark, u'%s %s' % (self.cleaned_data['name'], self.cleaned_data['id_number']) ,gl.check_object_id_mark_color,font=font)
            del draw
            img.save(file_temp_name,"JPEG")
            
            default_storage.save(file_path, file_temp)
            file_temp.close()
            del img
            del file_temp
            try:
                check_object = CheckObject.objects.get(is_active=False, id_number=self.cleaned_data['id_number'])
            except ObjectDoesNotExist:
#                print self.cleaned_data['wedding_time'], self.cleaned_data['address']
                check_object = CheckObject.objects.create(name=self.cleaned_data['name'],
                                                          photo=file_path,
                                                          id_number=self.cleaned_data['id_number'],
                                                          service_area_department=self.service_area_department_object,
                                                          is_family=is_family_value,
                                                          mate_name=self.cleaned_data['mate_name'],
                                                          mate_id_number=self.cleaned_data['mate_id_number'],
                                                          mate_service_area_department=self.mate_service_area_department_object,
                                                          ctp_method = self.cleaned_data['ctp_method'],
                                                          ctp_method_time = self.cleaned_data['ctp_method_time'],
                                                          wedding_time = self.cleaned_data['wedding_time'],
                                                          address = self.cleaned_data['address'],
                                                          children_1_name = self.cleaned_data['children_1_name'],
                                                          children_1_sex = self.cleaned_data['children_2_sex'],
                                                          children_1_id_number = self.cleaned_data['children_1_id_number'],
                                                          children_2_name = self.cleaned_data['children_2_name'],
                                                          children_2_sex = self.cleaned_data['children_2_sex'],
                                                          children_2_id_number = self.cleaned_data['children_2_id_number'],
                                                          children_3_name = self.cleaned_data['children_3_name'],
                                                          children_3_sex = self.cleaned_data['children_3_sex'],
                                                          children_3_id_number = self.cleaned_data['children_3_id_number'],
                                                          creater = user,
                                                          )
                return check_object
            check_object.is_active =True
            check_object.name=self.cleaned_data['name']
            check_object.photo=file_path
            check_object.service_area_department=self.service_area_department_object
            check_object.is_family=is_family_value
            check_object.mate_name=self.cleaned_data['mate_name']
            check_object.mate_id_number=self.cleaned_data['mate_id_number']
            check_object.mate_service_area_department=self.mate_service_area_department_object
            check_object.ctp_method = self.cleaned_data['ctp_method']
            check_object.ctp_method_time = self.cleaned_data['ctp_method_time']
            check_object.wedding_time = self.cleaned_data['wedding_time']
            check_object.address = self.cleaned_data['address'],
            check_object.children_1_name = self.cleaned_data['children_1_name'],
            check_object.children_1_sex = self.cleaned_data['children_2_sex'],
            check_object.children_1_id_number = self.cleaned_data['children_1_id_number'],
            check_object.children_2_name = self.cleaned_data['children_2_name'],
            check_object.children_2_sex = self.cleaned_data['children_2_sex'],
            check_object.children_2_id_number = self.cleaned_data['children_2_id_number'],
            check_object.children_3_name = self.cleaned_data['children_3_name'],
            check_object.children_3_sex = self.cleaned_data['children_3_sex'],
            check_object.children_3_id_number = self.cleaned_data['children_3_id_number'],
            check_object.creater = user
            check_object.save()
            return check_object
        return None
            

class CheckObjectModifyForm(forms.Form):
    """
    检查对象修改表单
    """

    id_object = None

    id = forms.CharField(
        widget=forms.HiddenInput(),
        error_messages = gl.check_object_name_error_messages,
        )
    
    def clean_id(self):
        try:
            try:
                id_copy = int(self.data.get('id'))
            except ValueError:
                raise forms.ValidationError(gl.check_object_name_error_messages['form_error'])
            self.id_object = CheckObject.objects.get(pk=id_copy, is_active=True)
#            print '************************'
#            print self.id_object.name
        except ObjectDoesNotExist:
            raise forms.ValidationError(gl.check_object_name_error_messages['form_error'])
        return id_copy

    def object(self):
        return self.id_object

class CheckObjectDetailModifyForm(forms.Form):
    """
    检查对象详细修改表单
    """
    id_object = None
    service_area_department_object = None
    mate_service_area_department_object = None
    ctp_method_time_copy = None
    wedding_time_copy = None

    name = forms.CharField(
        max_length=64,
        required=True, 
        label=_(u'妻子姓名(*)'), 
        widget=forms.TextInput(attrs={'class':'',
                                     'size':'30',
                                     }
                              ), 
        help_text=_(u'例如：张三、李四'),
        error_messages = gl.check_object_name_error_messages,
        )
    id_number = forms.CharField(
        max_length=18,
        required=True,
        label=_(u'身份证号(*)'),
        help_text=_(u'例如：360733199009130025'),
        error_messages = gl.check_object_id_number_error_messages,
        )
    service_area_name = forms.CharField(
        max_length=128,
        required=True,
        label=_(u'服务区域(*)'),
        widget=forms.TextInput(attrs={'class':'',
                                      'size':'30',}), 
        help_text=_(u'例如：西江镇、周田乡'),
        error_messages = gl.service_area_name_error_messages,
        )
    department_name = forms.CharField(
        max_length=128,
        required=True, 
        label=_(u'单位部门(*)'), 
        widget=forms.TextInput(attrs={'class':'',
                                     'size':'30',
                                     }
                              ), 
        help_text=_(u'例如：县委、政法委、公安局'),
        error_messages = gl.department_name_error_messages,
        )
    is_family = forms.CharField(
        required=True,
        label =_(u'家属(*)'),
        help_text=_(u'例如：对象没有单位则打勾'),
        widget=forms.CheckboxInput(attrs={'class':'',
                                          'value':'is_family',
                                          }, 
                                   check_test=None,
                                   ),
        )
    mate_name = forms.CharField(
        max_length=64,
        required=True,
        label=_(u'丈夫姓名(*)'),
        widget=forms.TextInput(attrs={'class':'',
                                     'size':'30',
                                     }
                              ), 
        help_text=_(u'例如：张三、李四'),
        error_messages = gl.check_object_name_error_messages,
        )
    mate_id_number = forms.CharField(
        max_length=18,
        required=False,
        label=_(u'身份证号'),
        help_text=_(u'例如：360733199009130025'),
        error_messages = gl.check_object_id_number_error_messages,
        )
    mate_service_area_name = forms.CharField(
        max_length=128,
        required=True,
        label=_(u'服务区域(*)'), 
        widget=forms.TextInput(attrs={'class':'',
                                      'size':'30',}), 
        help_text=_(u'例如：西江镇、周田乡'),
        error_messages = gl.service_area_name_error_messages,
        )
    mate_department_name = forms.CharField(
        max_length=128,
        required=True, 
        label=_(u'单位部门(*)'), 
        widget=forms.TextInput(attrs={'class':'',
                                     'size':'30',
                                     }
                              ), 
        help_text=_(u'例如：县委、政法委、公安局'),
        error_messages = gl.department_name_error_messages,
        )

    ctp_method = forms.ChoiceField(
        required=True,
        label =_(u'避孕措施'),
        choices=((u'method_0', u'未使用'),
                 (u'method_1', u'避孕环方式'),
                 (u'method_2', u'避孕药方式'),
                 (u'method_3', u'其他方式'),
                 ),
        help_text=_(u'例如：上环选避孕环方式'),
        )
    ctp_method_time = forms.DateField(
        required=False,
        label=_(u'实施时间'),
        help_text=_(u'例如：2010-10-25'),
        error_messages = gl.check_object_ctp_method_time_error_messages,
        input_formats = ('%Y-%m-%d',)
        )
    wedding_time = forms.DateField(
        required=False,
        label=_(u'结婚时间'),
        help_text=_(u'例如：1985-1-1'),
        error_messages = gl.check_object_wedding_time_error_messages,
        input_formats = ('%Y-%m-%d',)
        )
    address = forms.CharField(
        max_length=128,
        required=False,
        label=_(u'家庭住址'),
        widget=forms.TextInput(attrs={'class':'',
                                     'size':'30',
                                     }
                              ), 
        error_messages = gl.department_name_error_messages,
        )
    children_1_name = forms.CharField(
        max_length=64,
        required=False, 
        label=_(u'姓名'), 
        widget=forms.TextInput(attrs={'class':'',
                                     'size':'30',
                                     }
                              ), 
        error_messages = gl.check_object_name_error_messages,
        )
    children_1_sex = forms.ChoiceField(
        required=True,
        label =_(u'性别'),
        choices=((u'm', u'男'),
                 (u'w', u'女'),
                 ),
        )

    children_1_id_number = forms.CharField(
        max_length=18,
        required=False,
        label=_(u'身份证号'),
        error_messages = gl.check_object_id_number_error_messages,
        )
    children_2_name = forms.CharField(
        max_length=64,
        required=False, 
        label=_(u'姓名'), 
        widget=forms.TextInput(attrs={'class':'',
                                     'size':'30',
                                     }
                              ), 
        error_messages = gl.check_object_name_error_messages,
        )
    children_2_sex = forms.ChoiceField(
        required=True,
        label =_(u'性别'),
        choices=((u'm', u'男'),
                 (u'w', u'女'),
                 ),
        )

    children_2_id_number = forms.CharField(
        max_length=18,
        required=False,
        label=_(u'身份证号'),
        error_messages = gl.check_object_id_number_error_messages,
        )
    children_3_name = forms.CharField(
        max_length=64,
        required=False, 
        label=_(u'姓名'), 
        widget=forms.TextInput(attrs={'class':'',
                                     'size':'30',
                                     }
                              ), 
        error_messages = gl.check_object_name_error_messages,
        )
    children_3_sex = forms.ChoiceField(
        required=True,
        label =_(u'性别'),
        choices=((u'm', u'男'),
                 (u'w', u'女'),
                 ),
        )

    children_3_id_number = forms.CharField(
        max_length=18,
        required=False,
        label=_(u'身份证号'),
        error_messages = gl.check_object_id_number_error_messages,
        )

    id = forms.CharField(
        widget=forms.HiddenInput(),
        error_messages = gl.check_object_name_error_messages,
        )

    def clean_name(self):
        try:
            name_copy = self.data.get('name')
            if re.match(gl.check_object_name_add_re_pattern, name_copy) is None:
                raise forms.ValidationError(gl.check_object_name_error_messages['format_error'])
        except ObjectDoesNotExist:
            raise forms.ValidationError(gl.check_object_name_error_messages['form_error'])
        return name_copy
    def clean_id_number(self):
        try:
            id_number_copy = self.data.get('id_number')
        except ObjectDoesNotExist:
            raise forms.ValidationError(gl.check_object_id_number_error_messages['form_error'])
        if re.match(gl.check_object_id_number_add_re_pattern, id_number_copy) is None:
            raise forms.ValidationError(gl.check_object_id_number_error_messages['format_error'])
        return id_number_copy
    
    def clean_service_area_name(self):
        try:
           service_area_name_copy = self.data.get('service_area_name')
        except ObjectDoesNotExist:
            raise forms.ValidationError(gl.service_area_name_error_messages['form_error'])

        if re.match(gl.service_area_name_add_re_pattern, service_area_name_copy) is None:
            raise forms.ValidationError(gl.service_area_name_error_messages['format_error'])

        try:
            ServiceArea.objects.get(name=service_area_name_copy, is_active=True)
        except ObjectDoesNotExist:
            raise forms.ValidationError(gl.service_area_name_error_messages['not_exist_error'])

        return service_area_name_copy

    def clean_department_name(self):
        try:
            department_name_copy = self.data.get('department_name')
            service_area_name_copy = self.data.get('service_area_name')
        except ObjectDoesNotExist:
            raise forms.ValidationError(gl.department_name_error_messages['form_error'])
        if re.match(gl.department_name_add_re_pattern, department_name_copy) is None:
            raise forms.ValidationError(gl.department_name_error_messages['format_error'])
        try:
            department_object = Department.objects.get(name=department_name_copy, is_active=True)
        except ObjectDoesNotExist:
            raise forms.ValidationError(gl.department_name_error_messages['not_exist_error'])
        try:
            service_area_object = ServiceArea.objects.get(name=service_area_name_copy, is_active=True)
        except ObjectDoesNotExist:
            raise forms.ValidationError(gl.service_area_name_error_messages['not_exist_error'])
        try:
            self.service_area_department_object = ServiceAreaDepartment.objects.get(service_area=service_area_object, department=department_object)
        except ObjectDoesNotExist:
            raise forms.ValidationError(gl.department_name_error_messages['not_match_error'])
        return department_name_copy
    def clean_mate_name(self):
        try:
            mate_name_copy = self.data.get('mate_name')
            if re.match(gl.check_object_name_add_re_pattern, mate_name_copy) is None:
                raise forms.ValidationError(gl.check_object_name_error_messages['format_error'])
        except ObjectDoesNotExist:
            raise forms.ValidationError(gl.check_object_name_error_messages['form_error'])
        return mate_name_copy
    
    def clean_mate_id_number(self):
        try:
            mate_id_number_copy = self.data.get('mate_id_number')
        except ObjectDoesNotExist:
            raise forms.ValidationError(gl.check_object_id_number_error_messages['form_error'])
        if re.match(gl.check_object_id_number_add_re_pattern, mate_id_number_copy) is None:
            raise forms.ValidationError(gl.check_object_id_number_error_messages['format_error'])
        return mate_id_number_copy

    def clean_mate_service_area_name(self):
        try:
            mate_service_area_name_copy = self.data.get('mate_service_area_name')
        except ObjectDoesNotExist:
            raise forms.ValidationError(gl.service_area_name_error_messages['form_error'])

        if re.match(gl.service_area_name_add_re_pattern, mate_service_area_name_copy) is None:
            raise forms.ValidationError(gl.service_area_name_error_messages['format_error'])

        try:
            ServiceArea.objects.get(name=mate_service_area_name_copy, is_active=True)
        except ObjectDoesNotExist:
            raise forms.ValidationError(gl.service_area_name_error_messages['not_exist_error'])

        return mate_service_area_name_copy

    def clean_mate_department_name(self):
        try:
            mate_department_name_copy = self.data.get('mate_department_name')
            mate_service_area_name_copy = self.data.get('mate_service_area_name')
        except ObjectDoesNotExist:
            raise forms.ValidationError(gl.department_name_error_messages['form_error'])
        if re.match(gl.department_name_add_re_pattern, mate_department_name_copy) is None:
            raise forms.ValidationError(gl.department_name_error_messages['format_error'])
        try:
            mate_department_object = Department.objects.get(name=mate_department_name_copy, is_active=True)
        except ObjectDoesNotExist:
            raise forms.ValidationError(gl.department_name_error_messages['not_exist_error'])
        try:
            mate_service_area_object = ServiceArea.objects.get(name=mate_service_area_name_copy, is_active=True)
        except ObjectDoesNotExist:
            raise forms.ValidationError(gl.service_area_name_error_messages['not_exist_error'])
        try:
            self.mate_service_area_department_object = ServiceAreaDepartment.objects.get(service_area=mate_service_area_object, department=mate_department_object)
        except ObjectDoesNotExist:
            raise forms.ValidationError(gl.department_name_error_messages['not_match_error'])
        return mate_department_name_copy
        
    def clean_ctp_method_time(self):
        try:
            ctp_method_time_copy = self.cleaned_data.get('ctp_method_time')
        except ObjectDoesNotExist:
            raise forms.ValidationError(gl.check_project_ctp_method_time_error_messages['form_error'])
        if ctp_method_time_copy is not None:
            if ctp_method_time_copy > datetime.datetime.now().date():
                raise forms.ValidationError(gl.check_project_ctp_method_time_error_messages['logic_error'])
        return ctp_method_time_copy
    
    def clean_wedding_time(self):
        try:
            wedding_time_copy = self.cleaned_data.get('wedding_time')
#            print wedding_time_copy
        except ObjectDoesNotExist:
            raise forms.ValidationError(gl.check_object_wedding_time_error_messages['form_error'])
        if wedding_time_copy is not None:
            if wedding_time_copy > datetime.datetime.now().date():
                raise forms.ValidationError(gl.check_object_wedding_time_error_messages['logic_error'])
        return wedding_time_copy
    def clean_children_1_name(self):
        try:
            children_name_copy = self.data.get('children_1_name')
            if re.match(gl.check_object_name_search_re_pattern, children_name_copy) is None:
                raise forms.ValidationError(gl.check_object_name_error_messages['format_error'])
        except ObjectDoesNotExist:
            raise forms.ValidationError(gl.check_object_name_error_messages['form_error'])
        return children_name_copy
    
    def clean_children_1_id_number(self):
        try:
            children_id_number_copy = self.data.get('children_1_id_number')
        except ObjectDoesNotExist:
            raise forms.ValidationError(gl.check_object_id_number_error_messages['form_error'])
        if re.match(gl.check_object_id_number_search_re_pattern, children_id_number_copy) is None:
            raise forms.ValidationError(gl.check_object_id_number_error_messages['format_error'])
        return children_id_number_copy
    def clean_children_2_name(self):
        try:
            children_name_copy = self.data.get('children_2_name')
            if re.match(gl.check_object_name_search_re_pattern, children_name_copy) is None:
                raise forms.ValidationError(gl.check_object_name_error_messages['format_error'])
        except ObjectDoesNotExist:
            raise forms.ValidationError(gl.check_object_name_error_messages['form_error'])
        return children_name_copy
    
    def clean_children_2_id_number(self):
        try:
            children_id_number_copy = self.data.get('children_2_id_number')
        except ObjectDoesNotExist:
            raise forms.ValidationError(gl.check_object_id_number_error_messages['form_error'])
        if re.match(gl.check_object_id_number_search_re_pattern, children_id_number_copy) is None:
            raise forms.ValidationError(gl.check_object_id_number_error_messages['format_error'])
        return children_id_number_copy
    def clean_children_3_name(self):
        try:
            children_name_copy = self.data.get('children_3_name')
            if re.match(gl.check_object_name_search_re_pattern, children_name_copy) is None:
                raise forms.ValidationError(gl.check_object_name_error_messages['format_error'])
        except ObjectDoesNotExist:
            raise forms.ValidationError(gl.check_object_name_error_messages['form_error'])
        return children_name_copy
    
    def clean_children_3_id_number(self):
        try:
            children_id_number_copy = self.data.get('children_3_id_number')
        except ObjectDoesNotExist:
            raise forms.ValidationError(gl.check_object_id_number_error_messages['form_error'])
        if re.match(gl.check_object_id_number_search_re_pattern, children_id_number_copy) is None:
            raise forms.ValidationError(gl.check_object_id_number_error_messages['format_error'])
        return children_id_number_copy

    def clean_id(self):
        try:
            try:
                id_copy = int(self.data.get('id'))
            except ValueError:
                raise forms.ValidationError(gl.check_object_name_error_messages['form_error'])
            self.id_object = CheckObject.objects.get(pk=id_copy, is_active=True)
#            print '************************'
#            print self.id_object.name
        except ObjectDoesNotExist:
            raise forms.ValidationError(gl.check_object_name_error_messages['form_error'])
        return id_copy

    def data_from_object(self, modify_object=None, user=None):
#        gl.check_object_init_flag = True
        data = {}
        if modify_object is not None and user is not None:

            data['name'] = modify_object.name
            data['id_number'] = modify_object.id_number
            if user.has_perm('department.unlocal'):
                data['service_area_name'] = modify_object.service_area_department.service_area.name
            else:
                data['service_area_name'] = user.get_profile().service_area_department.service_area.name
            
            data['department_name'] = modify_object.service_area_department.department.name
            if modify_object.is_family is True:
                data['is_family'] = u'is_family'
            else:
                data['is_family'] = False
            data['mate_name'] = modify_object.mate_name
            data['mate_id_number'] = modify_object.mate_id_number
            data['mate_service_area_name'] = modify_object.mate_service_area_department.service_area.name
            data['mate_department_name'] = modify_object.mate_service_area_department.department.name
            data['ctp_method'] = modify_object.ctp_method
            data['address'] = modify_object.address
            data['children_1_name'] = modify_object.children_1_name
            data['children_1_sex'] = modify_object.children_1_sex
            data['children_1_id_number'] = modify_object.children_1_id_number
            data['children_2_name'] = modify_object.children_2_name
            data['children_2_sex'] = modify_object.children_2_sex
            data['children_2_id_number'] = modify_object.children_2_id_number
            data['children_3_name'] = modify_object.children_3_name
            data['children_3_sex'] = modify_object.children_3_sex
            data['children_3_id_number'] = modify_object.children_3_id_number
            if modify_object.ctp_method_time is not None:
                data['ctp_method_time'] = modify_object.ctp_method_time.isoformat()
            else:
                data['ctp_method_time'] = u''
            if modify_object.wedding_time is not None:
                data['wedding_time'] = modify_object.wedding_time.isoformat()
            else:
                data['wedding_time'] = u''
            if modify_object.is_family is True:
                data['is_family'] = u'is_family'
            else:
                data['is_family'] = False
            data['id'] = modify_object.id
        else:
            pass
        return data


    def init_from_object(self, modify_object=None, user=None):
        if modify_object is not None and user is not None:
            self.fields['name'].widget.attrs['value'] = modify_object.name
            self.fields['id_number'].widget.attrs['value'] = modify_object.id_number
            if user.has_perm('department.unlocal'):
                self.fields['service_area_name'].widget.attrs['value'] = modify_object.service_area_department.service_area.name
            else:
                self.fields['service_area_name'].widget.attrs['value'] = user.get_profile().service_area_department.service_area.name
                self.fields['service_area_name'].widget.attrs['readonly'] = True

            self.fields['department_name'].widget.attrs['value'] = modify_object.service_area_department.department.name
            self.fields['mate_name'].widget.attrs['value'] = modify_object.mate_name
            self.fields['mate_id_number'].widget.attrs['value'] = modify_object.mate_id_number
            self.fields['mate_service_area_name'].widget.attrs['value'] = modify_object.mate_service_area_department.service_area.name
            self.fields['mate_department_name'].widget.attrs['value'] = modify_object.mate_service_area_department.department.name
            self.fields['ctp_method'].widget.attrs['value'] = modify_object.ctp_method
            self.fields['address'].widget.attrs['value'] = modify_object.address
            self.fields['children_1_name'].widget.attrs['value'] = modify_object.children_1_name
            self.fields['children_1_sex'].widget.attrs['value'] = modify_object.children_1_sex
            self.fields['children_1_id_number'].widget.attrs['value'] = modify_object.children_1_id_number
            self.fields['children_2_name'].widget.attrs['value'] = modify_object.children_2_name
            self.fields['children_2_sex'].widget.attrs['value'] = modify_object.children_2_sex
            self.fields['children_2_id_number'].widget.attrs['value'] = modify_object.children_2_id_number
            self.fields['children_3_name'].widget.attrs['value'] = modify_object.children_3_name
            self.fields['children_3_sex'].widget.attrs['value'] = modify_object.children_3_sex
            self.fields['children_3_id_number'].widget.attrs['value'] = modify_object.children_3_id_number
            if modify_object.ctp_method_time is not None:
                self.fields['ctp_method_time'].widget.attrs['value'] = modify_object.ctp_method_time.isoformat()
            else:
                self.fields['ctp_method_time'].widget.attrs['value'] = u''
            if modify_object.wedding_time is not None:
                self.fields['wedding_time'].widget.attrs['value'] = modify_object.wedding_time.isoformat()
            else:
                self.fields['wedding_time'].widget.attrs['value'] = u''
            self.fields['id'].widget.attrs['value'] = modify_object.id
            is_family = modify_object.is_family
            if is_family is True:
                self.fields['is_family'].widget.attrs['checked'] = u'true'
            else:
                pass
            return True
        else:

            return False
    
    def detail_modify(self, request):
        
        check_object = self.id_object
        if request is None:
            return None
        if request.session.get(gl.session_check_object_detail_modify_uploader, u'') == request.user.username:
            try:
                file_temp = default_storage.open(u'images/photos/temp/%s.temp' % request.user.username)
            except IOError:
                return None
            file_path = u'images/photos/%s.jpg' % self.cleaned_data['id_number']
            default_storage.delete(file_path)
            file_temp_name = file_temp.name.decode('utf-8').replace('\\', '/')
            font = ImageFont.truetype('%s/static/fonts/MSYH.TTF' % settings.CURRENT_PATH,12)
            try:
                img = Image.open(file_temp_name)
            except IOError:
                img = Image.open('%s/static/images/photo.jpg' % settings.CURRENT_PATH)
                if img.mode != "RGB":
                    img = img.convert("RGB")
                img.resize(gl.check_object_image_size,Image.ANTIALIAS)
            draw = ImageDraw.Draw(img)
            draw.rectangle([gl.check_object_id_mark, gl.check_object_image_size], fill=gl.check_object_id_mark_bottom_color)
            draw.text(gl.check_object_id_mark, u'%s %s' % (self.cleaned_data['name'], self.cleaned_data['id_number']) ,gl.check_object_id_mark_color,font=font)
            del draw
            img.save(file_temp_name,"JPEG")

            default_storage.save(file_path, file_temp)
            file_temp.close()
            del img
            del file_temp
            request.session[gl.session_check_object_detail_modify_uploader] = u''

        if self.cleaned_data['is_family'] == u'is_family':
            is_family_value = True
        else:
            is_family_value = False

        check_object.is_active =True
        check_object.name=self.cleaned_data['name']
        check_object.photo=file_path
        check_object.id_number=self.cleaned_data['id_number']
        check_object.service_area_department=self.service_area_department_object
        check_object.is_family=is_family_value
        check_object.mate_name=self.cleaned_data['mate_name']
        check_object.mate_id_number=self.cleaned_data['mate_id_number']
        check_object.mate_service_area_department=self.mate_service_area_department_object
        check_object.ctp_method = self.cleaned_data['ctp_method']
        check_object.ctp_method_time = self.cleaned_data['ctp_method_time']
        check_object.wedding_time = self.cleaned_data['wedding_time']
        check_object.address = self.cleaned_data['address']
        check_object.children_1_name = self.cleaned_data['children_1_name']
        check_object.children_1_sex = self.cleaned_data['children_1_sex']
        check_object.children_1_id_number = self.cleaned_data['children_1_id_number']
        check_object.children_2_name = self.cleaned_data['children_2_name']
        check_object.children_2_sex = self.cleaned_data['children_2_sex']
        check_object.children_2_id_number = self.cleaned_data['children_2_id_number']
        check_object.children_3_name = self.cleaned_data['children_3_name']
        check_object.children_3_sex = self.cleaned_data['children_3_sex']
        check_object.children_3_id_number = self.cleaned_data['children_3_id_number']
        check_object.save()
        return check_object

class CheckObjectDeleteForm(forms.Form):
    """
    检查对象删除表单
    """
    id_object = None

    id = forms.CharField(
        widget=forms.HiddenInput(),
        error_messages = gl.check_object_name_error_messages,
        )
    
    def clean_id(self):
        try:
            try:
                id_copy = int(self.data.get('id'))
            except ValueError:
                raise forms.ValidationError(gl.check_object_name_error_messages['form_error'])
            self.id_object = CheckObject.objects.get(pk=id_copy, is_active=True)
        except ObjectDoesNotExist:
            raise forms.ValidationError(gl.check_object_name_error_messages['form_error'])
        try:
            check_project = CheckProject.objects.get(is_setup=True, is_active=True)
        except ObjectDoesNotExist:
            check_project = None
        try:
            CheckResult.objects.get(check_object=self.id_object, check_project=check_project)
        except ObjectDoesNotExist:
            return id_copy
        raise forms.ValidationError(u'该检查对象在此次检查项目中已经检查，无法删除该对象！')
    
    def delete(self):
        if self.id_object is not None:
            self.id_object.is_active = False
            self.id_object.save()
            return True
        else:
            return False

class CheckObjectRestoreForm(forms.Form):
    """
    检查对象恢复表单
    """
    id_object = None

    id = forms.CharField(
        widget=forms.HiddenInput(),
        error_messages = gl.check_object_name_error_messages,
        )
    
    def clean_id(self):
        try:
            try:
                id_copy = int(self.data.get('id'))
            except ValueError:
                raise forms.ValidationError(gl.check_object_name_error_messages['form_error'])
            self.id_object = CheckObject.objects.get(pk=id_copy, is_active=False)
        except ObjectDoesNotExist:
            raise forms.ValidationError(gl.check_object_name_error_messages['form_error'])
        return id_copy

    def restore(self):
        if self.id_object is not None:
            self.id_object.is_active = True
            self.id_object.save()
            return True
        else:
            return False

class CheckObjectSearchForm(forms.Form):
    """
    检查对象搜索表单
    """
    is_fuzzy = False
    name = forms.CharField(
        max_length=64,
        required=False, 
        label=_(u'妻子姓名'), 
        widget=forms.TextInput(attrs={'class':'',
                                     'size':'30',
                                     }
                              ), 
        help_text=_(u'例如：张三、李四'),
        error_messages = gl.check_object_name_error_messages,
        )
    id_number = forms.CharField(
        max_length=18,
        required=False,
        label=_(u'身份证号'),
        help_text=_(u'例如：360733199009130025'),
        error_messages = gl.check_object_id_number_error_messages,
        )
    service_area_name = forms.CharField(
        max_length=128,
        required=False,
        label=_(u'服务区域'),
        widget=forms.TextInput(attrs={'class':'',
                                      'size':'30',}), 
        help_text=_(u'例如：西江镇、周田乡'),
        error_messages = gl.service_area_name_error_messages,
        )
    department_name = forms.CharField(
        max_length=128,
        required=False, 
        label=_(u'单位部门'), 
        widget=forms.TextInput(attrs={'class':'',
                                     'size':'30',
                                     }
                              ), 
        help_text=_(u'例如：县委、政法委、公安局'),
        error_messages = gl.department_name_error_messages,
        )
    is_family = forms.ChoiceField(
        required=True,
        label =_(u'家属'),
        help_text=_(u' '),
        choices=((u'none', u'未知'),
                 (u'true', u'是'),
                 (u'false', u'否'),
                 ),
        )

    mate_name = forms.CharField(
        max_length=64,
        required=False,
        label=_(u'丈夫姓名'),
        widget=forms.TextInput(attrs={'class':'',
                                     'size':'30',
                                     }
                              ), 
        help_text=_(u'例如：张三、李四'),
        error_messages = gl.check_object_name_error_messages,
        )
    mate_id_number = forms.CharField(
        max_length=18,
        required=False,
        label=_(u'身份证号'),
        help_text=_(u'例如：360733199009130025'),
        error_messages = gl.check_object_id_number_error_messages,
        )
    mate_service_area_name = forms.CharField(
        max_length=128,
        required=False,
        label=_(u'服务区域'), 
        widget=forms.TextInput(attrs={'class':'',
                                      'size':'30',}), 
        help_text=_(u'例如：西江镇、周田乡'),
        error_messages = gl.service_area_name_error_messages,
        )
    mate_department_name = forms.CharField(
        max_length=128,
        required=False, 
        label=_(u'单位部门'), 
        widget=forms.TextInput(attrs={'class':'',
                                     'size':'30',
                                     }
                              ), 
        help_text=_(u'例如：县委、政法委、公安局'),
        error_messages = gl.department_name_error_messages,
        )

    ctp_method = forms.ChoiceField(
        required=True,
        label =_(u'避孕措施'),
        choices=((u'none', u'未知'),
                 (u'method_0', u'未使用'),
                 (u'method_1', u'避孕环方式'),
                 (u'method_2', u'避孕药方式'),
                 (u'method_3', u'其他方式'),
                 ),
        help_text=_(u'例如：上环选避孕环方式'),
        )
    ctp_method_time = forms.DateField(
        required=False,
        label=_(u'实施时间'),
        help_text=_(u'例如：2010-10-25'),
        error_messages = gl.check_object_ctp_method_time_error_messages,
        input_formats = ('%Y-%m-%d',)
        )
    wedding_time = forms.DateField(
        required=False,
        label=_(u'结婚时间'),
        help_text=_(u'例如：1985-1-1'),
        error_messages = gl.check_object_wedding_time_error_messages,
        input_formats = ('%Y-%m-%d',)
        )
    modify_start_time = forms.DateField(
        required=False,
        label=_(u'修改开始时间'),
        help_text=_(u'例如：2010-10-25'),
        input_formats = ('%Y-%m-%d',)
        )
    modify_end_time  = forms.DateField(
        required=False,
        label=_(u'修改结束时间'),
        help_text=_(u'例如：2010-10-25'),
        input_formats = ('%Y-%m-%d',)
        )

    is_fuzzy = forms.CharField(
        required=True,
        label =_(u'模糊查询'),
        widget=forms.CheckboxInput(attrs={'class':'',
                                          'value':'is_fuzzy',
                                          }, 
                                   check_test=None,
                                   ),
        help_text=_(u' '),
        )
    def clean_name(self):
        try:
            name_copy = self.data.get('name')
            if re.match(gl.check_object_name_search_re_pattern, name_copy) is None:
                raise forms.ValidationError(gl.check_object_name_error_messages['format_error'])
        except ObjectDoesNotExist:
            raise forms.ValidationError(gl.check_object_name_error_messages['form_error'])
        return name_copy
    
    def clean_id_number(self):
        try:
            id_number_copy = self.data.get('id_number')
        except ObjectDoesNotExist:
            raise forms.ValidationError(gl.check_object_id_number_error_messages['form_error'])
        if re.match(gl.check_object_id_number_search_re_pattern, id_number_copy) is None:
            raise forms.ValidationError(gl.check_object_id_number_error_messages['format_error'])
        return id_number_copy
    def clean_service_area_name(self):
        try:
           service_area_name_copy = self.data.get('service_area_name')
        except ObjectDoesNotExist:
            raise forms.ValidationError(gl.service_area_name_error_messages['form_error'])

        if re.match(gl.service_area_name_search_re_pattern, service_area_name_copy) is None:
            raise forms.ValidationError(gl.service_area_name_error_messages['format_error'])

        return service_area_name_copy

    def clean_department_name(self):
        try:
            department_name_copy = self.data.get('department_name')
        except ObjectDoesNotExist:
            raise forms.ValidationError(gl.department_name_error_messages['form_error'])
        if re.match(gl.department_name_search_re_pattern, department_name_copy) is None:
            raise forms.ValidationError(gl.department_name_error_messages['format_error'])
        return department_name_copy

    def clean_mate_name(self):
        try:
            mate_name_copy = self.data.get('mate_name')
            if re.match(gl.check_object_name_search_re_pattern, mate_name_copy) is None:
                raise forms.ValidationError(gl.check_object_name_error_messages['format_error'])
        except ObjectDoesNotExist:
            raise forms.ValidationError(gl.check_object_name_error_messages['form_error'])
        return mate_name_copy
    
    def clean_mate_id_number(self):
        try:
            mate_id_number_copy = self.data.get('mate_id_number')
        except ObjectDoesNotExist:
            raise forms.ValidationError(gl.check_object_id_number_error_messages['form_error'])
        if re.match(gl.check_object_id_number_search_re_pattern, mate_id_number_copy) is None:
            raise forms.ValidationError(gl.check_object_id_number_error_messages['format_error'])
        return mate_id_number_copy

    def clean_mate_service_area_name(self):
        try:
           mate_service_area_name_copy = self.data.get('mate_service_area_name')
        except ObjectDoesNotExist:
            raise forms.ValidationError(gl.service_area_name_error_messages['form_error'])

        if re.match(gl.service_area_name_search_re_pattern, mate_service_area_name_copy) is None:
            raise forms.ValidationError(gl.service_area_name_error_messages['format_error'])
        return mate_service_area_name_copy

    def clean_mate_department_name(self):
        try:
            mate_department_name_copy = self.data.get('mate_department_name')
        except ObjectDoesNotExist:
            raise forms.ValidationError(gl.department_name_error_messages['form_error'])
        if re.match(gl.department_name_search_re_pattern, mate_department_name_copy) is None:
            raise forms.ValidationError(gl.department_name_error_messages['format_error'])
        return mate_department_name_copy
    
    def clean_ctp_method_time(self):
        try:
            ctp_method_time_copy = self.cleaned_data.get('ctp_method_time')
        except ObjectDoesNotExist:
            raise forms.ValidationError(gl.check_project_ctp_method_time_error_messages['form_error'])
        if ctp_method_time_copy is not None:
            if ctp_method_time_copy > datetime.datetime.now().date():
                raise forms.ValidationError(gl.check_project_ctp_method_time_error_messages['logic_error'])
        return ctp_method_time_copy
    def clean_wedding_time(self):
        try:
            wedding_time_copy = self.cleaned_data.get('wedding_time')
        except ObjectDoesNotExist:
            raise forms.ValidationError(gl.check_object_wedding_time_error_messages['form_error'])
        if wedding_time_copy is not None:
            if wedding_time_copy > datetime.datetime.now().date():
                raise forms.ValidationError(gl.check_object_wedding_time_error_messages['logic_error'])
        return wedding_time_copy
    
    def data_to_session(self, request):
        request.session[gl.session_check_object_name] = self.cleaned_data['name']
        request.session[gl.session_check_object_id_number] = self.cleaned_data['id_number']
        if request.user.has_perm('department.unlocal'):
            request.session[gl.session_check_object_service_area_name] = self.cleaned_data['service_area_name']
        else:
            request.session[gl.session_check_object_service_area_name] = request.user.get_profile().service_area_department.service_area.name
        
        request.session[gl.session_check_object_department_name] = self.cleaned_data['department_name']
        request.session[gl.session_check_object_is_family] = self.cleaned_data['is_family']
        request.session[gl.session_check_object_mate_name] = self.cleaned_data['mate_name']
        request.session[gl.session_check_object_mate_id_number] = self.cleaned_data['mate_id_number']
        request.session[gl.session_check_object_mate_service_area_name] = self.cleaned_data['mate_service_area_name']
        request.session[gl.session_check_object_mate_department_name] = self.cleaned_data['mate_department_name']
        request.session[gl.session_check_object_ctp_method] = self.cleaned_data['ctp_method']
        if self.cleaned_data['ctp_method_time'] is not None:
            request.session[gl.session_check_object_ctp_method_time] = self.cleaned_data['ctp_method_time'].isoformat()
        else:
            request.session[gl.session_check_object_ctp_method_time] = u''
        if self.cleaned_data['wedding_time'] is not None:
            request.session[gl.session_check_object_wedding_time] = self.cleaned_data['wedding_time'].isoformat()
        else:
            request.session[gl.session_check_object_wedding_time] = u''
        is_fuzzy = self.cleaned_data['is_fuzzy']
#        print is_fuzzy
        if is_fuzzy == u'is_fuzzy':
#            print u'true'
            request.session[gl.session_check_object_is_fuzzy] = is_fuzzy
        else:
#            print u'false'
            request.session[gl.session_check_object_is_fuzzy] = False
        if self.cleaned_data['modify_start_time'] is not None:
            request.session[gl.session_check_object_modify_start_time] = self.cleaned_data['modify_start_time'].isoformat()
        else:
            request.session[gl.session_check_object_modify_start_time] = u''
        if self.cleaned_data['modify_end_time'] is not None:
            request.session[gl.session_check_object_modify_end_time] = self.cleaned_data['modify_end_time'].isoformat()
        else:
            request.session[gl.session_check_object_modify_end_time] = u''

        return True
    
    def data_from_session(self, request):
        data = {}
        data['name'] = request.session.get(gl.session_check_object_name, u'')
        data['id_number'] = request.session.get(gl.session_check_object_id_number, u'')
        
        if request.user.has_perm('department.unlocal'):
            data['service_area_name'] = request.session.get(gl.session_check_object_service_area_name, u'')
        else:
            data['service_area_name'] = request.user.get_profile().service_area_department.service_area.name

        data['department_name'] = request.session.get(gl.session_check_object_department_name, u'')
        data['is_family'] = request.session.get(gl.session_check_object_is_family, u'none')
        data['mate_name'] = request.session.get(gl.session_check_object_mate_name, u'')
        data['mate_id_number'] = request.session.get(gl.session_check_object_mate_id_number, u'')
        data['mate_service_area_name'] = request.session.get(gl.session_check_object_mate_service_area_name, u'')
        data['mate_department_name'] = request.session.get(gl.session_check_object_mate_department_name, u'')
        data['ctp_method'] = request.session.get(gl.session_check_object_ctp_method, u'none')
        data['ctp_method_time'] = request.session.get(gl.session_check_object_ctp_method_time, u'')
        data['wedding_time'] = request.session.get(gl.session_check_object_wedding_time, u'')
        data['modify_start_time'] = request.session.get(gl.session_check_object_modify_start_time, u'')
        data['modify_end_time'] = request.session.get(gl.session_check_object_modify_end_time, u'')
        data['is_fuzzy'] = request.session.get(gl.session_check_object_is_fuzzy, False)

#        print data['is_fuzzy']
        return data
    def init_from_session(self, request):
        self.fields['name'].widget.attrs['value'] = request.session.get(gl.session_check_object_name, u'')
        self.fields['id_number'].widget.attrs['value'] = request.session.get(gl.session_check_object_id_number, u'')
        if request.user.has_perm('department.unlocal'):
            self.fields['service_area_name'].widget.attrs['value'] = request.session.get(gl.session_check_object_service_area_name, u'')
        else:
            self.fields['service_area_name'].widget.attrs['value'] = request.user.get_profile().service_area_department.service_area.name
            self.fields['service_area_name'].widget.attrs['readonly'] = True
        
        self.fields['department_name'].widget.attrs['value'] = request.session.get(gl.session_check_object_department_name, u'')
        self.fields['is_family'].widget.attrs['value'] = request.session.get(gl.session_check_object_is_family, u'none')
        self.fields['mate_name'].widget.attrs['value'] = request.session.get(gl.session_check_object_mate_name, u'')
        self.fields['mate_id_number'].widget.attrs['value'] = request.session.get(gl.session_check_object_mate_id_number, u'')
        self.fields['mate_service_area_name'].widget.attrs['value'] = request.session.get(gl.session_check_object_mate_service_area_name, u'')
        self.fields['mate_department_name'].widget.attrs['value'] = request.session.get(gl.session_check_object_mate_department_name, u'')
        self.fields['ctp_method'].widget.attrs['value'] = request.session.get(gl.session_check_object_ctp_method, u'none')
        self.fields['ctp_method_time'].widget.attrs['value'] = request.session.get(gl.session_check_object_ctp_method_time, u'')
        self.fields['wedding_time'].widget.attrs['value'] = request.session.get(gl.session_check_object_wedding_time, u'')
        self.fields['modify_start_time'].widget.attrs['value'] = request.session.get(gl.session_check_object_modify_start_time, u'')
        self.fields['modify_end_time'].widget.attrs['value'] = request.session.get(gl.session_check_object_modify_end_time, u'')
        is_fuzzy = request.session.get(gl.session_check_object_is_fuzzy, False)
        if is_fuzzy == u'is_fuzzy':
            self.fields['is_fuzzy'].widget.attrs['checked'] = u'true'
        else:
            pass
        return True
    
    def query_name(self, query_set=None):
        name = self.cleaned_data['name']
        is_fuzzy = self.is_fuzzy
        
        if query_set is None:
            return query_set

        if name == u'':
            pass
        else:
            if is_fuzzy is False:
                query_set = query_set.filter(name__startswith=name)
            else:
                query_set = query_set.filter(name__icontains=name)
                
        return query_set

    def query_id_number(self, query_set=None):
        id_number = self.cleaned_data['id_number']
        is_fuzzy = self.is_fuzzy

        if query_set is None:
            return query_set

        if id_number == u'':
            pass
        else:
            if is_fuzzy is False:
                query_set = query_set.filter(id_number__startswith=id_number)
            else:
                query_set = query_set.filter(id_number__icontains=id_number)

        return query_set
    
    def query_service_area_name(self, query_set=None):
        service_area_name = self.cleaned_data['service_area_name']
        is_fuzzy = self.is_fuzzy

        if query_set is None:
            return query_set

        if service_area_name == u'':
            pass
        else:
            if is_fuzzy is False:
                query_set = query_set.filter(service_area_department__service_area__name__startswith=service_area_name)
            else:
                query_set = query_set.filter(service_area_department__service_area__name__icontains=service_area_name)

        return query_set
    
    def query_department_name(self, query_set=None):
        department_name = self.cleaned_data['department_name']
        is_fuzzy = self.is_fuzzy

        if query_set is None:
            return query_set

        if department_name == u'':
            pass
        else:
            if is_fuzzy is False:
                query_set = query_set.filter(service_area_department__department__name__startswith=department_name)
            else:
                query_set = query_set.filter(service_area_department__department__name__icontains=department_name)

        return query_set

    def query_is_family(self, query_set=None):
        is_family = self.cleaned_data['is_family']

        if query_set is None:
            return query_set
        
        if is_family == u'true':
            query_set = query_set.filter(is_family=True)
        else:
            if is_family == u'false':
                query_set = query_set.filter(is_family=False)
            else:
                if is_family == u'none':
                    pass
                else:
                    pass

        return query_set

    def query_mate_name(self, query_set=None):
        mate_name = self.cleaned_data['mate_name']
        is_fuzzy = self.is_fuzzy
        
        if query_set is None:
            return query_set

        if mate_name == u'':
            pass
        else:
            if is_fuzzy is False:
                query_set = query_set.filter(mate_name__startswith=mate_name)
            else:
                query_set = query_set.filter(mate_name__icontains=mate_name)
                
        return query_set

    def query_mate_id_number(self, query_set=None):
        mate_id_number = self.cleaned_data['mate_id_number']
        is_fuzzy = self.is_fuzzy

        if query_set is None:
            return query_set

        if mate_id_number == u'':
            pass
        else:
            if is_fuzzy is False:
                query_set = query_set.filter(mate_id_number__startswith=mate_id_number)
            else:
                query_set = query_set.filter(mate_id_number__icontains=mate_id_number)

        return query_set
    
    def query_mate_service_area_name(self, query_set=None):
        mate_service_area_name = self.cleaned_data['mate_service_area_name']
        is_fuzzy = self.is_fuzzy

        if query_set is None:
            return query_set

        if mate_service_area_name == u'':
            pass
        else:
            if is_fuzzy is False:
                query_set = query_set.filter(mate_service_area_department__service_area__name__startswith=mate_service_area_name)
            else:
                query_set = query_set.filter(mate_service_area_department__service_area__name__icontains=mate_service_area_name)

        return query_set
    
    def query_mate_department_name(self, query_set=None):
        mate_department_name = self.cleaned_data['mate_department_name']
        is_fuzzy = self.is_fuzzy

        if query_set is None:
            return query_set

        if mate_department_name == u'':
            pass
        else:
            if is_fuzzy is False:
                query_set = query_set.filter(mate_service_area_department__department__name__startswith=mate_department_name)
            else:
                query_set = query_set.filter(mate_service_area_department__department__name__icontains=mate_department_name)

        return query_set

    def query_ctp_method(self, query_set=None):
        ctp_method = self.cleaned_data['ctp_method']

        if query_set is None:
            return query_set
        
        if ctp_method == u'none':
            pass
        else:
            query_set = query_set.filter(ctp_method=ctp_method)
            
        return query_set
    
    def query_ctp_method_time(self, query_set=None):
        ctp_method_time = self.cleaned_data['ctp_method_time']

        if query_set is None:
            return query_set

        if ctp_method_time == None:
            pass
        else:
            query_set = query_set.filter(ctp_method_time=ctp_method_time)
            
        return query_set
    
    def query_wedding_time(self, query_set=None):
        wedding_time = self.cleaned_data['wedding_time']

        if query_set is None:
            return query_set

        if wedding_time == None:
            pass
        else:
            query_set = query_set.filter(wedding_time=wedding_time)
        
        return query_set

    def query_modify_start_time(self, query_set=None):
        start_time = self.cleaned_data['modify_start_time']

        if query_set is None:
            return query_set

        if start_time == None:
            pass
        else:
            start_time = datetime.datetime(start_time.year, start_time.month, start_time.day)
            query_set = query_set.filter(updated_at__gte=start_time)
        
        return query_set
    def query_modify_end_time(self, query_set=None):
        end_time = self.cleaned_data['modify_end_time']
        if query_set is None:
            return query_set

        if end_time == None:
            pass
        else:
            end_time = datetime.datetime(end_time.year, end_time.month, end_time.day, 23, 59, 59)
            query_set = query_set.filter(updated_at__lte=end_time)
        return query_set

    
    def search(self):

        if self.cleaned_data['is_fuzzy'] == u'is_fuzzy':
            self.is_fuzzy = True
        else:
            self.is_fuzzy = False

        query_set = CheckObject.objects.filter(is_active=True)
        
        query_set = self.query_name(query_set)
        query_set = self.query_id_number(query_set)
        query_set = self.query_mate_name(query_set)
        query_set = self.query_mate_id_number(query_set)
        query_set = self.query_service_area_name(query_set)
        query_set = self.query_department_name(query_set)
        query_set = self.query_mate_service_area_name(query_set)
        query_set = self.query_mate_department_name(query_set)
        query_set = self.query_ctp_method(query_set)
        query_set = self.query_is_family(query_set)
        query_set = self.query_ctp_method_time(query_set)
        query_set = self.query_wedding_time(query_set)
        query_set = self.query_modify_start_time(query_set)
        query_set = self.query_modify_end_time(query_set)
        
        return query_set

    def unsearch(self):

        if self.cleaned_data['is_fuzzy'] == u'is_fuzzy':
            self.is_fuzzy = True
        else:
            self.is_fuzzy = False

        query_set = CheckObject.objects.filter(is_active=False)
        
        query_set = self.query_name(query_set)
        query_set = self.query_id_number(query_set)
        query_set = self.query_mate_name(query_set)
        query_set = self.query_mate_id_number(query_set)
        query_set = self.query_service_area_name(query_set)
        query_set = self.query_department_name(query_set)
        query_set = self.query_mate_service_area_name(query_set)
        query_set = self.query_mate_department_name(query_set)
        query_set = self.query_ctp_method(query_set)
        query_set = self.query_is_family(query_set)
        query_set = self.query_ctp_method_time(query_set)
        query_set = self.query_wedding_time(query_set)
        query_set = self.query_modify_start_time(query_set)
        query_set = self.query_modify_end_time(query_set)
        
        return query_set
    


