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
            key_name = "result_judge_logic" + str(i)
            _re_dict[key_name] = _data[key_name]
        return _re_dict

class JudgeCaseHandle():

    def __init__(self, except_content, response_content):
        self.except_content = except_content
        self.response_content = response_content
        print(except_content)
        print(response_content)

    def judge_by_key(self, key, value, key_type):
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
                except_value = ""

            try:

                if response_value_dict[key] or response_value_dict[key] == 0:
                    response_value = response_value_dict[key]
                else:
                    response_value = "null"
            except Exception:
                response_value = "节点%s不存在" % key

            if key_type == "Str":
                except_value = str(except_value)
            elif key_type == "Int":
                except_value = int(except_value)

            try:
                assert except_value == response_value
                return True, response_value
            except Exception:
                return False, response_value
        else:
            return False, ""
