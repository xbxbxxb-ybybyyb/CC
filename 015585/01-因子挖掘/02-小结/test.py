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

send_message('123', users=['015585'])