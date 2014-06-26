from check_project.models import *
from check_object.models import *
from check_result.models import *
check_project = CheckProject.objects.get(is_setup=True, is_active=True)
check_object = CheckObject.objects.filter(is_active=False, check_result__check_project=check_project)
check_object.update(is_active=True)



#ALTER TABLE check_object ADD COLUMN thumbnail varchar(100);
#UPDATE check_object SET thumbnail='images/thumbnails';
#ALTER TABLE check_object MODIFY thumbnail varchar(100) NOT NULL;

from check_object.models import *
from untils import gl
from django.core.files.storage import default_storage
from PIL import Image,ImageDraw,ImageFont
from hchq import settings



def photo():
    qs_co = CheckObject.objects.all()
    font = ImageFont.truetype('%s/static/fonts/MSYH.TTF' % settings.CURRENT_PATH,12)                    
    for co in qs_co:
        temp_file = default_storage.open(co.photo.name)
        temp_file_name = temp_file.name.decode('utf-8').replace('\\', '/')
        temp_file.close()
        try:
            img = Image.open(u'%s' % temp_file_name)
            print temp_file_name
        except IOError:
            print '*******88'
            img = Image.open('%s/static/images/photo.jpg' % settings.CURRENT_PATH)
            if img.mode != "RGB":
                img = img.convert("RGB")
                img.resize(gl.check_object_image_size,Image.ANTIALIAS)
        draw = ImageDraw.Draw(img)
        draw.rectangle([gl.check_object_rect_mark, gl.check_object_image_size], fill=gl.check_object_rect_mark_color)
        draw.text(gl.check_object_text_mark, u'%s %s' % (co.name, co.id_number),gl.check_object_text_mark_color,font=font)
        del draw
        img.save(temp_file_name,"JPEG")


def thumbnail():
    qs_co = CheckObject.objects.all()
    for co in qs_co:
        co.thumbnail = co.photo.name.replace('photos', 'thumbnails')
        co.save()
        temp_file = default_storage.open(co.photo.name)
        temp_file_name = temp_file.name.replace('\\', '/')
        temp_file.close()
        try:
            img = Image.open(u'%s' % temp_file_name)
            print temp_file_name
        except IOError:
            print '*******88'
            img = Image.open('%s/static/images/photo.jpg' % settings.CURRENT_PATH)
            if img.mode != "RGB":
                img = img.convert("RGB")
                img.resize(gl.check_object_image_size,Image.ANTIALIAS)
        img.thumbnail(gl.check_object_thumbnail_size, Image.ANTIALIAS)
        temp_file_name = temp_file_name.replace('photos', 'thumbnails')
        print temp_file_name
        print '$$$$$$$$'
        img.save(temp_file_name,"JPEG")
        

#########################################################################
#                  FIX check_result for service_area_department
#########################################################################

# ALTER TABLE `hchq`.`check_result`
# ADD COLUMN
# `service_area_department_id` INT(11) NOT NULL AFTER `is_latest`;
#
# 解决方法如下：
# 打开Workbench的菜单[Edit]->[Preferences...]
# 切换到[SQL Editor]页面
# 把[Forbid UPDATE and DELETE statements without a WHERE clause (safe updates)]之前的对勾去掉
# 点击[OK]按钮
# 最后记得要重启一下sql editor,建立一个新的连接就可以了。
# UPDATE `hchq`.`check_result` SET `service_area_department_id`='1' ;
#
#
# ALTER TABLE `hchq`.`check_result`
# ADD INDEX `service_area_department_id_refs_id_5079e70a_idx` (`service_area_department_id` ASC);
# ALTER TABLE `hchq`.`check_result`
# ADD CONSTRAINT `service_area_department_id_refs_id_5079e70a`
#   FOREIGN KEY (`service_area_department_id`)
#   REFERENCES `hchq`.`service_area_department` (`id`)
#   ON DELETE RESTRICT
#   ON UPDATE RESTRICT;

# python manage.py shell
#
# from check_result.models import CheckResult
#
# cr = CheckResult.objects.all()
# cr.count()
# for i in cr:
#    i.service_area_department = i.check_object.service_area_department
#    i.save()

import datetime
from check_project.models import CheckProject
from check_result.models import CheckResult
from check_object.models import CheckObject
from django.contrib.auth.models import User

qs_cp = CheckProject.objects.filter(is_active=True)

print qs_cp.count()
user = User.objects.get(pk=1)
result = u'invalid'
for cp in qs_cp:
    check_project_endtime = datetime.datetime(cp.end_time.year,
                                              cp.end_time.month,
                                              cp.end_time.day,
                                              23, 59, 59)
    qs_check_object = CheckObject.objects.exclude(created_at__gt=check_project_endtime).exclude(is_active=False,
                                                                                                updated_at__lt=check_project_endtime)
    qs_check_result = CheckResult.objects.filter(check_project=cp)

    for co in qs_check_object:
        if qs_check_result.filter(check_object=co).count() < 0:
            if co.is_family is False:
                CheckResult.objects.create(check_object=co,
                                           check_project=cp,
                                           checker=user,
                                           recorder=user,
                                           result=result,
                                           is_latest=False,
                                           service_area_department=co.service_area_department)
            else:
                CheckResult.objects.create(check_object=co,
                                           check_project=cp,
                                           checker=user,
                                           recorder=user,
                                           result=result,
                                           is_latest=False,
                                           service_area_department=co.mate_service_area_department)


1. 参检单位和区域自动补全功能。
2. 增加检查项目的时候，预检查所有的对象，检查结果是无效的
3. 检查对象增加和修改的时候，需要预检查这个对象，或者修改有效的检查结果。
4. 增加检查对象和修改检查对象的时候，如果是家属则加入丈夫和妻子单位匹配校验。
5. 找出所有家属中，丈夫和妻子单位不匹配的对象，并加以修改。
6. 报表中的对象数量的计算需要重新来计算，包括所有报表中计算机制也需要替换。比如（check_object_check_service_area_report）
7. 检查结果添加的语句无需区别家属还是非家属。
这样做的目的就是为了是历史数据更加稳定，准确。