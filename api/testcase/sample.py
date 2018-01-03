# -*- coding: utf-8 -*-
import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "platform3.settings")
django.setup()
import allure
import unittest
from api.models import ApiTest, ApiTestResultKey, apiList, project, ApiScript, env
from api.lib import request_handle
from time import time
import json
import os
import importlib


class TestApi(unittest.TestCase):

    def setUp(self):

        self.project_id, self.apiId, self.env, self.caseId = self.get_project_api_case_num()
        apiId = self.apiId
        caseId = self.caseId
        envId = self.env
        print("env %s" %envId)
        print(type(envId))
        base_path = os.path.join(os.getcwd(), "api/upload")
        script_path = os.path.join(base_path, str(apiId))
        try:
            setup_script_query = ApiScript.objects.filter(apiId=apiId)

            for script in setup_script_query:
                script_file = os.path.join(script_path, script.ScriptName)
                try:
                    script_name = "api.upload.api%s.%s" % (str(apiId), script.ScriptName[:-3])
                    setup_script = importlib.import_module(script_name)
                    setup_script.run()
                except Exception:
                    print("apiId:%s caseId:%s have error when run script_file: %s" %(apiId, caseId, script_file))
        except:
            print("apiId:%s caseId:%s have not setup script" % (apiId, caseId))


        try:
            self.test_obj = ApiTest.objects.get(apiId=apiId, CaseNum=caseId, env_id=self.env)
        except:
            print("no find case")
            print("apiId: %s , casenum: %s", (apiId, caseId))

        try:
            self.result_obj = ApiTestResultKey.objects.get(apiId=apiId)
        except:
            print("no find key")

        try:
            self.api_obj = apiList.objects.get(pk=apiId)
        except:
            print("no api")

        try:
            self.project_obj = project.objects.get(pk=self.api_obj.projectName_id)
        except:
            print("no project")

        try:
            self.env_obj = env.objects.get(pk=int(envId))
        except:
            print("no env")

        case_request = request_handle.requestHandle(project_obj=self.project_obj, api_obj=self.api_obj, project_env=self.env_obj.envName)
        params = self.params_fix(self.test_obj.TestParams)
        case_request.set_case_params(params=params)
        bodys = self.bodys_fix(self.test_obj.TestBodys)
        case_request.set_case_bodys(payload=bodys)
        print("request_params: %s" % params)
        print("request_bodys: %s" % bodys)
        start_time = time()
        response = case_request.request_send()
        end_time = time()
        print("request_content: %s" % response.content)

        self.test_obj.Response_code = response.status_code
        self.test_obj.Response_time = int((end_time - start_time) * 1000)
        self.test_obj.Response_content = response.content

        try:
            self.test_obj.save()
        except:
            print("save test_obj failed")

        self.except_content = eval(self.test_obj.Except_content)
        self.except_code = self.test_obj.Except_code
        self.except_time = self.test_obj.Except_time
        self.judge_logic = eval(self.test_obj.Judge_logic)
        self.judge_type = eval(self.test_obj.Judge_type)
        self.result_key = eval(self.result_obj.Result_key)
        self.result_key_type = eval(self.result_obj.Result_key_type)
        self.params = params
        self.bodys = self.bodys_fix_dict(self.test_obj.TestBodys)
        allure.attach("params", str(self.params))
        allure.attach("bodys", str(self.bodys))
        allure.attach("response_content", str(response.text))

        try:
            self.response_content = json.loads(response.content)
        except:
            print("response_content can not json loads")

    @allure.feature('123')
    @allure.story('321')
    def test_case(self):
        flag = True
        judge_result_dict = {}
        for key in self.result_key.keys():
            if self.result_key[key]:
                i = key[5:]
                judge_key = self.result_key[key]
                try:
                    expect_value = self.except_content["result_expect_value" + str(i)]
                except:
                    print("apiId:%s caseId:%s no have expect_value" % (self.apiId, self.caseId))
                judge_logic = self.judge_logic["result_judge_logic_value" + str(i)]
                judge_type = self.judge_type["result_judge_type" + str(i)]
                result_value = self.__response_with_key(self.response_content, judge_key)


                expect_value, result_value = self.__type_handle(
                    expect_value=expect_value, result_value=result_value, judge_type=judge_type)
                judge_flag = self.__judge_handle(
                    expect_value=expect_value, result_value=result_value, judge_logic=judge_logic, judge_type=judge_type)
                judge_result_dict["result" + str(i)] = judge_flag
                if not judge_flag:
                    allure.attach("assert error", "节点:%s数据类型:%s判断逻辑:%s" % (str(judge_key), str(judge_type), str(judge_logic)))
                    flag = False
        try:
            self.test_obj.Judge_result = judge_result_dict
            self.test_obj.save()
        except:
            print("apiId:%s caseId:%s save result failed" % (self.apiId, self.caseId))

        assert flag == True

    def tearDown(self):
        pass

    def params_fix(self, case_params):
        re_dict = {}
        params = eval(case_params)
        for key in params.keys():
            re_dict[key[7:]] = params[key]
        return re_dict

    def bodys_fix_dict(self, case_bodys):
        re_dict = {}
        params = eval(case_bodys)
        for key in params.keys():
            re_dict[key[6:]] = params[key]
        return re_dict


    def bodys_fix(self, case_bodys):
        re_payload = None
        if self.api_obj.post_method == "x-www-form-urlencoded":
            bodys = eval(case_bodys)
            for key in bodys.keys():
                if bodys[key]:
                    if re_payload:
                        re_payload = re_payload + "&%s=%s" % (key[6:], bodys[key])
                    else:
                        re_payload = "%s=%s" % (key[6:], bodys[key])
            return re_payload
        return re_payload

    def __response_with_key(self, json_data, json_key):
        key_list = []
        re_list = self.__key_list(json_key, key_list)
        data = json_data
        for char in re_list:
            char = self.__islist_index(char)
            try:
                data = data[char]
                if data or data == 0:
                    pass
                else:
                    data = "null"
            except Exception:
                data = "no node: %s" % json_key
        return data

    def __key_list(self, key, para_list):
        if key.find(".") != -1:
            count = key.find(".")
            para_list.append(key[:count])
            self.__key_list(key[count+1:], para_list)
        else:
            para_list.append(key)
        return para_list

    def __islist_index(self, char):
        re_char = char
        if char[:1] == "[" and char[-1:] == "]":
            re_char = int(char[1:-1])
        return re_char

    def __charge_type(self, target, type):
        if type == "Str":
            target = str(target)
        elif type == "Int":
            try:
                target = int(target)
            except Exception:
                pass
        return target

    def __type_handle(self, expect_value, result_value, judge_type):
        if judge_type == "Str":
            try:
                expect_value = str(expect_value)
            except:
                print("expect_value can not charge to str:%s" % expect_value)
            try:
                result_value = str(result_value)
            except:
                print("result_value can not charge to str:%s" % result_value)
        elif judge_type == "Int":
            try:
                expect_value = int(expect_value)
            except:
                print("expect_value can not charge to int:%s" % expect_value)
            try:
                result_value = int(result_value)
            except:
                print("result_value can not charge to int:%s" % result_value)
        return expect_value, result_value

    def __judge_handle(self, expect_value, result_value, judge_logic, judge_type):
        re_flag = True
        if judge_logic == "=":
            try:
                assert expect_value == result_value
            except:
                allure.attach("期待值不等于结果", "expect_value:%s 不等于 result_value:%s" % (str(expect_value), str(result_value)))
                re_flag = False
        elif judge_logic == "type":
            if expect_value == "list":
                try:
                    assert isinstance(result_value, list) == True
                except:
                    re_flag = False
                    allure.attach("期待值的类型不是队列", "expect_value:%s 的类型不是list" % str(expect_value))
            elif expect_value == "dict":
                try:
                    assert isinstance(result_value, dict) == True
                except:
                    re_flag = False
                    allure.attach("期待值的类型不是字典", "expect_value:%s 的类型不是dict" % str(expect_value))
        elif judge_logic == ">":
            try:
                assert result_value > expect_value
                allure.attach("期待值大于等于结果", "expect_value:%s  大于等于 result_value:%s" % (str(expect_value), str(result_value)))
            except:
                re_flag = False
        elif judge_logic == "<":
            try:
                assert result_value < expect_value
            except:
                re_flag = False
                allure.attach("期待值小于等于结果", "expect_value:%s  小于等于 result_value:%s" % (str(expect_value), str(result_value)))
        elif judge_logic == "python":
            base_path = os.path.join(os.getcwd(), "api/upload")
            api_path = os.path.join(base_path, str(self.apiId))
            script_file = os.path.join(api_path, expect_value)
            try:
                script_name = "api.upload.api%s.%s" % (str(self.apiId), expect_value[:-3])
                setup_script = importlib.import_module(script_name)
                res = setup_script.run(params=self.params, bodys=self.bodys)
            except:
                print("apiId:%s caseId:%s 执行脚本%s出错" % (self.apiId, self.caseId, script_file))
                res = "脚本运行出错"
                allure.attach("脚本运行出错",
                              "apiId:%s caseId:%s 执行脚本%s出错" % (self.apiId, self.caseId, script_file))


            res, result_value = self.__type_handle(expect_value=res, result_value=result_value, judge_type=judge_type)
            try:
                assert res == result_value
            except:
                re_flag = False
                allure.attach("脚本返回值不等于结果", "脚本返回值:%s  不等于 result_value:%s" % (str(res), str(result_value)))

        return re_flag

    def get_project_api_case_num(self):
        path_file = os.path.split(__file__)
        file = path_file[1]
        path = path_file[0]
        file_index = file.find("_")
        case_num = file[4:file_index]

        env_index = path.rfind("/")
        env_num = path[env_index+1:]

        api_path = path[:env_index]
        api_index = api_path.rfind("/")
        api_num = api_path[api_index+1:]

        project_path = api_path[:api_index]
        project_index = project_path.rfind("/")
        project_num = project_path[project_index+1:]

        return project_num, api_num, env_num, case_num