import redis


class Config(object):
    '''参数配置'''
    SECRET_KEY = 'DLJDSJKAETsaflsahfeio8*(%#$%!@#$%^&*()'
    # 链接数据库的参数信息
    SQLALCHEMY_DATABASE_URI = "mysql://root:mysql@127.0.0.1:3306/ihome"
    # 让sqlalchemy跟踪数据库的改动
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    # 配置redis数据库的参数
    REDIS_PORT = 6379
    REDIS_HOST = '127.0.0.1'

    # flask_session用到的配置信息
    SESSION_TYPE = 'redis'  # 指明 保存到redis中
    SESSION_USE_SIGNER = True  # 使cookie中的session_id被签名加密处理
    SESSION_REDIS = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT)  # 使用redis实例
    PERMANENT_SESSION_LIFETIME = 86400  # 设置session的有效期

                                                    
class DevelopmentConfig(Config):
    '''开发模式使用到的配置信息'''
    DEBUG = True
    # 支付宝参数
    ALIPAY_APPID = "2016091800536588"
    ALIPAY_URL = "https://openapi.alipaydev.com/gateway.do"


class ProductionConfig(Config):
    '''线上模式 使用到的配置信息'''
    pass


config_dict = {
    'develop':DevelopmentConfig,
    'protect':ProductionConfig
}