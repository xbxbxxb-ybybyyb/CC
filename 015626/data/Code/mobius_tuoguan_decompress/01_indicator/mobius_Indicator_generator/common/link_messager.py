import os
import json
import requests
from xquant.xqutils.helper import link
from loguru import logger

# list of users receiving the link message
USER_IDS = [
    # '012872',  # 胡俊鹏
    # '015612',  # 陈俊男
    # '018083',  # 郭晨
    # '012129',  # 汪振
    # '015518',  # 陈家强
    # '018728',  # 王楠
]

class LinkMessage(object):
    """
    LinkMessage responsible for send link message
    """
    def __init__(self, user_ids=None):
        if user_ids is not None:
            self.user_ids = user_ids
        self.lm = link.LinkMessage(user_ids)
        self.count_limit = 0
        self.max_limit = 9

    def sendMessage(self, msg):
        try:
            if self.count_limit >= self.max_limit:
                self.lm = link.LinkMessage(self.user_ids)
                self.count_limit = 0
            # self.lm.sendMessage(msg)
            print(msg)
            self.count_limit += 1
        except Exception as e:
            logger.error("铃客发送消息异常：message={}, error={}".format(msg, e))



if __name__ == '__main__':
    link_messager = LinkMessage(USER_IDS)
    for i in range(0, 18):
        link_messager.sendMessage("Test link SDK messages, test_no={}".format(i))
