# @Time : 2021/9/6 14:33
# @Author : Zhichen Lu
# @File : IndustryMatrix.py

import sys; print('Python %s on %s' % (sys.version, sys.platform))
sys.path.append('/data/group/800442/800319')
sys.path.append('/data/user/015614/BWorkHandOver')
sys.path.append('/data/user/015614/BWorkHandOver/ensemblemonitor-strategy-python')
sys.path.append('/data/user/015614/BWorkHandOver/StrongStockModel')

import pandas as pd
from dataApi.getData import get_daily_1factor,trans_windcode2int,trans_int2windcode
from MillenniumFalcon.IndustryMatrixDaily import get_historical_matrix
from dataApi.tradeDate import get_date_range, get_pre_trade_date, get_recent_trade_date
from dataApi.sendInfo import send_message
from dataApi.stockList import get_all_stock_ever_appear,get_stock_list
from ExtraTools import save_nonfix_in_val

sw = get_daily_1factor('SW1')

non_fix_path = '/data/group/800319/strategy_local_path3/'
def out_matrix(today):
    _code_list = get_all_stock_ever_appear(today)
    relation_arr_dict = get_historical_matrix(sw.loc[[today], _code_list], return_type='df')
    relation_df = relation_arr_dict[today]
    relation_df.index = relation_df.index.map(trans_int2windcode)
    relation_df.columns = relation_df.columns.map(trans_int2windcode)
    save_nonfix_in_val({'sw1': relation_df},'matrix',today,non_fix_path=non_fix_path)
    send_message(['015664', '015614'], f'{today} 关系矩阵生成成功 {relation_df.shape}')

def update_restrict_list(date):
    available_pool = pd.read_excel(f'/data/group/800442/800319/strategy_local_path3/restrict_list/证券池{date}.xls')
    black_list = pd.read_excel(f'/data/group/800442/800319/strategy_local_path3/restrict_list/黑名单{date}.xls')
    black_list = black_list[black_list['证券类别'] == '股票']
    available_pool = available_pool[available_pool['交易市场'].isin(['上交所A', '深交所A'])]
    black_list = black_list['证券代码'].astype(int)  # .apply(trans_int2windcode)
    available_pool = available_pool['证券代码'].astype(int)  # .apply(trans_int2windcode)

    all_pool = get_stock_list(date)
    restrict_list = (set(all_pool) - set(available_pool)).union(set(black_list))
    max_day = max(list(extra_restrict_list.keys()))
    restrict_list = restrict_list.union(set(extra_restrict_list[max_day]))
    restrict_list = set(list(map(trans_int2windcode, restrict_list)))
    save_nonfix_in_val(restrict_list,'restrict_list',today, non_fix_path)
    # pd.to_pickle(restrict_list,)
    send_message(['015664', '015614'],f'不可交易名单长度  {len(restrict_list)}')

extra_restrict_list = {
20220223: ['002682.SZ', '603176.SH', '300427.SZ', '300362.SZ', '002432.SZ', '600880.SH', '300437.SZ', '600078.SH',
                                  '603032.SH', '300052.SZ', '301089.SZ', '600112.SH', '300688.SZ', '600145.SH', '000537.SZ', '001317.SZ', '600218.SH',
                                  '600856.SH', '605286.SH', '600306.SH', '601798.SH', '600071.SH', '600995.SH', '300612.SZ', '300412.SZ', '600396.SH',
                                  '000812.SZ', '002750.SZ', '603123.SH', '605333.SH', '603169.SH', '600275.SH', '600698.SH', '601068.SH', '300350.SZ',
                                   '002761.SZ','300649.SZ','603316.SH','600146.SH','601789.SH'],
20220303: ['002682.SZ', '603176.SH', '300427.SZ', '300362.SZ', '002432.SZ', '600880.SH', '300437.SZ', '600078.SH',
          '603032.SH', '300052.SZ', '301089.SZ', '600112.SH', '300688.SZ', '600145.SH', '000537.SZ', '001317.SZ', '600218.SH',
          '600856.SH', '605286.SH', '600306.SH', '601798.SH', '600071.SH', '600995.SH', '300612.SZ', '300412.SZ', '600396.SH',
          '000812.SZ', '002750.SZ', '603123.SH', '605333.SH', '603169.SH', '600275.SH', '600698.SH', '601068.SH', '300350.SZ',
           '002761.SZ','300649.SZ','603316.SH','600146.SH','601789.SH','603122.SH','600078.SH'],
    20220401: ['002682.SZ', '603176.SH', '300427.SZ', '300362.SZ', '002432.SZ', '600880.SH', '300437.SZ', '600078.SH', '603032.SH', '300052.SZ', '301089.SZ',
               '600112.SH', '300688.SZ', '600145.SH', '000537.SZ', '001317.SZ', '600218.SH', '600856.SH', '605286.SH', '600306.SH', '601798.SH', '600071.SH',
               '600995.SH', '300612.SZ', '300412.SZ', '600396.SH', '000812.SZ', '002750.SZ', '603123.SH', '605333.SH', '603169.SH', '600275.SH', '600698.SH',
               '601068.SH', '300350.SZ', '002761.SZ', '300649.SZ', '603316.SH', '600146.SH', '601789.SH', '603122.SH', '600078.SH', '000815.SZ', '600190.SH',
               '600083.SH', '600734.SH', '600090.SH', '600275.SH', '600818.SH', '600056.SH', '603538.SH', '600077.SH', '002613.SZ', '600057.SH'],

}

if __name__ == '__main__':
    print('in')
    today = get_recent_trade_date()
    out_matrix(today)
    # update_restrict_list(today)
    # for date in get_date_range(20211117,20211124):
    #     out_matrix(date)






