# coding: utf-8
# Author：fengchi863
# Date ：2022/8/2 8:40

from dataApi.sendInfo import send_message
import datetime

team_no_dict = {
    '王敬': '013550',
    '谢璐瑶': '013551',
    '冯炽': '015614',
    '徐碧村': '020412',
    '孙少森': '018107',
    '孙康康': '021012'
}

debug_list = ['015614']
team_no_list = list(team_no_dict.values())

week_day = datetime.datetime.now().weekday() + 1

has_send_flag_weekday = False

if not has_send_flag_weekday:
    if week_day == 2:
       message = '【周例会小结提醒】请各位同事发送一下上周工作小结以及下周工作计划~'
       send_message(message, users=team_no_list)
       print(f'已发送：{message}')
    has_send_flag_weekday = True
