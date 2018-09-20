# coding=utf-8
from ihome.libs.yuntongxun.CCPRestSDK import REST

# import ConfigParser
# ConfigParser
# 主帐号
accountSid = '8a216da86541f9fd016542c989990098'

# 主帐号Token
accountToken = 'c913dee5b21e43b7b7ee66cfca86743a'

# 应用Id
appId = '8a216da86541f9fd016542c98a01009f'

# 请求地址，格式如下，不需要写http://
serverIP = 'app.cloopen.com'

# 请求端口
serverPort = '8883'

# REST版本号
softVersion = '2013-12-26'

  # 发送模板短信
  # @param to 手机号码
  # @param datas 内容数据 格式为列表 例如：['12','34']，如不需替换请填 ''
  # @param $tempId 模板Id

class CCP(object):
    '''发送短信的工具类，单例模式'''
    def __new__(cls):
        if not hasattr(cls, "instance"):
            # 判断该类中有没有类属性instance
            # 如果没有类属性instance，重写父类的方法，并设置对象属性
            obj = super().__new__(cls)
            # 初始化REST SDK
            obj.rest = REST(serverIP, serverPort, softVersion)
            obj.rest.setAccount(accountSid, accountToken)
            obj.rest.setAppId(appId)

            cls.instance = obj

        return cls.instance


    def send_template_sms(self, to, datas, temp_id):
        try:
            # 调用云通讯的工具rest发送短信
            # sendTemplateSMS(手机号码,内容数据,模板Id)
            result = self.rest.sendTemplateSMS(to, datas, temp_id)

        except Exception as e:
            raise e

        print(result)
        # 返回值
        # {'templateSMS': {'smsMessageSid': '62676c547a194d18b4103b07a69e56e0', 'dateCreated': '20171106182730'},
        # 'statusCode': '000000'}
        status_code = result.get("statusCode")
        if status_code == '000000':
            return 0
        else:
            return -1




if __name__ == '__main__':
    ccp = CCP()