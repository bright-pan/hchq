#coding=utf-8
import os, tempfile, zipfile
from django.core.servers.basehttp import FileWrapper
from django.http import HttpResponseRedirect,HttpResponse,HttpResponseForbidden,Http404
from sendfile import sendfile

def down_zipfile(request, path=None):
    if path:
	response = HttpResponse()
	name=path.split('/')[-1]
	response['Content_Type']='application/octet-stream'
	response["Content-Disposition"] = "attachment; filename=%s" % name
	response['Content-Length'] = os.path.getsize(path)
	response['X-Accel-Redirect'] = "/protected/%s" % name
	return response
	# send myfile.pdf as an attachment (with name myfile.pdf)
	return sendfile(request, path, attachment=True)

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
