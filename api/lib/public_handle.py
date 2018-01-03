# -*- coding: utf-8 -*-
from api.models import env
import os

def case_default_env(projectId):
    try:
        obj = env.objects.filter(projectId=projectId, default=True)
        if not obj:
            obj = env.objects.filter(projectId=projectId, default=False)
    except Exception:
        print("获取默认环境出错")
    return obj[0].pk

def os_run(projectId, apiId, envId):
    path = os.getcwd()
    case_path = "%s/api/testcase/%s/%s/%s" % (path, projectId, apiId, envId)
    os.system("pytest %s" % case_path)