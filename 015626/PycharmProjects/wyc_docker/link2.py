import random
import time
import hashlib
from xquant.setXquantEnv import xquantEnv, testEnv
from FactorProvider.conf.DubboConf import get_userid
import requests
import os
import json

if xquantEnv == 0:

    # 新版铃客配置
    corpid = 'ww90dba4dc323845a2'
    corpsecret = 'P9DHuJEBWcWuDRm8Pl9k-RclkMNk955XxzlOc9h__qE'
    agentid = 1000020
    token_url = "http://168.61.113.101:8990/cgi-bin/gettoken?corpid={0}&corpsecret={1}".format(corpid, corpsecret)
    send_url = "http://168.61.113.101:8990/cgi-bin/message/send?access_token={}"

else:

    # 新版铃客配置
    corpid = 'wwd53282142c96185d'
    corpsecret = 'Pk0ewu3nuo6JhEaBj_EkuCyiALj0RuISWuZeJcoPdhI'
    agentid = 1000033
    token_url = " http://168.7.124.15:1080/cgi-bin/gettoken?corpid={0}&corpsecret={1}".format(corpid, corpsecret)
    send_url = " http://168.7.124.15:1080/cgi-bin/message/send?access_token={}"


class LinkMessage:
    user_id = get_userid()
    def __init__(self, user_id = str(user_id)):
        self.user_id = user_id

    def __get_access_token(self):
        con = requests.get(token_url)
        json_text = json.loads(con.text)
        access_token = json_text["access_token"]
        return access_token

    def __sendMessage_new(self, msg):
        if not os.environ.get('ENV_VERSION', False):
            raise Exception("Exception: Spark程序不支持发送铃客消息！")

        access_token = self.__get_access_token()
        post_url = send_url.format(access_token)

        data = {"touser": str(self.user_id),
                "msgtype": "text",
                "agentid": agentid,
                "text": {
                    "content": msg
                }}

        json_data = json.dumps(data)

        res = requests.post(post_url, json_data)
        if res.status_code != 200:
            print("Exception: 新版铃客发送消息失败：消息发送异常！")
        else:
            print("Info: 新版铃客消息发送成功！")

    def sendMessage(self, msg):
        try:
            self.__sendMessage_new(msg)
        except Exception as e:
            print("新版铃客发送消息失败：{}".format(e))

