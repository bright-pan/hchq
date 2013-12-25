import pymssql
import datetime
from django.contrib.auth.models import *
from service_area.models import *
from department.models import *
from check_object.models import *
import Image
from django.core.files.storage import default_storage
import settings
from untils import gl
from django.db.models import ObjectDoesNotExist

conn = pymssql.connect(host='192.168.0.167',user='sa',password='',database='HCHQ')
cur = conn.cursor()
cur.execute('select a.QiZXM name ,a.qizsfzh id_number,a.zhangfxm mate_name,a.zhinxx children,a.jiatzz address,a.zhaoplj photo_name, a.jiehsj wedding_time, a.Jias is_family , a.ZhangFsfz mate_id_number,b.FuWQMC service_area_name,e.fuwqmc mate_service_area_name,c.dianwmc department_name,d.dianwmc mate_department_name from GeRXX a ,FuWuQu b,FuWuQu e,DanWXX c,DanWXX d where a.FuWQ = b.FuWQBM and a.DianWBH=c.DianBH and a.zhangdwbh=d.dianbh and a.ZhangFwq = e.FuWQBM and a.QiY = 1')
query_set = cur.fetchall_asdict()

for row in query_set:
    try:
        name = row['name'].strip().decode('gb2312')
    except UnicodeDecodeError:
        name = row['name'].strip().decode('gbk')
    try:
        id_number = row['id_number'].strip().decode('gb2312')
    except UnicodeDecodeError:
        id_number = row['id_number'].strip().decode('gbk')
    try:
        mate_name = row['mate_name'].strip().decode('gb2312')
    except UnicodeDecodeError:
        mate_name = row['mate_name'].strip().decode('gbk')
    try:
        mate_id_number = row['mate_id_number'].strip().decode('gb2312')
    except UnicodeDecodeError:
        mate_id_number = row['mate_id_number'].strip().decode('gbk')
    is_family = row['is_family']
    try:
        address = row['address'].strip().decode('gb2312')
    except UnicodeDecodeError:
        address = row['address'].strip().decode('gbk')
    ctp_method = u'method_0'
    ctp_method_time = None
    try:
        wt = row['wedding_time'].strip().decode('gb2312')
    except UnicodeDecodeError:
        wt = row['wedding_time'].strip().decode('gbk')
    if wt ==u'':
        wedding_time=None
    else:
        wt_list = wt.split(u'-')
        wedding_time = datetime.date(int(wt_list[0]),int(wt_list[1]),int(wt_list[2]))
    children_1_name =u''
    children_1_sex = u'm'
    children_1_id_number = u''
    children_2_name =u''
    children_2_sex = u'm'
    children_3_id_number = u''
    children_2_id_number = u''
    children_3_name =u''
    children_3_id_number = u''
    children_3_sex = u'm'
    try:    
        children = row['children'].strip().decode('gb2312')
    except UnicodeDecodeError:
        children = row['children'].strip().decode('gbk')
    if children == u'':
        pass
    else:
        children_list = children.split(u';')
        num = len(children_list)
        if num == 1:
            children_info_list = children_list[0].split(u'-')
            children_1_name = children_info_list[0]
            if children_info_list[1] == u'0':
                children_1_sex = u'm'
            else:
                children_1_sex = u'w'
                children_1_id_number = children_info_list[2]
        else:
            children_info_list = children_list[0].split(u'-')
            children_1_name = children_info_list[0]
            if children_info_list[1] == u'0':
                children_1_sex = u'm'
            else:
                children_1_sex = u'w'
                children_1_id_number = children_info_list[2]
                children_info_list = children_list[1].split(u'-')
                children_2_name = children_info_list[0]
            if children_info_list[1] == u'0':
                children_2_sex = u'm'
            else:
                children_2_sex = u'w'
                children_2_id_number = children_info_list[2]
    creater = User.objects.get(pk=1)
    try:
        service_area_name = row['service_area_name'].strip().decode('gb2312')
    except UnicodeDecodeError:
        service_area_name = row['service_area_name'].strip().decode('gbk')
    service_area, created = ServiceArea.objects.get_or_create(name=service_area_name, creater=creater)
    try:
        department_name = row['department_name'].strip().decode('gb2312')
    except UnicodeDecodeError:
        department_name = row['department_name'].strip().decode('gbk')
    department, created = Department.objects.get_or_create(name=department_name,creater = creater)
    service_area_department, created = ServiceAreaDepartment.objects.get_or_create(service_area=service_area, department=department)
    try:
        mate_service_area_name = row['mate_service_area_name'].strip().decode('gb2312')
    except UnicodeDecodeError:
        mate_service_area_name = row['mate_service_area_name'].strip().decode('gbk')
    mate_service_area, created = ServiceArea.objects.get_or_create(name=mate_service_area_name, creater=creater)
    try:
        mate_department_name = row['mate_department_name'].strip().decode('gb2312')
    except UnicodeDecodeError:
        mate_department_name = row['mate_department_name'].strip().decode('gbk')
    mate_department, created = Department.objects.get_or_create(name=mate_department_name,creater = creater)
    mate_service_area_department, created = ServiceAreaDepartment.objects.get_or_create(service_area=mate_service_area, department=mate_department)
    try:
        photo_name = row['photo_name'].strip().decode('gb2312')
    except UnicodeDecodeError:
        photo_name = row['photo_name'].strip().decode('gbk')
    try:
        file = default_storage.open(u'images/photos/%s' % photo_name)
    except IOError:
        file = default_storage.open(u'images/photo.jpg')
    photo_path = u'images/photos/%s.jpg' % id_number
    img = Image.open(file.name)
    if img.mode != 'RGB':
        img = img.convert('RGB')
    img.resize(gl.check_object_image_size,Image.ANTIALIAS).save(u'%s%s' % (settings.MEDIA_ROOT, photo_path),"JPEG")
    file.close()
    del img
    del file
    try:
        CheckObject.objects.get(id_number=id_number)
    except ObjectDoesNotExist:
        CheckObject.objects.create(name=name, photo=photo_path,id_number=id_number,service_area_department=service_area_department,is_family=is_family,mate_name=mate_name, mate_id_number=mate_id_number, mate_service_area_department=mate_service_area_department, ctp_method = ctp_method, ctp_method_time = ctp_method_time, wedding_time = wedding_time, address = address, children_1_name = children_1_name,children_1_sex = children_2_sex, children_1_id_number = children_1_id_number,children_2_name = children_2_name,children_2_sex = children_2_sex,children_2_id_number = children_2_id_number,children_3_name = children_3_name,children_3_sex = children_3_sex, children_3_id_number = children_3_id_number,creater = creater)



conn.close()
