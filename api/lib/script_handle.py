# -*- coding: utf-8 -*-
import os, stat, shutil


def save_script(work_path, apiId, filename):
    base_path = os.path.join(work_path, "api/upload")
    filename = str(filename)
    os.chmod(base_path, stat.S_IRWXU)


    os.chmod(base_path, stat.S_IRWXU)
    api_path = os.path.join(base_path, "api" + str(apiId))
    if not os.path.exists(api_path):
        os.makedirs(api_path)
        os.chmod(api_path, stat.S_IRWXU)
        shutil.copy(os.path.join(base_path, "__init__.py"), os.path.join(api_path, "__init__.py"))

    shutil.move(os.path.join(base_path, filename), os.path.join(api_path, filename))

def del_script(work_path, apiId, exist_file_list):
    base_path = os.path.join(work_path, "api/upload")
    api_path = os.path.join(base_path, "api" + str(apiId))
    file_list = os.listdir(api_path)
    for file in file_list:
        if not file in exist_file_list:
            filename = os.path.join(api_path, file)
            init_file = os.path.join(api_path, "__init__.py")
            if filename != init_file:
                os.remove(filename)