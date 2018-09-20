import re
from flask import request, jsonify, current_app, session
from ihome import redis_store, db, constants
from ihome.api_1_0 import api
from ihome.models import User
from ihome.utils.response_code import RET

# POST /api/v1_0/users
# @api.route('/users', methods=['POST'])
@api.route("/users", methods=["POST"])
def register():
    '''用户注册'''

    # 接受参数, 手机号、短信验证码、密码, json格式的数据
    # json.loads(request.data)
    # request.get_json方法能够帮助将请求体的json数据转换为字典
    req_dict = request.get_json()
    mobile = req_dict.get('mobile')
    sms_code = req_dict.get('sms_code')
    password = req_dict.get('password')
    # print(password)
    # 校验参数
    # 完整性校验参数
    if not all([mobile, sms_code, password]):
        resp = {
            'errno': RET.PARAMERR,
            'errmsg': '参数不完整'
        }
        return jsonify(resp)

    # 手机号的正则匹配校验
    if not re.match(r"1[3456789]\d{9}", mobile):
        resp = {
            'errno': RET.DATAERR,
            'errmsg': '手机号格式错误'
        }
        return jsonify(resp)

    # 进行逻辑处理
    # 从redis中获取手机验证码
    try:
        real_sms_code = redis_store.get('sms_code_%s' %mobile )
    except Exception as e:
        current_app.logger.error(e)
        resp = {
            'errno': RET.DBERR,
            'errmsg': '查询验证码错误'
        }
        return jsonify(resp)

    # 判断验证码的有效期
    if real_sms_code is None:
        resp = {
            'errno': RET.NODATA,
            'errmsg': '验证码已经过期'
        }
        return jsonify(resp)

    # 比对从数据库中获取的验证码和用户输入的验证码
    real_sms_code = real_sms_code.decode('utf-8')
    if real_sms_code != sms_code:
        resp = {
            'errno': RET.DATAERR,
            'errmsg': '验证码输入有误'
        }
        return jsonify(resp)

    # 用户输入正确后将验证码从数据库删除
    try:
        redis_store.delete('sms_code_%s' %mobile)
    except Exception as e :
        current_app.logger.error(e)

    # 在mysql数据库中相应的表中保存用户的用户名，密码，以及手机号
    # try:
    #     user = User.query.filter_by(mobile=mobile).first()
    # except Exception as e :
    #     current_app.logger.error(e)
    #     resp = {
    #         'errno': RET.DBERR,
    #         'errmsg': '数据库有误'
    #     }
    #     return jsonify(resp)
    # if user is None:
    #     resp = {
    #         'errno': RET.DATAEXIST,
    #         'errmsg': '手机号已经被注册'
    #     }
    #     return jsonify(resp)
    # user = User(name=mobile, mobile=mobile)
    user = User(name=mobile, mobile=mobile)
    # 对于password属性的设置，会调用属性方法，进行加密操作
    user.password = password
    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        resp = {
            'errno': RET.DATAEXIST,
            'errmsg': '手机号已经被注册'
        }
        return jsonify(resp)

    # 在session中记录用户的登录状态
    session["user_id"] = user.id
    session["user_name"] = mobile
    session["mobile"] = mobile

    # 返回值
    resp = {
        'errno':RET.OK,
        'errmsg':'注册成功'
    }
    return jsonify(resp)


@api.route('/sessions', methods=["POST"])
def login():
    '''用户登录'''
    # 获取参数
    req_dict = request.get_json()
    password = req_dict.get('password')
    mobile = req_dict.get('mobile')

    # 校验参数
    # 完整性校验
    if not all([password, mobile]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数不完整')
    # 手机号正确性校验
    if not re.match(r"1[3456789]\d{9}", mobile):
        return jsonify(errno=RET.PARAMERR, errmsg='手机号格式不正确')

    # 业务逻辑处理
    # 判断用户登录的错误次数
    # 获取用户登录的id地址
    user_ip = request.remote_addr
    try:
        access_counts = redis_store.get("access_%s" %user_ip)
    except Exception as e :
        current_app.logger.error(e)

    else:
        # 如果有错误次数，并且已经超过最大的允许次数，直接返回
        # access_counts = access_counts.decode("utf-8")
        if access_counts is not None and int(access_counts.decode("utf-8"))>=constants.LOGIN_ERROR_MAX_NUM:
            return jsonify(errno=RET.REQERR, errmsg='请求过于频繁')

    # 查询用户信息，判断用户输入的数据
    try:
        user = User.query.filter_by(mobile=mobile).first()
    except Exception as e :
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询数据异常')
    # 没有从数据库中查询到用户的信息，或者用户密码输入错误
    if user is None or not user.check_password(password):
        try :
            # 在redis数据库中累计用户登录次数
            redis_store.incr("access_%s" %user_ip)
            # 如果用户登录次数超过上限， 设置禁止登录的时间
            redis_store.expire("access_%s" %user_ip, constants.LOGIN_ERROR_FORBID_TIME)
        except Exception as e :
            current_app.logger.error(e)
        return jsonify(errno=RET.LOGINERR, errmsg="用户名或者密码有问题")

    # 返回值
    # 登录成功，清除用户的登录次数
    try:
        redis_store.delete("access_%s" %user_ip)
    except Exception as e :
        current_app.logger.errorr(e)

    # 登录成果后记录用户的登录状态
    session['user_id'] = user.id
    session['user_name'] = user.name
    session["mobile"] = user.mobile

    return jsonify(errno=RET.OK, errmsg="登录成功")


@api.route("/session", methods=["GET"])
def check_login():
    '''检查用户的登录状态'''
    # 从session中获取用户的信息
    name = session.get("user_name")
    # print(name)
    # 如果session中数据name名字存在，则表示用户已登录，否则未登录
    if name is not None:
        return jsonify(errno=RET.OK, errmsg="true", data={"name":name})
    else:
        return jsonify(errno=RET.SESSIONERR, errmsg="false")


@api.route("/session", methods=["DELETE"])
def logout():
    '''用户退出登录'''
    session.clear()
    return jsonify(errno=RET.OK, errmsg="ok")



