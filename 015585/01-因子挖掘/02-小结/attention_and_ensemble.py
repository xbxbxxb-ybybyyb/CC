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
    '王敬': '013550',
    '谢璐遥': '013551',
    '冯炽': '015614',
    '孙少森': '018107',
    '徐碧村': '020412',
    '孙康康': '021012',
    '秦雨豪': '015585',
    '张文虎': '022325',
    '唐松乔': '023859',
}

team_addr_dict = {
    '王敬': '/data/user/013550/share/for_qyh/daily_summary/',
    '谢璐遥': '/data/user/013551/share/for-qyh/summary/',
    '冯炽': '/data/user/015614/daily/',
    '孙少森': '/data/user/015614/daily/',
    '徐碧村': '/data/user/015614/daily/',
    '孙康康': '/data/user/015614/daily/',
    '秦雨豪': '/data/user/015614/daily/',
    '张文虎': '/data/user/015614/daily/',
    '唐松乔': '/data/user/015614/daily/',
}

debug_team_no_dict = {'冯炽': '015614'}
# team_no_dict = debug_team_no_dict

path = '/data/user/015614/daily/团队小结/按日/'

team_no_list = list(team_no_dict.values())
team_name_list = list(team_no_dict.keys())

cur_time = datetime.datetime.now().strftime('%H%M%S')
cur_time = int(cur_time)
week_day = datetime.datetime.now().weekday() + 1
today_date = datetime.date.today().strftime('%Y%m%d')

# 为了创建下周二的周小结文件夹
if datetime.date.today().weekday() == 4:    # 如果是周五
    next_meeting_day = datetime.date.today() + datetime.timedelta(days=8 - datetime.date.today().weekday())
    next_meeting_day = int(next_meeting_day.strftime('%Y%m%d'))
    os.makedirs(f'/data/user/015614/daily/团队小结/按周/{next_meeting_day}/', exist_ok=True)

check_time = [193000, 200000, 203000, 210000,
              211000, 212000, 213000, 214000, 215000, 220000,
              220500, 221000, 221500, 222000, 222500, 223000, 223500, 224000, 224500, 225000, 225500, 230000,
]
has_attention_time_dict = dict(zip(check_time, [False] * len(check_time)))

# 交易日17:00定时任务 第一次发送
message = '【日小结提醒】各位同事，请发送今天的日小结~'
os.makedirs(path + f'{today_date}/', exist_ok=True)
send_message(message, users=team_no_list)

while True:
    cur_time = datetime.datetime.now().strftime('%H%M%S')
    cur_time = int(cur_time)

    # 获得目前仍未检查的最近时间
    t_list = list()
    for t in list(has_attention_time_dict.keys()):
        if not has_attention_time_dict[t]:
            t_list.append(t)
    t_list.sort()

    if len(t_list) == 0:
        break

    has_submit_num = 0
    # 对每个人进行单独的处理
    time.sleep(60)
    print(f'当前时间{cur_time}，下一检查时间{t_list[0]}')
    if cur_time > t_list[0]:
        has_attention_time_dict[t_list[0]] = True
        not_submit_no_list = list()
        not_submit_name_list = list()
        for name in team_name_list:
            if os.path.exists(f'{team_addr_dict[name]}团队小结/按日/' + f'{today_date}/{name}.txt'):
                has_submit_num += 1
            else:
                not_submit_no_list.append(team_no_dict[name])
                not_submit_name_list.append(name)

        # 开始个性化提醒
        if len(not_submit_no_list) >= 3:
            send_message('【日小结提醒】请发送今天的日小结，目前还剩3位同事未交~', users=not_submit_no_list)
            if  203000 < cur_time < 210500:
                send_message(f'【日小结提醒】请发送今天的日小结，目前还剩3位同事未交~({",".join(not_submit_name_list)})', users=['015585'])
        if len(not_submit_no_list) == 2:
            send_message('【日小结提醒】请发送今天的日小结，目前还剩2位同事未交！', users=not_submit_no_list)
            if 203000 < cur_time < 210500:
                send_message(f'【日小结提醒】请发送今天的日小结，目前还剩2位同事未交~({",".join(not_submit_name_list)})', users=['015585'])
        if len(not_submit_no_list) == 1:
            send_message('【日小结提醒】请发送今天的日小结，目前还剩1位同事未交，就差你啦', users=not_submit_no_list)
            if 203000 < cur_time < 210500:
                send_message(f'【日小结提醒】请发送今天的日小结，目前还剩1位同事未交~({",".join(not_submit_name_list)})', users=['015585'])

    if has_submit_num == len(team_name_list):
        print(f'{today_date}日小结已收齐')
        break
    if cur_time > t_list[-1]:
        break

# 默认每天检查到晚上23点，大家都已经提交
summary = f'{today_date}日小结汇总：'
for name in team_name_list:
    if os.path.exists(f'{team_addr_dict[name]}团队小结/按日/' + f'{today_date}/{name}.txt'):
        with open(f'{team_addr_dict[name]}团队小结/按日/' + f'{today_date}/{name}.txt', 'r') as file:
            summary += f'\n【{name}】' + file.readline()
send_message(summary, users=['015585'])