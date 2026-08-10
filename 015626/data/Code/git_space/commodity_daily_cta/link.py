from xquant.xqutils.helper import link
from loguru import logger

# list of users receiving the link message
USER_IDS = [
    '012398',
    '015626'
]

class LinkMessage(object):
    """
    LinkMessage responsible for send link message
    """
    def __init__(self, user_ids):
        self.user_ids = user_ids
        self.lm = link.LinkMessage(user_ids)
        self.count_limit = 0
        self.max_limit = 9

    def sendMessage(self, msg):
        try:
            if self.count_limit >= self.max_limit:
                self.lm = link.LinkMessage(self.user_ids)
                self.count_limit = 0
            self.lm.sendMessage(msg)
            self.count_limit += 1
        except Exception as e:
            logger.error("铃客发送消息异常：message={}, error={}".format(msg, e))