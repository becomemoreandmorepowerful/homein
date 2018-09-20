from flask import json

# value = [{"key1": "value1"}]  # 列表包字典
# a = {"key": value}  # 字典，键是key 值应该是一个列表包字典
# json_str = json.dumps(a)
#
# print(json_str)
# print(a)
# print(type(json_str))
# print(type(a))


value1 = '[{"key1": "value1"}]'  # 字符串
b = {"key": value1}  # 字典，键是key 值应该是一个字符串
json_str1 = json.dumps(b)  # {"key": "[{'key1': 'value1'}]"}
print(json_str1)

value2 = '[{"key1": "value1"}]'  # 字符串
json_str3 = "{'key': %s}" % value2    #  {'key': [{'key1': 'value1'}]}
print(json_str3)
