# -*- coding: utf-8 -*-

import os

class TestCaseHandle():

    def __init__(self, data):
        self.data = data
        self.except_content = {}
        self.response_content = {}

    def params_handle(self):
        params_dict = {}
        data = self.data
        for key in data.keys():
            if key.startswith('params'):
                if data[key]:
                    params_dict[key] = data[key]
        return params_dict

    def code_handle(self):
        _data = self.data
        re_code = _data['result_expect_code']
        return re_code

    def time_handle(self):
        _data = self.data
        re_time = _data['result_expect_time']
        return re_time

    def except_content_hanele(self, result_key_dict):
        _data = self.data
        _re_dict ={}
        _result_key_dict = result_key_dict
        for key in _result_key_dict.keys():
            if _data['result_expect_' + key]:
                _re_dict['result_expect_' + key] = _data['result_expect_' + key]
        return _re_dict

    def judge_logic_handle(self):
        _data = self.data
        _re_dict = {}
        for i in range (1, 11, 1):
            key_name = "result_judge_logic_value" + str(i)
            _re_dict[key_name] = _data[key_name]
        return _re_dict

class JudgeCaseHandle():

    def __init__(self, except_content, response_content, params_dict):
        self.except_content = except_content
        self.response_content = response_content
        self.params_dict = params_dict

    def judge_by_key(self, key, value, key_type, logic, apiId):
        if self.except_content:
            except_content_dict = eval(self.except_content)
        else:
            except_content_dict = {}

        if self.response_content:
            response_value_dict = eval(self.response_content)
        else:
            response_value_dict = {}

        if except_content_dict and response_value_dict:
            try:
                except_value = except_content_dict['result_expect_' + value]
            except Exception:
                except_value = "1"

            response_value = self.__response_with_key(response_value_dict, key)

            # if key_type == "Str":
            #     except_value = str(except_value)
            # elif key_type == "Int":
            #     try:
            #         except_value = int(except_value)
            #     except Exception:
            #         pass

            except_value = self.__charge_type(except_value, key_type)

            try:
                if logic == "=":
                    assert except_value == response_value
                elif logic == "type":
                    if except_value == "list":
                        if isinstance(response_value, list):
                            pass
                        else:
                            return False, response_value
                    elif except_value == "dict":
                        if isinstance(response_value, dict):
                            pass
                        else:
                            return False, response_value
                    else:
                        return False, response_value
                elif logic == ">":
                    assert except_value > response_value
                elif logic == "<":
                    assert except_value < response_value
                elif logic == "python":
                    base_path = os.path.join(os.getcwd(), "api/upload")
                    api_path = os.path.join(base_path, str(apiId))
                    script_file = os.path.join(api_path, except_content_dict['result_expect_%s' % value])
                    kwargs =""
                    for param_key in self.params_dict.keys():
                        kwargs = kwargs + " %s=%s" % (param_key[7:], self.params_dict[param_key])
                    result = os.popen("python3 %s%s" % (script_file, kwargs))
                    res = result.read()
                    except_value = self.__charge_type(res, key_type)
                    assert except_value == response_value
                elif logic == "in":
                    print("logic is in")
                return True, response_value
            except Exception:
                return False, response_value
        else:
            return False, ""

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




