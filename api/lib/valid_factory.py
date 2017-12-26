# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from api.models import project, apiList
from . import messages

class validFactory():

    def __init__(self, temp=None, request=None, formsets_POST=None):
        self.temp = temp
        self.request = request
        self.formsets_POST = formsets_POST

    def createProjectSave(self):
        name = self.temp['name']
        host = self.temp['host']
        port = self.temp['port']
        obj = project.objects.create(name=name, port=port, host=host)
        try:
            obj.save()
            messages.flash(self.request, 'info', '项目保存成功')
        except Exception as e:
            print(e)
            messages.flash(self.request, 'info', '项目保存异常')

    def editProjectSave(self):
        try:
            self.formsets_POST.save()
            messages.flash(self.request, 'info', '项目编辑成功')
        except Exception as e:
            print(e)
            messages.flash(self.request, 'info', '项目编辑异常')

    def createApiSave(self, projectId, username):
        apiName = self.temp['apiName']
        url = self.temp['url']
        request_method = self.temp['request_method']
        request_protocol = self.temp['request_protocol']
        post_method = self.temp['post_method']
        obj = apiList.objects.create(apiName=apiName, url=url, request_protocol=request_protocol,
                                     request_method=request_method, creater=username,
                                     projectName_id=projectId, post_method=post_method)
        try:
            obj.save()
            messages.flash(self.request, 'info', '接口保存成功')
        except Exception as e:
            print(e)
            messages.flash(self.request, 'info', '接口保存异常')


    def editApiSave(self):
        try:
            self.formsets_POST.save()
            messages.flash(self.request, 'info', '项目编辑成功')
        except Exception as e:
            print(e)
            messages.flash(self.request, 'info', '项目编辑异常')

    def paramsSave(self):
        try:
            self.formsets_POST.save()
            messages.flash(self.request, 'info', 'Params编辑成功')
        except Exception as e:
            print(e)
            messages.flash(self.request, 'info', 'Params编辑异常')

    def bodysSave(self):
        try:
            self.formsets_POST.save()
            messages.flash(self.request, 'info', 'Bodys编辑成功')
        except Exception as e:
            print(e)
            messages.flash(self.request, 'info', 'Bodys编辑异常')