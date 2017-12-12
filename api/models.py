# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from datetime import datetime

# Create your models here.


TYPE_CHOICE = (("str", "str"),
               ("int", "int"),)

class project(models.Model):
    name = models.CharField(max_length=100)
    host = models.CharField(max_length=100)
    port = models.CharField(max_length=10)


class apiList(models.Model):
    projectName = models.ForeignKey(project, on_delete=models.CASCADE)
    apiName = models.CharField(max_length=100)
    url = models.CharField(max_length=100)
    request_method = models.CharField(max_length=100)
    creater = models.CharField(max_length=100)
    request_protocol = models.CharField(max_length=100, default="http")
    env = models.CharField(max_length=100, default="Online")

    def __str__(self):
        return self.apiName


class ApiDetail(models.Model):

    apiId = models.ForeignKey(apiList, on_delete=models.CASCADE)
    debug_sample = models.CharField(max_length=1000, blank=True, null=True)


class ApiParams(models.Model):
    apiId = models.ForeignKey(apiList, on_delete=models.CASCADE)
    key = models.CharField(max_length=1000, null=True)
    key_type = models.CharField(max_length=1000, choices=TYPE_CHOICE, default="str")
    key_must = models.BooleanField(default=True)
    key_default = models.CharField(max_length=1000, null=True, blank=True)
    key_description = models.CharField(max_length=1000, null=True, blank=True)
    key_value = models.CharField(max_length=1000, null=True, blank=True)

    def __str__(self):
        return self.apiId


class ApiBody(models.Model):
    apiId = models.ForeignKey(apiList, on_delete=models.CASCADE)
    body = models.CharField(max_length=1000, null=True)
    body_type = models.CharField(max_length=1000, choices=TYPE_CHOICE, default="str")
    body_must = models.BooleanField(default=True)
    body_default = models.CharField(max_length=1000, null=True, blank=True)
    body_description = models.CharField(max_length=1000, null=True, blank=True)

    def __str__(self):
        return self.apiId


class ApiDebug(models.Model):
    apiId = models.ForeignKey(apiList, on_delete=models.CASCADE)
    apiHead = models.CharField(max_length=1000, blank=True, null=True)
    apiParams = models.CharField(max_length=1000, blank=True, null=True)
    apiBodys = models.CharField(max_length=1000, blank=True, null=True)
    createTime = models.DateTimeField("createTime", default=datetime.now)


class ApiTest(models.Model):
    apiId = models.ForeignKey(apiList, on_delete=models.CASCADE)
    TestHead = models.CharField(max_length=1000, blank=True, null=True)
    TestParams = models.CharField(max_length=1000, blank=True, null=True)
    TestBodys = models.CharField(max_length=1000, blank=True, null=True)
    Response_code = models.CharField(max_length=10, blank=True, null=True)
    Response_time = models.CharField(max_length=100, blank=True, null=True)
    Response_content = models.CharField(max_length=15000, blank=True, null=True)
    Except_code = models.CharField(max_length=10, blank=True, null=True)
    Except_time = models.CharField(max_length=100, blank=True, null=True)
    Except_content = models.CharField(max_length=1000, blank=True, null=True)
    CaseNum = models.CharField(max_length=1000, blank=True, null=True)
    Judge_logic = models.CharField(max_length=1000, blank=True, null=True)


class ApiTestResultKey(models.Model):
    apiId = models.ForeignKey(apiList, on_delete=models.CASCADE)
    Result_key = models.CharField(max_length=1000, blank=True, null=True)
    Result_key_type = models.CharField(max_length=1000, blank=True, null=True)


class ApiScript(models.Model):
    apiId = models.ForeignKey(apiList, on_delete=models.CASCADE)
    ScriptName = models.CharField(max_length=100, blank=True, null=True)
    ScriptTpye = models.CharField(max_length=100, blank=True, null=True)
    ScriptFile = models.FileField(upload_to='./api/upload')
    createTime = models.DateTimeField("createTime", default=datetime.now)
    updateTime = models.DateTimeField("updateTime", default=datetime.now)
    author = models.CharField(max_length=100, blank=True, null=True)