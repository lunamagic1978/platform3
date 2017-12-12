# -*- coding: utf-8 -*-
from django import forms
from django.forms import ModelForm, BaseFormSet
from .models import project, apiList, ApiParams, ApiTest, ApiTestResultKey, ApiScript
from django.forms import  BaseInlineFormSet
from django.forms.fields import BooleanField, IntegerField
from .lib import testcase_handle

METHOD_CHOICE = (('GET', 'GET'),
                 ('POST', 'POST'),
                 )

PROTOCOL_CHOICE = (('HTTP', 'HTTP'),
                   ('HTTPS', 'HTTPS'),
                   )

ENV_CHOICE = (('Online', 'Online'),
              ('158', '158'),
              ('230', '230'),
                   )

TYPE_CHOICE = (('Str', 'Str'),
               ('Int', 'Int'),
               ('List', 'List'),
               ('Dict', 'Dict'),)


LOGIC_CHOICE = (('=', '='),
                ('>', '>'),
                ('<', '<'),
               ('type', 'type'),
               ('python', 'python'),
               ('in', 'in'),)


class createProject(ModelForm):

    class Meta:
        model = project

        fields = ('name', 'host', 'port')


class createApi(ModelForm):

    request_methond = forms.ChoiceField()
    request_protocol = forms.ChoiceField()

    def __init__(self, *args, **kwargs):
        super(createApi, self).__init__(*args, **kwargs)
        self.fields['request_methond'].choices = METHOD_CHOICE
        self.fields['request_methond'].widget.attrs["class"] = "form-control"

        self.fields['request_protocol'].choices = PROTOCOL_CHOICE
        self.fields['request_protocol'].widget.attrs["class"] = "form-control"

    class Meta:
        model = apiList
        fields = ('apiName', 'url')


class DebugApiParamsForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super(DebugApiParamsForm, self).__init__(*args, **kwargs)

    class Meta:
        model = ApiParams
        fields = ('key_value', 'key')


class CustomInlineFormSet(BaseInlineFormSet):

    def __init__(self, *args, **kwargs):
        super(CustomInlineFormSet, self).__init__(*args, **kwargs)
        for form in self.forms:
            form.fields['key_value'].label = form.instance.key
            form.fields['key'].widget.attrs["style"] = "width:100%;"
            form.fields['key_value'].widget.attrs["style"] = "width:100%;"


class DebugEnv(ModelForm):
    env = forms.ChoiceField(widget=forms.Select)

    def __init__(self, *args, **kwargs):
        super(DebugEnv, self).__init__(*args, **kwargs)
        if 'instance' in kwargs:
            self.fields['env'].initial = kwargs['instance'].env
        self.fields['env'].choices = ENV_CHOICE

    class Meta:
        model = apiList
        fields = ('env',)


class ExpectKey(forms.Form):

    response_code = forms.CharField()
    response_time = forms.CharField()

    def __init__(self,*args, **kwargs):
        super(ExpectKey, self, ).__init__(*args, **kwargs)
        self.fields['response_code'].initial = "code"
        self.fields['response_time'].initial = "time"
        self.fields['response_code'].widget.attrs["style"] = "width:100%;"
        self.fields['response_code'].widget.attrs["readonly"] = True
        self.fields['response_time'].widget.attrs["style"] = "width:100%;"
        self.fields['response_time'].widget.attrs["readonly"] = True
        result_key_obj = ApiTestResultKey.objects.get_or_create(apiId=kwargs['initial']['apiId'])[0]

        for i in range (1, 11, 1):
            fields_name = 'value' + str(i)
            self.fields[fields_name] = forms.CharField()
            self.fields[fields_name].widget.attrs["style"] = "width:100%;"
            self.fields[fields_name].required = False

            try:
                if result_key_obj:
                    result_key_dict = eval(result_key_obj.Result_key)
                    self.fields[fields_name].initial = result_key_dict[fields_name]
            except Exception:
                pass


class ExpectKey_Type(forms.Form):

    codetype = forms.ChoiceField(choices=(('Str', 'Str'),))
    timetype = forms.ChoiceField(choices=(('Int', 'Int'),))

    def __init__(self,*args, **kwargs):
        super(ExpectKey_Type, self, ).__init__(*args, **kwargs)
        result_key_type_obj = ApiTestResultKey.objects.get_or_create(apiId=kwargs['initial']['apiId'])[0]

        for i in range (1, 11, 1):
            fields_name = 'value' + str(i)
            fields_type = fields_name + 'type'

            self.fields[fields_type] = forms.ChoiceField(choices=TYPE_CHOICE)
            try:
                if result_key_type_obj:
                    result_key_type_dict = eval(result_key_type_obj.Result_key_type)
                    self.fields[fields_type].initial = result_key_type_dict[fields_type]

            except Exception:
                pass


class Case(forms.Form):

    case_num = forms.CharField()
    result_expect_code = forms.CharField()
    result_expect_time = forms.CharField()
    result_response_code = forms.CharField()
    result_response_time = forms.CharField()
    result_judge_logic_code = forms.ChoiceField(choices=LOGIC_CHOICE)
    result_judge_logic_time = forms.ChoiceField(choices=LOGIC_CHOICE)

    def __init__(self, *args, **kwargs):
        super(Case, self).__init__(*args, **kwargs)
        self.fields["case_num"].required = False
        self.fields["result_expect_code"].required = False
        self.fields["result_expect_time"].required = False
        self.fields["result_response_code"].required = False
        self.fields["result_response_time"].required = False

        # print(args)
        # print(kwargs)
        if 'prefix' in kwargs:
            case_num = kwargs['prefix'][5:]
        else:
            case_num = "1"

        apiId = kwargs['initial']['apiId']
        params_query = ApiParams.objects.filter(apiId=apiId) #根据外键找到params的字段

        try:
            result_key_dict = eval(ApiTestResultKey.objects.get(apiId=apiId).Result_key)
        except Exception:
            result_key_dict = {}

        try:
            result_key_type_dict = eval(ApiTestResultKey.objects.get(apiId=apiId).Result_key_type)
        except Exception:
            result_key_type_dict = {}


        try:
            case_data = ApiTest.objects.get(apiId=apiId, CaseNum=str(int(case_num)+1)) #根据formset的form索引来找到对应的case，具体编号为索引+1
            case_data_flag = True
        except:
            case_data = {} #不存在数据就给一个空字典
            case_data_flag = False

        try:
            except_content = case_data.Except_content
        except:
            except_content = {}

        try:
            response_content = case_data.Response_content
        except:
            response_content = {}

        try:
            judge_logic_content = case_data.Judge_logic
        except:
            judge_logic_content = {}


        if case_data_flag: #根据case_data_flag 判断是否有测试用例
            params_dict = eval(case_data.TestParams)
            casenum = case_data.CaseNum
        else:
            params_dict = {}
            casenum = False

        if casenum:
            self.fields['case_num'].initial = case_data.CaseNum
        for item in params_query:
            fields_name = 'params_' + item.key
            self.fields[fields_name] = forms.CharField()
            self.fields[fields_name].widget.attrs["style"] = "width:100%;"
            self.fields[fields_name].required = False
            if fields_name in params_dict.keys():
                self.fields[fields_name].initial = params_dict[fields_name]




        self.fields['case_num'].widget.attrs["style"] = "width:100%;"
        self.fields['result_expect_code'].widget.attrs["style"] = "width:100%;"
        self.fields['result_expect_time'].widget.attrs["style"] = "width:100%;"
        self.fields['result_response_code'].widget.attrs["style"] = "width:100%;"
        self.fields['result_response_time'].widget.attrs["style"] = "width:100%;"
        self.fields['result_judge_logic_code'].widget.attrs["style"] = "width:100%;"
        self.fields['result_judge_logic_time'].widget.attrs["style"] = "width:100%;"
        self.fields['result_expect_time'].initial = "1"

        try:
            new_code = case_data.Except_code
            self.fields['result_expect_code'].initial = new_code
        except Exception:
            self.fields['result_expect_code'].initial = "200"
            new_code = False

        try:
            new_time = case_data.Except_time
            self.fields['result_expect_time'].initial = new_time
        except Exception:
            self.fields['result_expect_time'].initial = "1"
            new_time = False

        try:
            response_code = case_data.Response_code
            self.fields['result_response_code'].initial = response_code
        except Exception:
            response_code = False

        try:
            response_time = case_data.Response_time
            self.fields['result_response_time'].initial = response_time
        except Exception:
            response_time = False


        for i in range(1, 11, 1):
            expect_name = "result_expect_value" + str(i)
            response_name = "result_response_value" + str(i)
            judge_logic = "result_judge_logic_value" + str(i)
            self.fields[expect_name] = forms.CharField()
            self.fields[expect_name].widget.attrs["style"] = "width:100%;"
            self.fields[expect_name].required = False
            self.fields[response_name] = forms.CharField()
            self.fields[response_name].widget.attrs["style"] = "width:100%;"
            self.fields[response_name].required = False
            self.fields[judge_logic] = forms.ChoiceField(choices=LOGIC_CHOICE)
            self.fields[judge_logic].widget.attrs["style"] = "width:100%;"

        if except_content != "{}":
            try:
                except_content_dict = eval(except_content)
            except:
                except_content_dict = {}
            for key in except_content_dict.keys():
                self.fields[key].initial = except_content_dict[key]

        if judge_logic_content != "{}":
            try:
                judge_logic_dict = eval(judge_logic_content)
            except:
                judge_logic_dict = {}
            for key in judge_logic_dict.keys():
                self.fields[key].initial = judge_logic_dict[key]

        if new_code and response_code:
            if new_code == response_code:
                self.fields['result_response_code'].widget.attrs["style"] = "width:100%; background: aquamarine"
            else:
                self.fields['result_response_code'].widget.attrs["style"] = "width:100%; background: red"

        if new_time and response_time:
            if int(new_time) >= int(response_time):
                self.fields['result_response_time'].widget.attrs["style"] = "width:100%; background: aquamarine"
            else:
                self.fields['result_response_time'].widget.attrs["style"] = "width:100%; background: red"


        if except_content != "{}" and response_content != "{}":
            judge_case_handle = testcase_handle.JudgeCaseHandle(except_content=except_content, response_content=response_content, params_dict=params_dict)
            for key in result_key_dict.keys():
                if result_key_dict[key]:
                    flag, resopnse_value = judge_case_handle.judge_by_key(key=result_key_dict[key], value=key, apiId=apiId,
                                key_type=result_key_type_dict[key + 'type'], logic=judge_logic_dict['result_judge_logic_' + key])
                    if flag:
                        self.fields['result_response_' + key].widget.attrs["style"] = "width:100%;  background: aquamarine"
                        self.fields['result_response_' + key].initial = resopnse_value
                    else:
                        self.fields['result_response_' + key].widget.attrs["style"] = "width:100%;  background: #FFE4E1"
                        self.fields['result_response_' + key].initial = resopnse_value

class ORDER_FIXED(BaseFormSet):

    def add_fields(self, form, index):
        """A hook for adding extra fields on to each form instance."""
        if self.can_order:
            # Only pre-fill the ordering field for initial forms.
            if index is not None and index < self.initial_form_count():
                form.fields['ORDER'] = IntegerField(label='Order', initial=index + 1, required=False)
                form.fields['ORDER'].widget.attrs["style"] = "width:30px;"
                form.fields['ORDER'].widget.attrs["readonly"] = True
            else:
                form.fields['ORDER'] = IntegerField(label='Order', required=False)
        if self.can_delete:
            form.fields['DELETE'] = BooleanField(label='DELETE', required=False)

    def save(self, datas, apiId, result_key, result_key_type):
        result_key_obj = ApiTestResultKey.objects.get_or_create(apiId=apiId)[0]
        result_key_obj.Result_key = result_key
        result_key_obj.Result_key_type = result_key_type
        result_key_obj.save()

        for data in datas:
            # print(data)
            case_num = data['ORDER']
            testcase_data = testcase_handle.TestCaseHandle(data)
            params_dict = testcase_data.params_handle()
            new_code = testcase_data.code_handle()
            new_time = testcase_data.time_handle()
            new_except_content = testcase_data.except_content_hanele(result_key_dict=result_key)
            new_judge_logic = testcase_data.judge_logic_handle()
            obj = ApiTest.objects.get_or_create(apiId=apiId, CaseNum=case_num)[0]
            obj.TestParams = params_dict
            obj.Except_code = new_code
            obj.Except_time = new_time
            obj.Judge_logic = new_judge_logic
            obj.Except_content = new_except_content
            obj.save()


class Script(ModelForm):
    ScriptTpye = forms.ChoiceField(choices=(("normalScript", "normalScript"),
                                            ("prepareScript", "prepareScript"),))
    class Meta:
        model = ApiScript

        fields = ('ScriptTpye', 'ScriptFile')