# coding: utf-8
# Author：fengchi863
# Date ：2023/2/9 13:09

"""
进行日小结的收集，从下午17:00开始运行
"""
import sys
sys.path.append('/data/user/015614/Lucien')

from tools import send_message
import datetime
import time
import os

team_no_dict = {
    # '王敬': '013550',
    # '谢璐遥': '013551',
    # '冯炽': '015614',
    # '孙少森': '018107',
    # '徐碧村': '020412',
    # '孙康康': '021012',
    '秦雨豪': '015585',
    # '张文虎': '022325'
}
# 为了创建下周二的周小结文件夹
if datetime.date.today().weekday() == 4:    # 如果是周五
    next_meeting_day = datetime.date.today() + datetime.timedelta(days=8 - datetime.date.today().weekday())
    next_meeting_day = int(next_meeting_day.strftime('%Y%m%d'))
    os.makedirs(f'/data/user/015614/daily/团队小结/按周/{next_meeting_day}/', exist_ok=True)
team_no_list = list(team_no_dict.values())

# 交易日17:00定时任务 第一次发送
message = '【日小结提醒】各位同事，请发送今天的日小结~'
send_message(message, users=team_no_list)