from flask_script import Manager
from flask_migrate import MigrateCommand,Migrate
from ihome import create_app,db

app = create_app('develop')
# print(app.url_map)
# 创建程序实例的管理工具对象
manager = Manager(app)

# 创建迁移工具对象
Migrate(app, db)

# 给管理工具对象添加指令
manager.add_command('db', MigrateCommand)


if __name__ == '__main__':
    # print(app.url_map)
    manager.run()