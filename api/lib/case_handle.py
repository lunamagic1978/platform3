import os
import shutil


def create_case(projectId, apiId, case_num, project_name, api_name, env_id):
    path, sample_path = create_fold(projectId=projectId, apiId=apiId, env_id=env_id)
    file_list = os.listdir(path)
    for file in file_list:
        file_name = os.path.join(path, file)
        if os.path.isfile(file_name):
            os.remove(file_name)
        # else:
        #     shutil.rmtree(file_name)
    if case_num != 0:
        for i in range(1, case_num+1, 1):
            filename = "case%s_%s_%s_%s_test.py" % (i, projectId, apiId, env_id)

            create_file(sample_path=sample_path, path=path, filename=filename,
                            project_name=project_name, api_name=api_name)


def create_fold(projectId, apiId, env_id):
    path = os.getcwd()
    root_path = os.path.join(path, "api/testcase")
    project_path = os.path.join(root_path, projectId)
    api_path = os.path.join(project_path, apiId)
    env_path = os.path.join(api_path, env_id)
    if not os.path.exists(env_path):
        os.makedirs(env_path)
    return env_path, root_path


def create_file(sample_path, path, filename, project_name, api_name):
    sample_file = os.path.join(sample_path, "sample.py")
    target_file = os.path.join(path, filename)
    source = open(sample_file, "r", encoding="utf-8")
    target = open(target_file, "w", encoding="utf-8")
    for line in source:
        if "@allure.feature" in line:
            feature = "    @allure.feature('%s')\n" % project_name
            target.write(feature)
        elif "@allure.story" in line:
            story = "    @allure.story('%s')\n" % api_name
            target.write(story)
        else:
            target.write(line)
    target.close()