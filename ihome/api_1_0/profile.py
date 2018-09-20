from flask import g, request, jsonify, current_app, session

from ihome import constants, db
from ihome.api_1_0 import api
from ihome.models import User
from ihome.utils.commons import login_required
from ihome.utils.image_storage import storage
from ihome.utils.response_code import RET


@api.route('/users/avatar', methods=['POST'])
@login_required
def set_user_avatar():
    '''设置用户头像'''
    # 获取参数
    user_id = g.user_id
    image_file = request.files.get('avatar')

    # 校验参数
    if image_file is None:
        return jsonify(errno=RET.PARAMERR, errmsg='参数不完整')

    # 逻辑处理
    # 将用户上传的图片存储在七牛服务器
    # 获取图片的内容
    image_data = image_file.read()

    try:
        # 将图片的内容存储到服务器
        file_name = storage(image_data)
    except Exception as e :
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR, errmsg='上传头像异常')

    # 将用户上传的图片保存到用户表的表中
    # print(file_name)
    try:
        User.query.filter_by(id=user_id).update({'avatar_url':file_name})
        db.session.commit()
    except Exception as e :
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg='保存头像信息失败')

    # 返回值
    print(file_name)
    avatar_url = constants.QINIU_URL_DOMAIN + file_name
    return jsonify(errno=RET.OK, errmsg='上传头像成功',data = {'avatar_url':avatar_url})


@api.route("/user/name", methods=["PUT"])
@login_required
def change_user_name():
    """修改用户名"""
    # 接收参数
    req_data = request.get_json()
    name = req_data.get("name")
    print(name)
    # 从g对象中获取用户的user_id
    user_id = g.user_id

    # 校验参数
    if not req_data:
        return jsonify(errno=RET.PARAMERR, errmsg="参数不完整")
    if not name :
        return jsonify(errno=RET.PARAMERR, errmsg="输入不能为空")
    # 业务逻辑处理
    try:
        # User.query.filter_by(id=user_id).update(name=name)
        User.query.filter_by(id=user_id).update({"name":name})
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="设置用户错误")
    # 成功返回应答
    # 重新设置session中的用户名
    session["user_name"] = name
    return jsonify(errno=RET.OK, errmsg="OK", data={"name":name})


@api.route("/user", methods=["GET"])
@login_required
def get_user_profile():
    """获取用户个人的信息"""
    # 获取参数
    user_id = g.user_id
    # 从数据库中查询数据
    try:
        user = User.query.filter_by(id=user_id).first()
    except Exception as e:
        current_app.logger.error(e)
        jsonify(errno=RET.DBERR, errmsg="获取用户实名信息失败")

    if user is None:
        return jsonify(errno=RET.NODATA, errmsg="无效操作")

    return jsonify(errno=RET.OK, errmsg="ok", data=user.to_dict())


@api.route("/user/auth", methods=["GET"])
@login_required
def get_user_auth():
    """获取用户的实名认证信息"""
    user_id = g.user_id

    # 在数据库中查询信息
    try:
        user = User.query.get(user_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="获取用户实名信息失败")

    if user is None:
        return jsonify(errno=RET.NODATA, errmsg="无效操作")

    return jsonify(errno=RET.OK, errmsg="OK", data=user.auth_to_dict())


@api.route("/user/auth", methods=["POST"])
@login_required
def set_user_auth():
    """保存用户实名认证信息"""
    user_id = g.user_id
    # 获取参数
    req_data = request.get_json()
    if not req_data:
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    real_name = req_data.get("real_name")
    id_card = req_data.get("id_card")

    # 校验参数
    if not all([real_name, id_card]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    # 业务逻辑处理
    try:
        User.query.filter_by(id=user_id, real_name=None, id_card=None)\
            .update({"real_name":real_name,"id_card":id_card})
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="保存用户实名信息失败")

    # 返回应答
    return jsonify(errno=RET.OK, errmsg="OK")