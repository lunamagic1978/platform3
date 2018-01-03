# -*- coding: utf-8 -*-
import requests
from api.models import ApiTest, env
from time import time
import os
import re

class requestHandle():

    def __init__(self, project_obj, api_obj, project_env):
        try:
            obj = env.objects.get(projectId=project_obj.pk, envName=project_env)
        except:
            print("环境配置不存在")

        self.host = obj.envHost
        self.url = api_obj.url
        self.request_method = api_obj.request_method
        self.post_method = api_obj.post_method
        self.request_protocol = api_obj.request_protocol
        self.port = obj.envPort
        self.params = {}
        self.payload = None
        self.headers = eval(obj.envHeaders)

    def set_params(self, key, value):
        if value:
            self.params[key] = value

    def set_case_params(self, params):
        self.params = params

    def set_case_bodys(self, payload):
        if self.post_method == "x-www-form-urlencoded":
            self.headers['content-type'] = "application/x-www-form-urlencoded"
        self.payload = payload

    def set_bodys(self, body, body_value):
        if self.post_method == "x-www-form-urlencoded":
            self.headers['content-type'] = "application/x-www-form-urlencoded"
            if body_value:
                if self.payload:
                    self.payload = self.payload + "&%s=%s" % (body, body_value)
                else:
                    self.payload = "%s=%s" % (body, body_value)

    def request_send(self):
        if self.port == "80":
            url = "%s://%s:%s" % (self.request_protocol, self.host, self.url)
        else:
            url = "%s://%s:%s%s" % (self.request_protocol, self.host, self.port, self.url)
        if self.request_protocol == "HTTP":
            response_data = requests.request(method=self.request_method, url=url, params=self.params, headers=self.headers, data=self.payload)
        else:
            response_data = requests.request(method=self.request_method, url=url, params=self.params,
                                             headers=self.headers, data=self.payload, verify=False)

        return response_data


def testCaseExec(apiId, project_obj, api_obj, env):

    testCases = ApiTest.objects.filter(apiId_id=apiId)
    for case in testCases:
        request_Handle = requestHandle(project_obj=project_obj, api_obj=api_obj)
        base_path = os.path.join(os.getcwd(), "api/upload")
        api_path = os.path.join(base_path, str(apiId))
        try:
            script_file = os.path.join(api_path, "setup.py")
            result = os.popen("python3 %s" % script_file)
            res = result.read()
        except Exception:
            print("no setup.py")

        params_dict = eval(case.TestParams)
        params_dict_fix = {}
        for key in params_dict.keys():
            params_dict_fix[key[7:]] = params_dict[key]

        if request_Handle.post_method == "x-www-form-urlencoded":
            bodys_dict = eval(case.TestBodys)
            for key in bodys_dict.keys():
                request_Handle.set_bodys(key[6:], bodys_dict[key])



        request_Handle.set_case_params(params_dict_fix)
        start_time = time()
        response_data = request_Handle.request_send(env=env)
        end_time = time()
        case.Response_code = response_data.status_code
        case.Response_time = int((end_time - start_time) * 1000)
        case.Response_content = response_data.content
        case.save()
