# @Time : 2021/4/14 14:19
# @Author : Zhichen Lu
# @File : restrict_list_update.py
import pandas as pd
from dataApi.stockList import get_stock_list
from dataApi.getData import trans_int2windcode
from online_conf import local_config_path
import datetime
import shutil
from xquant.xqutils.helper import link
lm = link.LinkMessage()



def update_restrict_list(date):
    available_pool = pd.read_excel(f'{local_config_path}restrict_list/{date}/自营交易证券池.xls')
    black_list = pd.read_excel(f'{local_config_path}restrict_list/{date}/自营黑名单.xls')
    shutil.copy(f'{local_config_path}restrict_list/{date}/自营交易证券池.xls',f'/data/group/800319/strategy_local_path/restrict_list/证券池{date}.xls')
    shutil.copy(f'{local_config_path}restrict_list/{date}/自营黑名单.xls',f'/data/group/800319/strategy_local_path/restrict_list/黑名单{date}.xls')
    black_list = black_list[black_list['证券类别']=='股票']
    available_pool = available_pool[available_pool['交易市场'].isin(['上交所A', '深交所A'])]

    black_list = black_list['证券代码'].astype(int)#.apply(trans_int2windcode)
    available_pool = available_pool['证券代码'].astype(int)#.apply(trans_int2windcode)

    all_pool = get_stock_list(date)
    restrict_list = (set(all_pool) - set(available_pool)).union(set(black_list))
    restrict_list = set(list(map(trans_int2windcode,restrict_list)))
    lm.sendMessage(f'不可交易名单长度  {len(restrict_list)}')
    pd.to_pickle(restrict_list,f'{local_config_path}restrict_list.pkl')

date = int(datetime.date.today().strftime('%Y%m%d'))
update_restrict_list(date)