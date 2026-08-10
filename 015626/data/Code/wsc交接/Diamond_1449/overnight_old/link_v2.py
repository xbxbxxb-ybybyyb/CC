import json
import os

import requests
from loguru import logger

# 接收信息的用户列表
user_ids = [
#    '012398',
#    '015626',
#    '013547',  # 陈宇轩
    '017024',
#    '015617',  # 孔剑阳
#    '016700',
    # '012872',  # 胡俊鹏
    # '015612',  # 陈俊男
#    '018083',  # 郭晨
#    '012129',  # 汪振
    # '015518',  # 陈家强
    # '018728',  # 王楠
]

# 新版铃客配置
corpid = 'wwd53282142c96185d'
corpsecret = 'Pk0ewu3nuo6JhEaBj_EkuCyiALj0RuISWuZeJcoPdhI'
agentid = 1000033
token_url = " http://168.7.124.15:1080/cgi-bin/gettoken?corpid={0}&corpsecret={1}".format(corpid, corpsecret)
send_url = " http://168.7.124.15:1080/cgi-bin/message/send?access_token={}"


class LinkMessage:
    def __init__(self):
        self.__count_limit_new = 20  # 一次实例化后剩余调用的次数

    @staticmethod
    def __get_access_token():
        con = requests.get(token_url)
        json_text = json.loads(con.text)
        access_token = json_text["access_token"]
        return access_token

    def __sendMessage_new(self, msg):
        if not os.environ.get('ENV_VERSION', False):
            raise Exception("Exception: Spark程序不支持发送铃客消息！")
        access_token = self.__get_access_token()
        post_url = send_url.format(access_token)

        success_user_ids = []

        for user_id in user_ids:
            data = {"touser": user_id,
                    "msgtype": "text",
                    "agentid": agentid,
                    "text": {
                        "content": msg
                    }}
            json_data = json.dumps(data)
            if self.__count_limit_new > 0:
                res = requests.post(post_url, json_data)
                self.__count_limit_new = self.__count_limit_new - 1
                if res.status_code != 200:
                    logger.error("Exception: 铃客发送消息失败：消息发送异常！")
                else:
                    success_user_ids.append(user_id)
            else:
                logger.error("Exception: 铃客发送消息失败：已达到最大发送次数！")
        if len(success_user_ids) != len(user_ids):
            logger.error(
                "铃客漏发消息：expect_user_list={}, actual_user_list={}, msg={}".format(user_ids, success_user_ids, msg))
        else:
            logger.info(
                "铃客成功发送消息：msg={}, users={}".format(msg, success_user_ids))

    def sendMessage(self, msg):
        try:
            self.__sendMessage_new(msg)
        except Exception as e:
            logger.error("铃客发送消息失败：msg={}, e={}".format(msg, e))


if __name__ == "__main__":
    lm = LinkMessage()
    lm.sendMessage("另类策略团队账户：51607留50万，51606留N万，其余请转出")
