#coding=utf-8
from django.template import RequestContext
from django.utils import simplejson
from django.http import HttpResponseRedirect,HttpResponse,HttpResponseForbidden,Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.cache import never_cache, cache_page
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user
from django.db.models import ObjectDoesNotExist, Q
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from PIL import Image
from hchq.check_object.forms import *
from hchq.untils.my_paginator import pagination_results
from hchq.untils import gl
from hchq import settings

# Create your views here.
@csrf_protect
@login_required
def check_object_add(request, template_name='my.html', next='/', check_object_page='1'):
    """
    检查对象添加视图，带添加预览功能！
    """
    page_title = u'添加检查对象'
    user = get_user(request)

    if request.method == 'POST':
        post_data = request.POST.copy()
        submit_value = post_data[u'submit']
        if submit_value == u'添加':
            check_object_add_form = CheckObjectAddForm(post_data, request.FILES)
            if check_object_add_form.is_valid():
                check_object_add_form.add(user)
            else:
                pass
            return render_to_response(template_name,
                                      {'add_form': check_object_add_form,
                                       'page_title': page_title,
                                       },
                                      context_instance=RequestContext(request))

        else:
            raise Http404('Invalid Request!')
    else:
        check_object_add_form = CheckObjectAddForm()
        return render_to_response(template_name,
                                  {'add_form': check_object_add_form,
                                  'page_title': page_title,
                                  },
                                  context_instance=RequestContext(request))
@csrf_protect
@login_required
def check_object_add_uploader(request, template_name='my.html', next='/', check_object_page='1'):
    if request.method == 'POST':
        if request.FILES.get('photo'):

            data = request.FILES['photo']
            if data.size >= settings.MAX_PHOTO_UPLOAD_SIZE:
                raise Http404('Invalid Request!')
            try:
                temp_file = default_storage.open(u'images/photos/temp/%s.temp' % request.user.username, 'wb+')
            except IOError:
                raise Http404('Invalid Request!')
            for chunk in data.chunks():
                temp_file.write(chunk)
            temp_file.close()
            try:
                img = Image.open(temp_file.name)
            except IOError:
                raise Http404('Invalid Request!')
            if not (img.format.lower() in ['jpeg','jpg','gif', 'png','bmp']):
                raise Http404('Invalid Request!')
            if img.mode != "RGB":
                img = img.convert("RGB")
            img.resize(gl.check_object_image_size,Image.ANTIALIAS).save(temp_file.name,"JPEG")
            del temp_file
            del img
            return HttpResponse('success')
        else:
            raise Http404('Invalid Request!')
    else:
        raise Http404('Invalid Request!')

    
@csrf_protect
@login_required
def check_object_show(request, template_name='', next='', check_object_index='1'):
    """
    检查对象详细信息显示。
    """
    page_title=u'检查对象详情'

    if request.method == 'POST':
        raise Http404('Invalid Request!')
            
    else:
        try:
            check_object_id = int(check_object_index)
        except ValueError:
            raise Http404('Invalid Request!')
        try:
            result = CheckObject.objects.get(pk=check_object_id, is_active=True)
        except ObjectDoesNotExist:
            raise Http404('Invalid Request!')
        
    return render_to_response(template_name,
                              {'result': result,
                               },
                              context_instance=RequestContext(request))

@csrf_protect
@login_required
def check_object_modify(request, template_name='my.html', next_template_name='my.html', check_object_page='1',):
    """
    检查对象修改视图
    """
    page_title = u'编辑检查对象'
    if request.method == 'POST':
        post_data = request.POST.copy()
        submit_value = post_data[u'submit']
        if submit_value == u'编辑':
            check_object_modify_form = Check_ObjectModifyForm(post_data)
            if check_object_modify_form.is_valid():
                check_object_modify_object = check_object_modify_form.object()
#                print check_object_modify_object
                check_object_detail_modify_form = Check_ObjectDetailModifyForm()
                check_object_detail_modify_form.set_value(check_object_modify_object)
                page_title = u'修改检查对象'
                return render_to_response(next_template_name,
                                          {'detail_modify_form': check_object_detail_modify_form,
                                           'check_object_name': check_object_modify_object.username,
                                           'page_title': page_title,
                                           },
                                          context_instance=RequestContext(request))
            else:
                pass
            check_object_search_form = Check_ObjectSearchForm(Check_ObjectSearchForm().data_from_session(request))
            check_object_search_form.init_from_session(request)
            if check_object_search_form.is_valid():
                query_set = check_object_search_form.search()
                results_page = pagination_results(check_object_page, query_set, settings.CHECK_OBJECT_PER_PAGE)
            else:
                results_page = None
        else:
            if submit_value == u'查询':
                check_object_search_form = Check_ObjectSearchForm(post_data)
                check_object_modify_form = Check_ObjectModifyForm()
                if check_object_search_form.is_valid():
                    check_object_search_form.data_to_session(request)
                    check_object_search_form.init_from_session(request)
                    query_set = check_object_search_form.search()
                    results_page = pagination_results(check_object_page, query_set, settings.CHECK_OBJECT_PER_PAGE)
                else:
                    results_page = None
            else:
                raise Http404('Invalid Request!')                
        return render_to_response(template_name,
                                  {'search_form': check_object_search_form,
                                   'modify_form': check_object_modify_form,
                                   'page_title': page_title,
                                   'results_page':results_page,
                                   },
                                  context_instance=RequestContext(request))
    else:
        check_object_modify_form = Check_ObjectModifyForm()
        check_object_search_form = Check_ObjectSearchForm(Check_ObjectSearchForm().data_from_session(request))
        check_object_search_form.init_from_session(request)
        if check_object_search_form.is_valid():
            query_set = check_object_search_form.search()
            results_page = pagination_results(check_object_page, query_set, settings.CHECK_OBJECT_PER_PAGE)
        else:
            results_page = None
        return render_to_response(template_name,
                                  {'search_form': check_object_search_form,
                                   'modify_form': check_object_modify_form,
                                   'page_title': page_title,
                                   'results_page':results_page,
                                   },
                                  context_instance=RequestContext(request))

@csrf_protect
@login_required
def check_object_detail_modify(request, template_name='my.html', next='/', check_object_page='1',):
    """
    检查对象修改视图
    """

    page_title = u'编辑检查对象'
    if request.method == 'POST':
        post_data = request.POST.copy()
        submit_value = post_data[u'submit']
        if submit_value == u'修改':
            check_object_detail_modify_form = Check_ObjectDetailModifyForm(post_data)
            if check_object_detail_modify_form.is_valid():
                check_object_detail_modify_form.detail_modify()
                return HttpResponseRedirect(next)
            else:
                check_object_id = int(check_object_detail_modify_form.data.get('id'))
                check_object_object = CheckProject.objects.get(pk=check_object_id)
                return render_to_response(template_name,
                                          {'detail_modify_form': check_object_detail_modify_form,
                                           'check_object_name': check_object_object.username,
                                           'page_title': page_title,
                                           },
                                          context_instance=RequestContext(request))

        else:
            raise Http404('Invalid Request!')
    else:
        raise Http404('Invalid Request!')

@csrf_protect
@login_required
def check_object_delete(request, template_name='my.html', next='/', check_object_page='1',):
    """
    检查对象删除视图
    """
    page_title = u'删除检查对象'

    if request.method == 'POST':
        post_data = request.POST.copy()
        submit_value = post_data[u'submit']
        if submit_value == u'删除':
            check_object_delete_form = Check_ObjectDeleteForm(post_data)
            if check_object_delete_form.is_valid():
                check_object_delete_form.delete()
            else:
                pass
            check_object_search_form = Check_ObjectSearchForm(Check_ObjectSearchForm().data_from_session(request))
            check_object_search_form.init_from_session(request)
            if check_object_search_form.is_valid():
                query_set = check_object_search_form.search()
                results_page = pagination_results(check_object_page, query_set, settings.CHECK_OBJECT_PER_PAGE)
            else:
                results_page = None
        else:
            if submit_value == u'查询':
                check_object_search_form = Check_ObjectSearchForm(post_data)
                check_object_delete_form = Check_ObjectDeleteForm()
                if check_object_search_form.is_valid():
                    check_object_search_form.data_to_session(request)
                    check_object_search_form.init_from_session(request)
                    query_set = check_object_search_form.search()
                    results_page = pagination_results(check_object_page, query_set, settings.CHECK_OBJECT_PER_PAGE)
                else:
                    results_page = None
            else:
                raise Http404('Invalid Request!')                
        return render_to_response(template_name,
                                  {'search_form': check_object_search_form,
                                   'delete_form': check_object_delete_form,
                                   'page_title': page_title,
                                   'results_page':results_page,
                                   },
                                  context_instance=RequestContext(request))
    else:
        check_object_delete_form = Check_ObjectDeleteForm()
        check_object_search_form = Check_ObjectSearchForm(Check_ObjectSearchForm().data_from_session(request))
        check_object_search_form.init_from_session(request)
        if check_object_search_form.is_valid():
            query_set = check_object_search_form.search()
            results_page = pagination_results(check_object_page, query_set, settings.CHECK_OBJECT_PER_PAGE)
        else:
            results_page = None
        return render_to_response(template_name,
                                  {'search_form': check_object_search_form,
                                   'delete_form': check_object_delete_form,
                                   'page_title': page_title,
                                   'results_page':results_page,
                                   },
                                  context_instance=RequestContext(request))


@csrf_protect
@login_required
def check_object_list(request, template_name='my.html', next='/', check_object_page='1',):
    """
    检查对象查询视图
    """
    page_title = u'查询检查对象'

    if request.method == 'POST':
        post_data = request.POST.copy()
        check_object_search_form = CheckObjectSearchForm(post_data)
        if check_object_search_form.is_valid():
            check_object_search_form.data_to_session(request)
            check_object_search_form.init_from_session(request)
            query_set = check_object_search_form.search()
            results_page = pagination_results(check_object_page, query_set, settings.CHECK_OBJECT_PER_PAGE)
        else:
            results_page = None
        return render_to_response(template_name,
                                  {'search_form': check_object_search_form,
                                   'page_title': page_title,
                                   'results_page': results_page,
                                   },
                                  context_instance=RequestContext(request))
    else:
        check_object_search_form = CheckObjectSearchForm(CheckObjectSearchForm().data_from_session(request))
        check_object_search_form.init_from_session(request)
        if check_object_search_form.is_valid():
            query_set = check_object_search_form.search()
            results_page = pagination_results(check_object_page, query_set, settings.CHECK_OBJECT_PER_PAGE)
        else:
            results_page = None
        return render_to_response(template_name,
                                  {'search_form': check_object_search_form,
                                   'page_title': page_title,
                                   'results_page': results_page,
                                   },
                                  context_instance=RequestContext(request))
    
