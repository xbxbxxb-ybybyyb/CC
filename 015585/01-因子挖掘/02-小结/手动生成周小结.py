# # coding: utf-8
# # Author：fengchi863
# # Date ：2023/2/10 16:51
#
# """
# 进行周小结的收集，从周二上午9:30开始运行
# """
# import sys
# sys.path.append('/data/user/015614/Lucien')
# import pandas as pd
# import datetime
# import os
# team_no_dict = {
#     '王敬': '013550',
#     '谢璐遥': '013551',
#     '孙少森': '018107',
#     '冯炽': '015614',
#     '徐碧村': '020412',
#     '孙康康': '021012',
#     '秦雨豪': '015585'
# }
# team_addr_dict = {
#     '王敬': '/data/user/013550/share/for_qyh/daily_summary/',
#     '谢璐遥': '/data/user/013551/share/for-qyh/summary/',
#     '冯炽': '/data/user/015614/daily/',
#     '孙少森': '/data/user/015614/daily/',
#     '徐碧村': '/data/user/015614/daily/',
#     '孙康康': '/data/user/015614/daily/',
#     '秦雨豪': '/data/user/015614/daily/'
# }
#
# debug_team_no_dict = {'冯炽': '015614'}
# # team_no_dict = debug_team_no_dict
#
# team_no_list = list(team_no_dict.values())
# team_name_list = list(team_no_dict.keys())
#
# cur_time = datetime.datetime.now().strftime('%H%M%S')
# cur_time = int(cur_time)
# week_day = datetime.datetime.now().weekday() + 1
# today_date = datetime.date.today().strftime('%Y%m%d')
# # 默认每天检查到下午15点，大家都已经提交
# summary = pd.DataFrame(index=team_name_list, columns=['工作进展', '工作计划及时间节点'])
# for name in team_name_list:
#     if os.path.exists(f'{team_addr_dict[name]}团队小结/按周/' + f'{today_date}/{name}/summary.txt') and os.path.exists(f'{team_addr_dict[name]}团队小结/按周/' + f'{today_date}/{name}/plan.txt'):
#         with open(f'{team_addr_dict[name]}团队小结/按周/' + f'{today_date}/{name}/summary.txt', 'r') as file:
#             file_lines1 = file.readlines()
#         with open(f'{team_addr_dict[name]}团队小结/按周/' + f'{today_date}/{name}/plan.txt', 'r') as file:
#             file_lines2 = file.readlines()
#         summary.loc[name, '工作进展'] = ''.join(file_lines1)
#         summary.loc[name, '工作计划及时间节点'] = ''.join(file_lines2)
#
# summary.to_excel(f'{team_addr_dict[name]}团队小结/按周/' + f'{today_date}/周小结汇总.xlsx')
#
#
# from tools import send_message
# summary = '20230509日小结汇总：\n【王敬】编写jupiterz策略迭代报告并进行相关数据的统计工作，替换最新因子测试脚本，构思并进行每周因子开发。\n【谢璐遥】针对新版本，修改每日实盘跟踪代码；针对特殊样本集进行因子开发与评估；修改实盘参数代码，针对预热票启动两次\n【冯炽】处理实盘日志重复问题，熟悉日志解析代码；TOrder因子开发；查找成交记录代码BUG\n【孙少森】特殊样本打分和入库；前日是否涨停的修改和检查；不同触发方式延时比较；jupiterZ样本统计。\n【徐碧村】开发新样本集下的因子。每周例会。\n【孙康康】基于快速拉升样本修改之前的因子，开发新的因子；\n【秦雨豪】Europa因子开发；小结程序配置与调试'
# send_message(summary, users=['015585'])
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
    '张文虎': '022325'
}

team_addr_dict = {
    '王敬': '/data/user/013550/share/for_qyh/daily_summary/',
    '谢璐遥': '/data/user/013551/share/for-qyh/summary/',
    '冯炽': '/data/user/015614/daily/',
    '孙少森': '/data/user/015614/daily/',
    '徐碧村': '/data/user/015614/daily/',
    '孙康康': '/data/user/015614/daily/',
    '秦雨豪': '/data/user/015614/daily/',
    '张文虎': '/data/user/015614/daily/'
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

# 默认每天检查到晚上23点，大家都已经提交
summary = f'{today_date}日小结汇总：'
for name in team_name_list:
    if os.path.exists(f'{team_addr_dict[name]}团队小结/按日/' + f'{today_date}/{name}.txt'):
        with open(f'{team_addr_dict[name]}团队小结/按日/' + f'{today_date}/{name}.txt', 'r') as file:
            summary += f'\n【{name}】' + file.readline()
# send_message(summary, users=['015585'])