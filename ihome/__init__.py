from logging.handlers import RotatingFileHandler
from config import config_dict
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import redis as redis
from flask_wtf import CSRFProtect
from flask_session import Session
import logging


# 创建sqlalchemy链接对象
from ihome.utils.commons import RegexConverter
# 创建数据库的链接对象
db = SQLAlchemy()

# 创建redis链接对象
redis_store = None

# 为flask补充csrf防范机制
csrf = CSRFProtect()

# 设置日志的记录等级
logging.basicConfig(level=logging.DEBUG)  # 调试debug级
# 创建日志记录器，指明日志保存的路径、每个日志文件的最大大小、保存的日志文件个数上限
file_log_handler = RotatingFileHandler("logs/log", maxBytes=1024*1024*100, backupCount=10)
# 创建日志记录的格式                 日志等级    输入日志信息的文件名 行数    日志信息
formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
# 为刚创建的日志记录器设置日志记录格式
file_log_handler.setFormatter(formatter)
# 为全局的日志工具对象（flask app使用的）添加日记录器
logging.getLogger().addHandler(file_log_handler)

def create_app(config_name):
    app = Flask(__name__)

    # conf 获取到的是config_name对应的类名
    conf = config_dict[config_name]

    # 从对象中获取参数
    app.config.from_object(conf)

    # 初始化数据库db
    db.init_app(app)

    # 初始化redis
    global redis_store
    redis_store = redis.StrictRedis(port=conf.REDIS_PORT, host=conf.REDIS_HOST)

    # 初始化csrf
    csrf.init_app(app)

    # 将flask中的session信息保存到redis中
    Session(app)

    # 自定义的转换器
    app.url_map.converters['re'] = RegexConverter

    # 延迟导入api
    from ihome import api_1_0
    # 注册蓝图
    app.register_blueprint(api_1_0.api, url_prefix='/api/v1_0')

    from ihome import web_html
    app.register_blueprint(web_html.html)

    return app