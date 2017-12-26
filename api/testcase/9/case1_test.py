# -*- coding: utf-8 -*-
import pytest
import allure
import unittest
from api.models import ApiTest, ApiTestResultKey, apiList

class TestApi(unittest.TestCase):

    def setUp(self):
        apiId = 9
        caseId = 1
        try:
            self.obj = ApiTest.objects.get(apiId=apiId, CaseNum=caseId)
        except:
            print("no find case")
        try:
            self.result_obj = ApiTestResultKey.objects.get(apiId=apiId)
        except:
            print("no find key")



        self.params = self.obj.TestParams
        self.bodys = self.obj.TestBodys
        self.heads = self.obj.TestHead
        self.except_content = self.obj.Except_content
        self.except_code = self.obj.Except_code
        self.except_time = self.obj.Except_time
        self.judge_logic = self.obj.Judge_logic
        self.result_key = self.result_obj.Result_key
        self.result_key_type = self.result_obj.Result_key_type

    def test_case(self):
        print(self.params)
        print(self.heads)
        print(self.bodys)
        print(self.except_content)
        print(self.except_code)
        print(self.except_time)
        print(self.judge_logic)
        print(self.result_key)
        print(self.result_key_type)
        a = "a"
        b = "b"
        assert a == b

    def tearDown(self):
        print("teardonw")