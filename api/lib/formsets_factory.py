# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.forms import inlineformset_factory, formset_factory, modelformset_factory
from django.forms import TextInput, Select
from api.models import project, apiList, ApiParams, ApiBody
from api.form import createProject, createApi, debugParamsFormSet, debugBodysFormset

class formsetsFactory():

    def __init__(self, projectId=None, apiId=None):
        self.projectId = projectId or None
        self.apiId = apiId or None


    def project_formsets(self, request_POST=None):
        _formsets = modelformset_factory(project, form=createProject,
                                           fields=("name", "host", "port"), extra=0, can_delete=True)
        if request_POST:
            re_formset = _formsets(request_POST)
        else:
            re_formset = _formsets()
        return re_formset

    def apiList_formsets(self, request_POST=None):
        project_obj = project.objects.get(id=self.projectId)
        _formsets = inlineformset_factory(project, apiList, form=createApi, fields=(
    "apiName", "url", "request_method", "request_protocol", "post_method", "creater"), can_delete=True, extra=0, )
        if request_POST:
            re_formset = _formsets(request_POST, instance=project_obj)
        else:
            re_formset = _formsets(instance=project_obj)
        return re_formset

    def docParams_formsets(self, request_POST=None):
        api_obj = apiList.objects.get(id=self.apiId)
        widgets = {
            "key": TextInput(attrs={'style': "border:none; width:100%;", }),
            "key_type": Select(attrs={'style': "border:none; width:100%;", }),
            "key_description": TextInput(attrs={'style': "border:none; width:100%;", }),
            "key_default": TextInput(attrs={'style': "border:none; width:100%;", }),
        }

        if ApiParams.objects.filter(apiId=self.apiId):
            _formsets = inlineformset_factory(apiList, ApiParams, fields=(
            "key", "key_type", "key_must", "key_default", "key_description", "apiId"), can_delete=True, extra=0,
                                                           widgets=widgets)  # 通过外键设置formset
        else:
            _formsets = inlineformset_factory(apiList, ApiParams, fields=(
            "key", "key_type", "key_must", "key_default", "key_description", "apiId"), can_delete=True, extra=1,
                                                           widgets=widgets)  # 通过外键设置formset
        if request_POST:
            re_formset = _formsets(request_POST, instance=api_obj)
        else:
            re_formset = _formsets(instance=api_obj)
        return re_formset

    def docBodys_formsets(self, request_POST=None):
        api_obj = apiList.objects.get(id=self.apiId)
        bodys_widgts = {
            "body": TextInput(attrs={'style': "border:none; width:100%;", }),
            "body_type": Select(attrs={'style': "border:none; width:100%;", }),
            "body_default": TextInput(attrs={'style': "border:none; width:100%;", }),
            "body_description": TextInput(attrs={'style': "border:none; width:100%;", }),
        }

        if ApiBody.objects.filter(apiId=self.apiId):
            _formsets = inlineformset_factory(apiList, ApiBody, fields=(
            "body", "body_type", "body_must", "body_default", "body_description", "apiId"), can_delete=True, extra=0,
                                                         widgets=bodys_widgts)  # 通过外键设置formset
        else:
            _formsets = inlineformset_factory(apiList, ApiBody, fields=(
            "body", "body_type", "body_must", "body_default", "body_description", "apiId"), can_delete=True, extra=1,
                                                        widgets=bodys_widgts)
        if request_POST:
            re_formset = _formsets(request_POST, instance=api_obj)
        else:
            re_formset = _formsets(instance=api_obj)
        return re_formset

    def debugParams_formsets(self, request_POST=None):
        api_obj = apiList.objects.get(id=self.apiId)
        _formsets = inlineformset_factory(apiList, ApiParams, fields=("key_value", "key",),
                                                             can_delete=False, extra=0, formset=debugParamsFormSet)
        if request_POST:
            re_formset = _formsets(request_POST, instance=api_obj)
        else:
            re_formset = _formsets(instance=api_obj)
        return re_formset

    def debugBodys_formsets(self, request_POST=None):
        api_obj = apiList.objects.get(id=self.apiId)
        _formsets = inlineformset_factory(apiList, ApiBody, fields=("body_value", "body",),
                                                             can_delete=False, extra=0, formset=debugBodysFormset)
        if request_POST:
            re_formset = _formsets(request_POST, instance=api_obj)
        else:
            re_formset = _formsets(instance=api_obj)
        return re_formset