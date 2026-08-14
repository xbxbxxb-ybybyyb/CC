# @Time : 2021/5/11 21:38
# @Author : Zhichen Lu
# @File : daily_update_pre_night.py
import sys; print('Python %s on %s' % (sys.version, sys.platform))
sys.path.append('/data/group/800442/800319')
sys.path.append('/data/user/015614/BWorkHandOver')
sys.path.append('/data/user/015614/BWorkHandOver/ensemblemonitor-strategy-python')
sys.path.append('/data/user/015614/BWorkHandOver/StrongStockModel')

import pandas as pd
import datetime, os
from StrongStockModel.conf.path_config import deal_price_path
# from ExtraTools import get_path_conf
from dataApi.getData import trans_int2windcode
from dataApi.tradeDate import get_pre_trade_date, get_date_range
import shutil, datetime
from dataApi.sendInfo import send_message
from ExtraTools import get_nonfix_in_val,save_nonfix_in_val



non_fix_path = '/data/group/800319/strategy_local_path3/'
non_fix_930_path = f'{non_fix_path}FolderFor930/'
non_fix_in_path = f'{non_fix_path}daily_input/'
non_fix_output_path = f'{non_fix_path}daily_output/'
non_fix_model_path = f'{non_fix_path}model/'
non_fix_model_conf_path = f'{non_fix_path}model_conf/'
non_fix_factor_list = f'{non_fix_path}factor_list/'
non_fix_using_fix_list_path = f'{non_fix_path}using_fix_list/'
non_fix_using_5min_list_path = f'{non_fix_path}using_5min_list/'

# path_conf = get_path_conf('/data/group/800319/strategy_local_path_sim/strategy_local_path3_sim20210513/')
# path_conf = get_path_conf('/data/group/800319/strategy_local_path3/')
# path_for_930, code_list_path, holding_info_path, ratio_path = [path_conf[x] for x in 'path_for_930,code_list_path,holding_info_path,ratio_path'.split(',')]


def get_vol_info(date):
    next_day = get_pre_trade_date(date, -1)
    vol_info = pd.read_pickle(deal_price_path + 'vol_rolling_future_30min_sum_5day_mean.pkl')
    vol_info.columns = vol_info.columns.map(trans_int2windcode)
    if date not in vol_info.index:
        raise Exception(f'Vol info of 930 are not update in date {date}')
    if not os.path.exists(f'{non_fix_930_path}{next_day}/'):
        os.mkdir(f'{non_fix_930_path}{next_day}/')
        os.mkdir(f'{non_fix_930_path}{next_day}/StrategyIn/')
        os.mkdir(f'{non_fix_930_path}{next_day}/StrategyOut/')
    pd.to_pickle(vol_info.loc[(date, 930)].fillna(0), f'{non_fix_930_path}{next_day}/StrategyIn/vol_info{next_day}.pkl')


def calc_two_part_ratio(date):
    holding_7_bar = get_nonfix_in_val('holding_info',get_pre_trade_date(date,-1),non_fix_path)#pd.read_pickle(f'{holding_info_path}{date}.pkl')
    holding_930_bar = pd.read_pickle(f'{non_fix_930_path}{date}/StrategyOut/holding{date}.pkl')
    compare = pd.DataFrame({'bar_930': pd.Series(holding_930_bar), 'bar_7': pd.Series(holding_7_bar)}).fillna(0)
    ratio = (compare.T / compare.sum(axis=1)).T
    save_nonfix_in_val(ratio.drop('cash'),'ratio',date,non_fix_path)
if __name__=="__main__":
    from dataApi.tradeDate import get_recent_trade_date
    date =get_recent_trade_date()#int(datetime.date.today().strftime('%Y%m%d'))
    print(date)
    get_vol_info(date)
    calc_two_part_ratio(date)

    send_message(['015664', '015614'], f'{date}  930成交量及ratio更新完成')

