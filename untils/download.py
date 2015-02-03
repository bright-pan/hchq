#coding=utf-8
import os, tempfile, zipfile
from django.core.servers.basehttp import FileWrapper
from django.http import HttpResponseRedirect,HttpResponse,HttpResponseForbidden,Http404

def down_zipfile(path=None):
    if path:
	filename = path.split('/')[-1]
	temp = tempfile.TemporaryFile()
	archive = zipfile.ZipFile(temp, 'w', zipfile.ZIP_DEFLATED)
	archive.write(path)
	archive.close()
	wrapper = FileWrapper(temp)
	response = HttpResponse(wrapper, content_type='application/zip')
	response['Content-Disposition'] = 'attachment; filename=%s.zip' % filename
	response['Content-Length'] = temp.tell()
	temp.seek(0)
	return response
    else:
	return None
