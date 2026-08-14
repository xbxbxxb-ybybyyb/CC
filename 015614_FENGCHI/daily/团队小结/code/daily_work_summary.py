# coding: utf-8
# Author：fengchi863
# Date ：2023/2/9 11:23

"""
=====日小结=====
日小结提交时间规则：
提交方式：每个工作日17:00收到第一次小结提醒之后开始提交，直接修改today_work_summary运行send_daily_work_summary函数即可。
提醒时间：目前从19:30开始二次提醒，19:30-21:00每半小时提醒一次；21:00-22:00每10分钟提醒一次；22:00-23:00每5分钟提醒一次，23:00后直接汇总当日已提交小结。
上述所有提醒按各位同事提交情况进行后续提醒（即若19:30前提交则不会受到后续任何提醒），若有特殊情况（如请假、病假）提前知会，则会取消当日提醒。

日小结提交格式：
一行无换行，末尾不加标点符号，样例见demo，当日汇总前可重复提交（自动覆盖当日上一次提交内容）

=====周小结=====
周小结提交时间规则：
提交方式：每周周五17：00之后即可提交周小结，填入week_summary.txt以及week_plan.txt保存后（与此代码同目录）运行send_weekly_work_summary函数即可
提醒时间：目前从周例会当天上午9:30进行第一次提醒，11:00进行第二次提醒；下午开始13:00-14:30每半小时提醒一次，14:30-15:00每10分钟提醒一次，15:00后直接汇总当日已提交周小结。
上述所有提醒按各位同事提交情况进行后续提醒（即若11:00前提交则不会受到后续任何提醒），若有特殊情况（如请假、病假）提前知会，则会取消当日提醒。

周小结提交格式：
按原格式提交，可换行，最好无空行，当日汇总前可重复提交（自动覆盖当日上一次提交内容）
"""

import datetime
import os


def send_daily_work_summary(stc:str, owner='冯炽', today_date=None, root_path=None):
    if not today_date:
        raise ValueError('请输入正确的日期！')
    if not root_path:
        raise ValueError('请输入正确的路径，为团队小结文件夹所在目录！')
    path = f'{root_path}/团队小结/按日/'
    os.makedirs(path + f'{today_date}/', exist_ok=True)

    with open(path + f'{today_date}/{owner}.txt', 'w') as file:
        file.write(stc)

    print(f'({owner})小结已提交：{stc}')

def send_weekly_work_summary(owner='冯炽', next_meeting_day=None, root_path=None):
    if not next_meeting_day:
        raise ValueError('请输入正确的周例会日期！')
    if not root_path:
        raise ValueError('请输入正确的路径，为团队小结文件夹所在目录！')
    path = f'{root_path}/团队小结/按周/'
    os.makedirs(path + f'{next_meeting_day}/{owner}/', exist_ok=True)

    if not os.path.exists('week_summary.txt'):
        raise FileNotFoundError('请本地创建week_summary.txt并填写周小结！')
    if not os.path.exists('week_plan.txt'):
        raise FileNotFoundError('请本地创建week_plan.txt并填写周计划！')

    f = open('week_summary.txt')
    buf = f.read()
    f.close()
    f =  open(path + f'{next_meeting_day}/{owner}/summary.txt', 'w')
    f.write(buf)
    f.close()

    f = open('week_plan.txt')
    buf = f.read()
    f.close()
    f = open(path + f'{next_meeting_day}/{owner}/plan.txt', 'w')
    f.write(buf)
    f.close()

    print(f'({owner})小结已提交')


if __name__ == '__main__':
    # TODO: 注意目录，summary_root_path，此目录下会自动生成"团队小结"文件夹
    summary_root_path = '/data/user/015614/daily/'

    today_date = int(datetime.date.today().strftime('%Y%m%d'))
    if datetime.date.today().weekday() == 1:
        next_meeting_day = today_date
    else:
        next_meeting_day = datetime.date.today() + datetime.timedelta(days=8 - datetime.date.today().weekday())
        next_meeting_day = int(next_meeting_day.strftime('%Y%m%d'))

    today_work_summary = '进行JupiterNSell的测试'

    # TODO:注意修改owner为自己的姓名，注意修改next_meeting_day为本次周例会日期，一般为周二
    send_daily_work_summary(today_work_summary, owner='冯炽', today_date=20230210, root_path=summary_root_path)
    # send_weekly_work_summary(owner='冯炽', next_meeting_day=next_meeting_day, root_path=summary_root_path)