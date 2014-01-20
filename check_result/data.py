##########################################
##检查项目必须启动,检查时间必须屏蔽自动写入时间，之后打开，切记
##########################################

import pymssql
import datetime
import re
from django.contrib.auth.models import *
from service_area.models import *
from department.models import *
from check_object.models import *
from check_project.models import *
from check_result.models import *
from PIL import Image
from django.core.files.storage import default_storage
from hchq import settings
from untils import gl
from django.db.models import ObjectDoesNotExist

conn = pymssql.connect(host='192.168.0.167',user='sa',password='',database='HCHQ')
cur = conn.cursor()
cur.execute('select b.qizsfzh id_number, a.jieg result, c.denglm recorder_name, d.xingm checker_name ,a.jiangcsj check_time, a.qiy is_latest from jiancjg a left join gerxx b on a.gerbm=b.gerbm left join yonghu c on a.lurrbm = c.yonghdm left join fuwryxx d on a.jiancys=d.fuwrybm')
query_set = cur.fetchall_asdict()

check_project = CheckProject.objects.get(is_setup=True)
re_pregnant = re.compile(ur'有孕|无孕')
re_ring = re.compile(ur'有环|无环')
re_pregnant_period = re.compile(ur'孕\d+周')
re_period = re.compile(ur'\d+')

for row in query_set:
    try:
        id_number = row['id_number'].strip().decode('gb2312')
    except UnicodeDecodeError:
        id_number = row['id_number'].strip().decode('gbk')
    try:
        check_object = CheckObject.objects.get(id_number=id_number)
    except ObjectDoesNotExist:
        continue
    if row['recorder_name'] is not None:
        try:
            recorder_name = row['recorder_name'].strip().decode('gb2312')
        except UnicodeDecodeError:
            recorder_name = row['recorder_name'].strip().decode('gbk')
        try:
            recorder = User.objects.get(username=recorder_name)
        except ObjectDoesNotExist:
            recorder = User.objects.get(pk=1)
    else:
        recorder = User.objects.get(pk=1)
    if row['checker_name'] is not None:
        try:
            checker_name = row['checker_name'].strip().decode('gb2312')
        except UnicodeDecodeError:
            checker_name = row['checker_name'].strip().decode('gbk')
        try:
            checker = User.objects.get(username=checker_name)
        except ObjectDoesNotExist:
            checker = recorder
    else:
        checker = recorder
    is_latest = row['is_latest']
    try:
        ct = row['check_time'].strip().decode('gb2312')
    except UnicodeDecodeError:
        ct = row['check_time'].strip().decode('gbk')
    if ct ==u'':
        check_time=None
    else:
        ct_list = ct.split(u'-')
        check_time = datetime.datetime(int(ct_list[0]),int(ct_list[1]),int(ct_list[2]))
    try:
        rs = row['result'].strip().decode('gb2312')
    except UnicodeDecodeError:
        rs = row['result'].strip().decode('gbk')
    ring = u'unring'
    pregnant = u'unpregnant'
    period = None
    rs_pregnant = re_pregnant.findall(rs)
    if rs_pregnant:
        if rs_pregnant[0] == u'有孕':
            pregnant = u'pregnant'
        else:
            pregnant = u'unpregnant'
    rs_ring = re_ring.findall(rs)
    if rs_ring:
        if rs_ring[0] == u'有环':
            ring = u'ring'
        else:
            ring = u'unring'
    rs_period = re_period.findall(rs)
    if rs_period:
        pregnant = u'pregnant'
        ring = u'unring'
        period = rs_period[0]
    result = "%s %s %s" % (pregnant, ring, period)
    if is_latest == True:
        CheckResult.objects.filter(check_object=check_object).update(is_latest=False)
    else:
        pass
    CheckResult.objects.create(check_object=check_object,check_project=check_project,checker=checker,recorder=recorder,result=result,check_time=check_time, is_latest=is_latest)




conn.close()
