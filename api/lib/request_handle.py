# -*- coding: utf-8 -*-
import requests
from api.models import ApiTest
from time import time

class requestHandle():

    def __init__(self, project_obj, api_obj):
        self.host = project_obj.host
        self.url = api_obj.url
        self.request_method = api_obj.request_method
        self.request_protocol = api_obj.request_protocol
        self.port = project_obj.port
        self.params = {}
        self.headers = {}

    def set_params(self, key, value):
        if value:
            self.params[key] = value

    def set_case_params(self, params):
        self.params = params

    def request_send(self, env):
        headers = {}

        if env == "Online":
            url = self.request_protocol + "://" + self.host + ":" + self.port + self.url
        elif env == "158":
            headers['host'] = self.host
            url = self.request_protocol + "://" + "123.59.42.158" + ":" + self.port + self.url
        elif env == '230':
            headers['host'] = self.host
            url = self.request_protocol + "://" + "180.150.179.230" + ":" + self.port + self.url

        response_data = requests.request(method=self.request_method, url=url, params=self.params, headers=headers)
        print(response_data.content)
        return response_data


def testCaseExec(apiId, project_obj, api_obj, env):

    testCases = ApiTest.objects.filter(apiId_id=apiId)
    for case in testCases:
        params_dict = eval(case.TestParams)
        params_dict_fix = {}
        for key in params_dict.keys():
            params_dict_fix[key[7:]] = params_dict[key]

        request_Handle = requestHandle(project_obj=project_obj, api_obj=api_obj)
        request_Handle.set_case_params(params_dict_fix)
        start_time = time()
        response_data = request_Handle.request_send(env=env)
        end_time = time()
        case.Response_code = response_data.status_code
        case.Response_time = int((end_time - start_time) * 1000)
        case.Response_content = response_data.content
        case.save()
