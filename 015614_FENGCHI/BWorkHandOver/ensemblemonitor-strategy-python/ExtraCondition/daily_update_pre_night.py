# @Time : 2021/5/11 21:38
# @Author : Zhichen Lu
# @File : daily_update_pre_night.py
import sys

sys.path.append('/data/user/015664/TriggeredTrading/ensemblemonitor-strategy-python/')
sys.path.append('/data/user/015664/TriggeredTrading/')
sys.path.append('/data/user/015664/TriggeredTrading/StrongStockModel/')
import pandas as pd
import datetime, os
from StrongStockModel.conf.path_config import deal_price_path
from ExtraTools import get_path_conf
from dataApi.getData import trans_int2windcode
from dataApi.tradeDate import get_pre_trade_date, get_date_range
import shutil, datetime
from dataApi.sendInfo import send_message

# path_conf = get_path_conf('/data/group/800319/strategy_local_path_sim/strategy_local_path3_sim20210513/')
path_conf = get_path_conf('/data/group/800319/strategy_local_path3_ForExtraSim/')
path_for_930, code_list_path, holding_info_path, ratio_path = [path_conf[x] for x in 'path_for_930,code_list_path,holding_info_path,ratio_path'.split(',')]


def get_vol_info(date):
    next_day = get_pre_trade_date(date, -1)
    vol_info = pd.read_pickle(deal_price_path + 'vol_rolling_future_30min_sum_5day_mean.pkl')
    vol_info.columns = vol_info.columns.map(trans_int2windcode)
    if date not in vol_info.index:
        raise Exception(f'Vol info of 930 are not update in date {date}')
    if not os.path.exists(f'{path_for_930}{next_day}/'):
        os.mkdir(f'{path_for_930}{next_day}/')
        os.mkdir(f'{path_for_930}{next_day}/StrategyIn/')
        os.mkdir(f'{path_for_930}{next_day}/StrategyOut/')
    pd.to_pickle(vol_info.loc[(date, 930)].fillna(0), f'{path_for_930}{next_day}/StrategyIn/vol_info{next_day}.pkl')


def calc_two_part_ratio(date):
    holding_7_bar = pd.read_pickle(f'{holding_info_path}{date}.pkl')
    holding_930_bar = pd.read_pickle(f'{path_for_930}{date}/StrategyOut/holding{date}.pkl')
    compare = pd.DataFrame({'bar_930': pd.Series(holding_930_bar), 'bar_7': pd.Series(holding_7_bar)}).fillna(0)
    ratio = (compare.T / compare.sum(axis=1)).T
    if not os.path.exists(ratio_path):
        os.mkdir(ratio_path)
    print(ratio.sort_values('bar_930'))
    pd.to_pickle(ratio.drop('cash'), f'{ratio_path}{date}.pkl')

if __name__=="__main__":
    date =int(datetime.date.today().strftime('%Y%m%d'))
    get_vol_info(date)
    calc_two_part_ratio(date)

    send_message(['015664'], '930成交量及ratio更新完成')

