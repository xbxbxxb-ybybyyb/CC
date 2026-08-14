# coding: utf-8
# Author：fengchi863
# Date ：2022/7/26 17:51

from dataApi.sendInfo import send_message
import datetime
import time

team_no_dict = {
    '王敬': '013550',
    '谢璐瑶': '013551',
    '冯炽': '015614',
    '徐碧村': '020412',
    '孙少森': '018107',
    '孙康康': '021012',
    '秦宇豪': '015585'
}

debug_list = ['015614']

team_no_list = list(team_no_dict.values())

cur_time = datetime.datetime.now().strftime('%H%M%S')
cur_time = int(cur_time)
week_day = datetime.datetime.now().weekday() + 1

has_send_flag_17 = False
has_send_flag_19 = False
has_send_flag_weekday = False

print(cur_time)

while cur_time < 193000:
    print(cur_time)
    if cur_time >= 170000:
        if not has_send_flag_17:
            message = '【日小结提醒】各位同事，请发送今天的日小结~'
            send_message(message, users=team_no_list)
            print(','.join(team_no_list))
            print(f'已发送：{message}')
            #            if week_day == 5:
            #                message = '【周小结提醒】今天周五，同时也要发一下周小结呦'
            #                send_message(message, users=team_no_list)
            #                print(f'已发送{message}')
            has_send_flag_17 = True

    if cur_time > 192500:
        if not has_send_flag_19:
            message = '【日小结二次提醒】饭后了，请各位同事尽快发送今天的日小结哈~（如已发送请忽略）'
            send_message(message, users=team_no_list)
            print(','.join(team_no_list))
            print(f'已发送：{message}')
            #            if week_day == 5:
            #                message = '【周小结二次提醒】周小结也请大家今晚下班前尽快发送（如已发送请忽略）'
            #                send_message(message, users=team_no_list)
            #                print(f'已发送{message}')
            has_send_flag_19 = True

    time.sleep(60)
    cur_time = datetime.datetime.now().strftime('%H%M%S')
    cur_time = int(cur_time)