# @Time : 2021/3/18 17:11
# @Author : Zhichen Lu
# @File : deal_stat.py
# from online_conf import local_config_path,holding_info_path,daily_out_path
import pandas as pd
import os
from dataApi.getData import trans_int2windcode
from dataApi.tradeDate import get_pre_trade_date
from ExtraTools import get_nonfix_in_val
import datetime



# local_config_path,daily_out_path,holding_info_path,buy_time_info_path,init_conf_path,sub_output_path,path_for_930,ratio_path =\
#     [path_conf[x] for x in 'local_config_path,daily_out_path,holding_info_path,buy_time_info_path,init_conf_path,sub_output_path,path_for_930,ratio_path'.split(',')]
#
# date = 20220322
# pre_date = get_pre_trade_date(date)
# path = f'{local_config_path}transfer_file/{date}/'

    # pd.to_pickle(holding_df,f'{daily_out_path}{date}/last_bar_holding.pkl')