
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


qs_check_project = CheckProject.objects.all()
qs_check_result = CheckResult.objects.all()
qs_check_object = CheckObject.objects.all()

# recorder check_object_object in qs_check_object:
#     for check_project_object in [qs_check_project[1]]:
#         qs_check_result_per_project = qs_check_result.filter(check_project = check_project_object, check_object=check_object_object)
#         count = qs_check_result_per_project.count()
#         if count:
#             check_result = qs_check_result_per_project[0]
#             check_result.is_latest = True
#             check_result.save()
#         # qs_check_result_per_project = qs_check_result.filter(check_project = check_project_object, check_object=check_object_object)
#         # print qs_check_result_per_project.count()
#         # print "********8"
#         # qs_check_result_per_project = qs_check_result.filter(check_project = check_project_object, check_object=check_object_object, is_latest=True)
#         # print qs_check_result_per_project.count()

for check_object_object in qs_check_object:
    for check_project_object in qs_check_project:
        qs_check_result_per_project = qs_check_result.filter(check_object = check_object_object, check_project = check_project_object).order_by("-id")
        count = qs_check_result_per_project.count()
        if count:
            check_result = qs_check_result_per_project[0]
            check_result.is_latest = True
            check_result.save()
            # print("************")
            # for check_result in qs_check_result_per_project:
            #     print check_result.id
            # print("*****************")
    #check_result=qs_check_result_per_project[0]


