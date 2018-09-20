from flask import session, g, jsonify
from werkzeug.routing import BaseConverter
from ihome.utils.response_code import RET
from functools import wraps

class RegexConverter(BaseConverter):
    '''自定义接受正则表达式的路由转换器'''
    def __init__(self, url_map, regex):
        '''regex是路由中的正则表达式'''
        super(RegexConverter, self).__init__(url_map)
        self.regex = regex



# # 定义登录装饰器函数
# def login_required(view_func):
#     def wrapper(*args, **kwargs):
#         # 从session中取出用户的Id
#         user_id = session.get('user_id')
#         # 用户已经登录
#         if user_id is not None:
#             # 使用g对象保存user_id，方便在视图函数中使用
#             g.user_id = user_id
#             return view_func(*args, *(kwargs))
#         else:
#             resp = {
#                 'errno':RET.SESSIONERR,
#                 'errmsg':'用户未登录'
#             }
#             return jsonify(resp)
#     return wrapper

def login_required(view_func):
    """检验用户的登录状态"""
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        user_id = session.get("user_id")
        if user_id is not None:
            # 表示用户已经登录
            # 使用g对象保存user_id，在视图函数中可以直接使用
            g.user_id = user_id
            return view_func(*args, **kwargs)
        else:
            # 用户未登录
            resp = {
                "errno": RET.SESSIONERR,
                "errmsg": "用户未登录"
            }
            return jsonify(resp)
    return wrapper
