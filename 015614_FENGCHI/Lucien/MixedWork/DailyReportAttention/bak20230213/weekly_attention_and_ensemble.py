# coding: utf-8
# Author：fengchi863
# Date ：2023/2/10 16:51

"""
进行周小结的收集，从周二上午9:30开始运行
"""
import sys
sys.path.append('/data/user/015614/Lucien')

from dataApi.sendInfo import send_message
import pandas as pd
import datetime
import time
import os

team_no_dict = {
    '王敬': '013550',
    '谢璐遥': '013551',
    '孙少森': '018107',
    '冯炽': '015614',
    '徐碧村': '020412',
    '孙康康': '021012',
    '秦雨豪': '015585'
}

debug_team_no_dict = {'冯炽': '015614'}
team_no_dict = debug_team_no_dict

path = '/data/user/015614/daily/团队小结/按周/'

team_no_list = list(team_no_dict.values())
team_name_list = list(team_no_dict.keys())

cur_time = datetime.datetime.now().strftime('%H%M%S')
cur_time = int(cur_time)
week_day = datetime.datetime.now().weekday() + 1
today_date = datetime.date.today().strftime('%Y%m%d')

check_time = [93000, 110000,
              133000, 140000, 143000,
              144000, 145000, 150000
]
has_attention_time_dict = dict(zip(check_time, [False] * len(check_time)))

# 周二9:30定时任务 第一次发送
message = '【周小结提醒】各位同事，请发送今天的周小结和周计划~'
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
        for name in team_name_list:
            if os.path.exists(path + f'{today_date}/{name}/'):
                has_submit_num += 1
            else:
                send_message('【周小结提醒】请发送今天的周小结和周计划~', users=[team_no_dict[name]])
    if has_submit_num == len(team_name_list):
        print(f'{today_date}周小结已收齐')
        break
    if cur_time > t_list[-1]:
        break

# 默认每天检查到下午15点，大家都已经提交
summary = pd.DataFrame(index=team_name_list, columns=['工作进展', '工作计划及时间节点'])
for name in team_name_list:
    if os.path.exists(path + f'{today_date}/{name}/summary.txt') and os.path.exists(path + f'{today_date}/{name}/plan.txt'):
        with open(path + f'{today_date}/{name}/summary.txt', 'r') as file:
            file_lines1 = file.readlines()
        with open(path + f'{today_date}/{name}/plan.txt', 'r') as file:
            file_lines2 = file.readlines()
        summary.loc[name, '工作进展'] = ''.join(file_lines1)
        summary.loc[name, '工作计划及时间节点'] = ''.join(file_lines2)

from dataApi.sendInfo import send_file
send_file(summary)


