# coding: utf-8
# Author：fengchi863
# Date ：2021/4/8 10:04

from LimitUpPredStrategy.conf.path_conf import bt_output_path
from ShortTermTrading.Util.tools import send_message, send_file

file_path = bt_output_path + 'all_board_bt_result_20210406135851.xlsx'
file_path = "/data/group/800319/Afengchi/LimitUpPredStrategy/backtest_result/dragon_board_bt_result_20210407170946.xlsx"
file_path = '/data/group/800319/Afengchi/LimitUpPredStrategy/backtest_result/20210510牛市测试/virga2consis_board_bt_result_20210510144230.xlsx'
# file_path = 'C:/Users/appadmin/Desktop/123.rar'
send_file(['fengchi'], file_path)
# send_message(['fengchi'], 'http://168.7.21.84/015614/limituppredstrategy')