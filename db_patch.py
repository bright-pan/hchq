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
