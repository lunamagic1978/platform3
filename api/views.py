# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging
import time

from api.lib import request_handle, testcase_handle, script_handle, public_handle
from django.contrib.auth.decorators import login_required
from django.forms import TextInput, Select
from django.forms import inlineformset_factory, formset_factory, modelformset_factory
from django.http import *
from django.shortcuts import render
from api.lib import formsets_factory, valid_factory, case_handle, messages
import os
import datetime
import pytest
import unittest

from .form import createProject, createApi, DebugEnv, ExpectKey, Case, ORDER_FIXED, ExpectKey_Type
from .form import Script, Base_script, config_env_form
from .models import project, apiList, ApiDetail, ApiBody, ApiParams, ApiTest, ApiScript, env

# Create your views here.
logger = logging.getLogger(__name__)

def report(request):
    username = request.session.get('user', '')
    return render(request, 'report.html')


@login_required
def apihome(request):
    username = request.session.get('user', '')
    projectFormsetsFactory = formsets_factory.formsetsFactory()
    project_modelforset = projectFormsetsFactory.project_formsets()

    if request.method == "POST":
        if "submit_createProject" in request.POST:
            logging.debug("创建项目的操作 保存")
            createProject_form = createProject(request.POST)
            if createProject_form.is_valid():
                createValidFactory = valid_factory.validFactory(temp=createProject_form.cleaned_data, request=request)
                createValidFactory.createProjectSave()
        if "editsave" in request.POST:
            project_modelforset_POST = projectFormsetsFactory.project_formsets(request.POST)
            if project_modelforset_POST.is_valid():
                editeProjectFactory = valid_factory.validFactory(request=request, formsets_POST=project_modelforset_POST)
                editeProjectFactory.editProjectSave()

        return HttpResponseRedirect("/api/home")
    else:
        createProject_form = createProject()
        ctx = {'username': username,
               'createProject_form': createProject_form,
               'project_modelforset': project_modelforset,}

        return render(request, 'apihome.html', ctx)


@login_required
def apilist(request, projectId):
    username = request.session.get('user', '')
    project_obj = project.objects.get(id=projectId)
    apiListFactory = formsets_factory.formsetsFactory(projectId=projectId)
    apiList_formset = apiListFactory.apiList_formsets()
    env_default = public_handle.case_default_env(projectId=projectId)
    if request.method == "POST":
        if "submit_createApi" in request.POST:
            createApi_form = createApi(request.POST)
            if createApi_form.is_valid():
                createValidFactory = valid_factory.validFactory(temp=createApi_form.cleaned_data, request=request)
                createValidFactory.createApiSave(projectId=projectId, username=username)
                return HttpResponseRedirect("/api/project%s" % projectId)

        if "editsave" in request.POST:
            apiList_formset_POST = apiListFactory.apiList_formsets(request_POST=request.POST)
            if apiList_formset_POST.is_valid():
                editeApiFactory = valid_factory.validFactory(request=request,
                                                                 formsets_POST=apiList_formset_POST)
                editeApiFactory.editApiSave()
        return HttpResponseRedirect("/api/project%s" % projectId)
    else:
        createApi_form = createApi()
        ctx = {'username': username,
               'project_obj': project_obj,
               'createApi_form': createApi_form,
               "projectId": projectId,
               "apiList_formset": apiList_formset,
               "env_default": env_default
                }
        return render(request, 'apilist.html', ctx)


@login_required
def api_doc(request, projectId, apiId):
    username = request.session.get('user', '') #根据session中的user获得登陆的用户名
    project_obj = project.objects.get(id=projectId) #根据projectId 查询项目数据 保存在project_obj中
    api_obj = apiList.objects.get(id=apiId) #根据apiid 查询api数据 保存在api_obj中
    env_default = public_handle.case_default_env(projectId=projectId)
    try:
        api_detail = ApiDetail.objects.get(apiId=apiId)
    except:
        api_detail = "无"

    docFactory = formsets_factory.formsetsFactory(projectId=projectId, apiId=apiId)

    if request.method == "POST":
        if "saveParams" in request.POST:
            ApiParamsModelFormSet_POST = docFactory.docParams_formsets(request_POST=request.POST)
            if ApiParamsModelFormSet_POST.is_valid(): #判断数据是否正确
                saveParams = valid_factory.validFactory(request=request, formsets_POST=ApiParamsModelFormSet_POST)
                saveParams.paramsSave()
        if "saveBodys" in request.POST:
            ApiBodyModelFormSet_POST = docFactory.docBodys_formsets(request_POST=request.POST)
            if ApiBodyModelFormSet_POST.is_valid(): #判断数据是否正确
                saveBodys = valid_factory.validFactory(request=request, formsets_POST=ApiBodyModelFormSet_POST)
                saveBodys.bodysSave()

        return HttpResponseRedirect("/api/project%s/api%s/doc" % (projectId, apiId))

    else:
        ApiParamsInlineForm = docFactory.docParams_formsets()
        ApiBodyInlineForm = docFactory.docBodys_formsets()
        ctx = {'username': username,
               'project_obj': project_obj,
               'api_obj': api_obj,
               'api_detail': api_detail,
               'ApiParamsInlineForm': ApiParamsInlineForm,
               'ApiBodyInlineForm': ApiBodyInlineForm,
               "env_default": env_default
               }
        return render(request, 'apidoc.html', ctx)


@login_required
def api_debug(request, projectId, apiId):
    username = request.session.get('user', '') #根据session中的user获得登陆的用户名
    project_obj = project.objects.get(id=projectId) #根据projectId 查询项目数据 保存在project_obj中
    api_obj = apiList.objects.get(id=apiId) #根据apiid 查询api数据 保存在api_obj中
    env_default = public_handle.case_default_env(projectId=projectId)

    debugFactory = formsets_factory.formsetsFactory(projectId=projectId, apiId=apiId)

    debugEnv = DebugEnv(instance=api_obj)
    if request.method == "POST":
        CustomApiParamsInlineForm = debugFactory.debugParams_formsets(request_POST=request.POST)
        CustomApiBodyInlineForm = debugFactory.debugBodys_formsets(request_POST=request.POST)
        debugEnv_POST = DebugEnv(request.POST, instance=api_obj)
        if CustomApiParamsInlineForm.is_valid() and debugEnv_POST.is_valid():
            env = debugEnv_POST.cleaned_data['env']
            requestHandle = request_handle.requestHandle(project_obj=project_obj, api_obj=api_obj, project_env=env)
            api_obj.env = env
            api_obj.save()
            CustomApiParamsInlineForm.save()
            CustomApiBodyInlineForm.save()
            for form in CustomApiParamsInlineForm:
                key = form.cleaned_data['key']
                key_value = form.cleaned_data['key_value']
                requestHandle.set_params(key=key, value=key_value)

            for form in CustomApiBodyInlineForm:
                body = form.cleaned_data['body']
                body_value = form.cleaned_data['body_value']
                requestHandle.set_bodys(body=body, body_value=body_value)
            response_data = requestHandle.request_send()
            CustomApiParamsInlineForm = debugFactory.debugParams_formsets()
            CustomApiBodyInlineForm = debugFactory.debugBodys_formsets()
            print(response_data.content)
            ctx = {'username': username,
                   'project_obj': project_obj,
                   'api_obj': api_obj,
                   'CustomApiParamsInlineForm': CustomApiParamsInlineForm,
                   'CustomApiBodyInlineForm': CustomApiBodyInlineForm,
                   'debugEnv': debugEnv_POST,
                   'response_data': response_data.content,
                   'response_status_code': response_data.status_code,
                   "env_default": env_default
                   }
            return render(request, 'apidebug.html', ctx)

        return HttpResponseRedirect("/api/project%s/api%s/debug" % (projectId, apiId))
    else:
        CustomApiParamsInlineForm = debugFactory.debugParams_formsets()
        CustomApiBodyInlineForm = debugFactory.debugBodys_formsets()
        ctx = {'username': username,
               'project_obj': project_obj,
               'api_obj': api_obj,
               'CustomApiParamsInlineForm': CustomApiParamsInlineForm,
               'CustomApiBodyInlineForm': CustomApiBodyInlineForm,
               'debugEnv': debugEnv,
               'response_data': "",
               "env_default": env_default
               }
        return render(request, 'apidebug.html', ctx)


@login_required
def api_test(request, projectId, apiId, envId):
    username = request.session.get('user', '')  # 根据session中的user获得登陆的用户名
    project_obj = project.objects.get(id=projectId) #根据projectId 查询项目数据 保存在project_obj中
    api_obj = apiList.objects.get(id=apiId) #根据apiid 查询api数据 保存在api_obj中
    api_params = ApiParams.objects.filter(apiId=apiId)
    api_bodys = ApiBody.objects.filter(apiId=apiId)
    obj_test = ApiTest.objects.filter(apiId=apiId, env_id=envId).values()
    params_len = len(api_params)
    bodys_len = len(api_bodys)
    expect_key = ExpectKey(initial={'apiId': api_obj})
    expect_key_type = ExpectKey_Type(initial={'apiId': api_obj})
    result_len = 12
    ScriptForm = Script()
    env_obj = env.objects.filter(projectId=projectId)

    if obj_test:
        MyFormSet = formset_factory(Case, formset=ORDER_FIXED, can_order=True, can_delete=True, extra=0)
        formset = MyFormSet(initial=obj_test, form_kwargs={"initial": {'apiId': apiId, 'is_empty': False, 'envId': envId}})
    else:
        MyFormSet = formset_factory(Case, formset=ORDER_FIXED, can_order=True, can_delete=True)
        formset = MyFormSet(initial=obj_test, form_kwargs={"initial": {'apiId': apiId, 'is_empty': True}})
    script_modelformsets = modelformset_factory(ApiScript, form=Base_script, fields=("ScriptName", "ScriptTpye",
                                "createTime", "updateTime", "author"), extra=0, can_order=True, can_delete=True)
    script_modelformset = script_modelformsets(queryset=ApiScript.objects.filter(apiId=apiId))

    if request.method == "POST":
        expectkey_POST = ExpectKey(request.POST, initial={'apiId': api_obj})
        case_formet_POST_SAVE = MyFormSet(request.POST, form_kwargs={"initial": {'apiId': apiId, 'is_empty': False, 'envId': envId}})
        expectkey_type_POST = ExpectKey_Type(request.POST, initial={'apiId': api_obj})


        if "testcasesave" in request.POST:
            if case_formet_POST_SAVE.is_valid() and expectkey_POST.is_valid() and expectkey_type_POST.is_valid():
                temp = case_formet_POST_SAVE.cleaned_data
                temp_result_key = expectkey_POST.cleaned_data
                temp_result_key_type = expectkey_type_POST.cleaned_data
                del temp_result_key['response_code']
                del temp_result_key['response_time']
                del temp_result_key_type['codetype']
                del temp_result_key_type['timetype']
                try:
                    case_formet_POST_SAVE.save(datas=temp, apiId=api_obj, result_key=temp_result_key,
                                               result_key_type=temp_result_key_type, env_id=envId, api_bodys=api_bodys,
                                               api_params=api_params)
                    new_obj_test = ApiTest.objects.filter(apiId=apiId, env_id=envId).values()
                    case_handle.create_case(projectId=projectId, apiId=apiId, case_num=len(new_obj_test),
                                            project_name=project_obj.name, api_name=api_obj.apiName, env_id=envId)
                except:
                    messages.flash(request, "报错", "保存测试用例出错", level="error")
                return HttpResponseRedirect("/api/project%s/api%s/test/%s" % (projectId, apiId, envId))

        elif "exec" in request.POST:
            if case_formet_POST_SAVE.is_valid() and expectkey_POST.is_valid() and expectkey_type_POST.is_valid():
                temp = case_formet_POST_SAVE.cleaned_data
                temp_result_key = expectkey_POST.cleaned_data
                temp_result_key_type = expectkey_type_POST.cleaned_data
                del temp_result_key['response_code']
                del temp_result_key['response_time']
                del temp_result_key_type['codetype']
                del temp_result_key_type['timetype']
                try:
                    case_formet_POST_SAVE.save(datas=temp, apiId=api_obj, result_key=temp_result_key,
                                               result_key_type=temp_result_key_type, env_id=envId, api_bodys=api_bodys,
                                               api_params=api_params)
                    new_obj_test = ApiTest.objects.filter(apiId=apiId, env_id=envId).values()
                    case_handle.create_case(projectId=projectId, apiId=apiId, case_num=len(new_obj_test),
                                            project_name=project_obj.name, api_name=api_obj.apiName, env_id=envId)
                except:
                    messages.flash(request, "报错", "保存测试用例出错", level="error")
                # pytest.main(['/Users/smzdm/luna/platform3/api/testcase/%s/%s/%s' % (project_obj.pk, api_obj.pk, envId)])
                # 'python3 -m unittest discover -s /Users/smzdm/luna/platform3/api/testcase/1/1/5/ -p "case*_test.py"'
                # path = "'/Users/smzdm/luna/platform3/api/testcase/%s/%s/%s'" % (project_obj.pk, api_obj.pk, envId)
                # file_list = os.listdir(path)
                # TestSuit = unittest.TestSuite
                # discover = unittest.defaultTestLoader.discover("/Users/smzdm/luna/platform3/api/testcase/1/1/5/",
                #                                                pattern="case*_test.py")
                # runner = unittest.TextTestRunner()
                # runner.run(discover)
                # os.system("pytest /Users/smzdm/luna/platform3/api/testcase/%s/%s/%s" % (project_obj.pk, api_obj.pk, envId))
                public_handle.os_run(projectId=project_obj.pk, apiId=api_obj.pk, envId=envId)

                return HttpResponseRedirect("/api/project%s/api%s/test/%s" % (projectId, apiId, envId))
        elif "script" in request.POST:
            script_POST = Script(request.POST, request.FILES)
            if script_POST.is_valid():
                temp = script_POST.cleaned_data
                script_obj = ApiScript.objects.get_or_create(apiId=api_obj, ScriptTpye=temp['ScriptTpye'],
                            ScriptName=temp['ScriptFile'])

                if script_obj[1]:
                    print("success")
                    script_obj[0].ScriptFile = temp['ScriptFile']
                    script_obj[0].author = username
                    script_obj[0].save()
                else:
                    print("failed")
                    script_obj[0].ScriptFile = temp['ScriptFile']
                    script_obj[0].author = username
                    script_obj[0].updateTime = datetime.datetime.now()
                    script_obj[0].save()

            script_handle.save_script(work_path=os.getcwd(), apiId=apiId, filename=temp['ScriptFile'])
            return HttpResponseRedirect("/api/project%s/api%s/test/%s" % (projectId, apiId, envId))
        elif "script_delete" in request.POST:

            script_modelformset_POST = script_modelformsets(request.POST)
            if script_modelformset_POST.is_valid():
                exist_file_list = []
                script_modelformset_POST.save()
                script_query = ApiScript.objects.filter(apiId=api_obj)
                for script in script_query:
                    exist_file_list.append(script.ScriptName)
                script_handle.del_script(work_path=os.getcwd(), apiId=apiId, exist_file_list=exist_file_list)
            return HttpResponseRedirect("/api/project%s/api%s/test/%s" % (projectId, apiId, envId))
        else:
            return HttpResponseRedirect("/api/project%s/api%s/test/%s" % (projectId, apiId, envId))

    else:
        ctx = {'username': username,
               'project_obj': project_obj,
               'api_obj': api_obj,
               'api_params': api_params,
               'params_len': params_len,
               'api_bodys': api_bodys,
               'bodys_len': bodys_len,
               'expect_key': expect_key,
               'result_len': result_len,
               'formset': formset,
               'expect_key_type': expect_key_type,
               'ScriptForm': ScriptForm,
               'script_modelformset': script_modelformset,
               'env_default': int(envId),
               'env_obj': env_obj,
               }
        return render(request, 'apitest.html', ctx)


@login_required
def project_config(request, projectId):
    project_obj = project.objects.get(id=projectId)
    env_modelformsets = modelformset_factory(env, form=config_env_form, extra=0, can_order=True, can_delete=True) #初始化env的modelformsets
    env_modelformset = env_modelformsets(queryset=env.objects.filter(projectId_id=projectId)) #根据projectId来设定formset内容

    if request.method == "POST":
        if "saveenv" in request.POST:
            env_modelformset_POST = env_modelformsets(request.POST) #把request内容过滤为formset内容
            if env_modelformset_POST.is_valid():
                env_modelformset_POST.save() #formset内容正确，保存内容
        return HttpResponseRedirect("/api/project%s/config" %projectId)
    else:
        ctx = {"project_obj": project_obj,
               "env_modelformset": env_modelformset,
               }
        return render(request, 'projectconfig.html', ctx)