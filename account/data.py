import pymssql
import datetime
from django.contrib.auth.models import *
from service_area.models import *
from department.models import *
from check_object.models import *
from PIL import Image
from django.core.files.storage import default_storage
from hchq import settings
from untils import gl
from django.db.models import ObjectDoesNotExist
from account.models import *

conn = pymssql.connect(host='192.168.0.167',user='sa',password='',database='HCHQ')
cur = conn.cursor()
cur.execute('select a.denglm username, c.fuwqmc service_area_name, d.dianwmc department_name , a.lianx contact, b.jiaomc role_name from yonghu a, jiaoshe b, FuWuQu c,DanWXX d where (a.fuwqbm=c.fuwqbm and a.dianwbh = d.dianbh and a.jiaosbh=b.jiaosbh)')
query_set = cur.fetchall_asdict()

creater = User.objects.get(pk=1)

for row in query_set:
    try:
        username = row['username'].strip().strip('(').strip(')').decode('gb2312')
    except UnicodeDecodeError:
        username = row['username'].strip().strip('(').strip(')').decode('gbk')
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
        contact = row['contact'].strip().decode('gb2312')
    except UnicodeDecodeError:
        contact = row['contact'].strip().decode('gbk')
    try:
        role_name = row['role_name'].strip().decode('gb2312')
    except UnicodeDecodeError:
        role_name = row['role_name'].strip().decode('gbk')
    role, created = Group.objects.get_or_create(name=role_name)
    try:
        User.objects.get(username=username)
    except ObjectDoesNotExist:
        user_object = User.objects.create_user(username=username,email=settings.ACCOUNT_DEFAULT_EMAIL,password=settings.ACCOUNT_DEFAULT_PASSWORD)
        user_object.groups.add(role)
        UserProfile.objects.create(user=user_object,service_area_department=service_area_department,contact = contact,)


cur.execute('select a.xingm username from fuwryxx a where a.qiy = 1')
query_set = cur.fetchall_asdict()


for row in query_set:
    try:
        username = row['username'].strip().strip('(').strip(')').decode('gb2312')
    except UnicodeDecodeError:
        username = row['username'].strip().strip('(').strip(')').decode('gbk')
    try:
        user_object = User.objects.get(username=username)
    except ObjectDoesNotExist:
        continue
    user_profile = user_object.get_profile()
    user_profile.is_checker = True
    user_profile.save()

    

conn.close()
