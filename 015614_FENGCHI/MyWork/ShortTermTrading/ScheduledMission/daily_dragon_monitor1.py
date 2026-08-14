# coding: utf-8
# Author：fengchi863
# Date ：2021/4/13 10:50
from ShortTermTrading.ScheduledMission.daily_dragon_monitor import  DailyDragonMonitor
from ShortTermTrading.conf.path_conf import dragon_monitor_path
from ShortTermTrading.Util.tools import get_yesterday_date

import os, sys
sys.path.append('/data/user/fengchi/MyWork')
sys.path.append('/data/user/fengchi/MyWork/ShortTermTrading')

DEBUG = False

if __name__ == '__main__':
    yes_date = get_yesterday_date()
    if DEBUG:
        yes_date = 20210412
    ddm = DailyDragonMonitor(dragon_monitor_path + '涨停分类%d.xlsx' % yes_date)
    ddm.start_intra1(ddm.duanban_dragon)