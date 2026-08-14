# coding: utf-8
# Author：fengchi863
# Date ：2022/9/28 13:43

"""
要约收购的统计
"""

from xquant.factordata import FactorData
from dataApi import getData, tradeDate, stockList
from sklearn.metrics import confusion_matrix
from sklearn.metrics import accuracy_score, precision_score, recall_score
import pandas as pd
import numpy as np

def forward_fill(arr, axis, zero_fill=True):
    arr = arr.swapaxes(axis, -1)
    if zero_fill:
        mask = arr == 0
    else:
        mask = np.isnan(arr)
    idx = np.where(~mask, np.arange(mask.shape[-1]), 0)
    np.maximum.accumulate(idx, axis=-1, out=idx)

    out = arr[tuple(np.arange(idx.shape[x])[(None,) * x + (slice(None),) + (None,) * (idx.ndim - x - 1)] for x in range(idx.ndim - 1)) + (idx,)]
    out = out.swapaxes(axis, -1)
    return out

def get_lb(zt_flag):
    zt_values_copy = zt_flag.values.copy()
    zt_values2 = zt_values_copy.cumsum(axis=1)
    breaks = zt_values2 * (zt_values_copy == 0)
    zt_values3 = forward_fill(breaks, axis=1)
    zt_values4 = zt_values2 - zt_values3
    return zt_values4

fd = FactorData()
basic_info = fd.get_factor_value('WIND_AShareDescription')
basic_info = basic_info[['S_INFO_WINDCODE', 'S_INFO_NAME', 'S_INFO_COMPCODE']]
offer = fd.get_factor_value('WIND_AshareOfferforoffer')     # 此表实时更新
offer = pd.merge(offer, basic_info, how='inner', on='S_INFO_COMPCODE')
offer = offer.sort_values('OPDATE', ascending=False)
filter_col = ['S_INFO_WINDCODE',
              'S_INFO_NAME',
              'START_DATE',
              'END_DATE',
              'S_PROFITNOTICE_FIRSTANNDATE',
              'S_PROFITNOTICE_DATE',
              'S_RESULT_BULLETIN_DAY',
              'NANN_DATE',
              'OPDATE',  # 最后一次更新的时间
              'PURCHASING_PRICE'
              ]
offer = offer[filter_col]
offer = offer.query('S_PROFITNOTICE_FIRSTANNDATE >= "2010-01-01"')
rename_col = {
              'S_INFO_WINDCODE': '证券代码',
              'S_INFO_NAME': '证券名称',
              'START_DATE': '开始日期',
              'END_DATE': '结束日期',
              'S_PROFITNOTICE_FIRSTANNDATE': '首次公告日',
              'S_PROFITNOTICE_DATE': '要约收购书公告日',
              'S_RESULT_BULLETIN_DAY': '要约收购结果公告日',
              'NANN_DATE': '最新公告日期',
              'OPDATE': '最新更新时间',
              'PURCHASING_PRICE': '流通股每股收购价格'
}
offer = offer.rename(columns=rename_col)
offer['首次公告日'] = offer['首次公告日'].map(int)
offer['证券ID'] = offer['证券代码'].map(stockList.trans_windcode2int)
offer['最近交易日'] = offer['首次公告日'].apply(lambda x: x if x in tradeDate.trade_dates else tradeDate.get_pre_trade_date(x, -1))
offer['流通股每股收购价格'] = offer['流通股每股收购价格'].map(float)
offer = offer[~offer['流通股每股收购价格'].isna()]
offer = offer.reset_index(drop=True)
"""
这里通过观察，首次公告日都是发布公告后的第一个交易日，公告发布日期在前一天下午15:30-21:00不等，所以对跟踪来说，也可能都比较晚才能发给双姐
如哈药股份20190815首次公告日，20190814晚上22:32发布的公告，而且这个没有经过停牌复牌
剔除无偿划转的，无偿划转的没有给出流通股收购价格
"""
#%% 统计发布后当天是否一字板，后面连续几个板，首日涨跌幅
pre_close = getData.get_daily_1factor('pre_close')
pctchg = getData.get_daily_1factor('pct_chg')
close = getData.get_daily_1factor('close')
high = getData.get_daily_1factor('high')
low = getData.get_daily_1factor('low')
limit_max = getData.get_daily_1factor('limit_max', code_list=close.columns.tolist())
zt = close == limit_max
yzb = (high == limit_max) & (low == limit_max)
lb = pd.DataFrame(get_lb(zt.loc[zt.index[::-1]].T).T, index=zt.index[::-1], columns=zt.columns)
yzlb = pd.DataFrame(get_lb(yzb.loc[yzb.index[::-1]].T).T, index=yzb.index[::-1], columns=yzb.columns)

offer['前收价'] = offer[['证券ID', '最近交易日']].apply(lambda x: pre_close.loc[x['最近交易日'], x['证券ID']], axis=1)
offer['当日涨跌幅'] = offer[['证券ID', '最近交易日']].apply(lambda x: pctchg.loc[x['最近交易日'], x['证券ID']], axis=1)
offer['最大连板数'] = offer[['证券ID', '最近交易日']].apply(lambda x: lb.loc[x['最近交易日'], x['证券ID']], axis=1)
offer['最大一字连板数'] = offer[['证券ID', '最近交易日']].apply(lambda x: yzlb.loc[x['最近交易日'], x['证券ID']], axis=1)
offer['当日是否涨停'] = offer[['证券ID', '最近交易日']].apply(lambda x: zt.loc[x['最近交易日'], x['证券ID']], axis=1)
offer['当日是否一字板'] = offer[['证券ID', '最近交易日']].apply(lambda x: yzb.loc[x['最近交易日'], x['证券ID']], axis=1)
offer['收购价是否大于前收价'] = offer['流通股每股收购价格'] > offer['前收价']
offer['收购价相对于前收价涨幅'] = offer['流通股每股收购价格'] / offer['前收价'] - 1
offer['收购涨幅大于0.1'] = offer['收购价相对于前收价涨幅'] > 0.1
offer['收购涨幅大于0.15'] = offer['收购价相对于前收价涨幅'] > 0.15

from dataApi.sendInfo import send_file
send_file(offer)

# label = pd.read_hdf('/data/group/800463/project/project1_prod/generalStrong_v3/Label_zt/Label_zt.h5')
# offer['o2ul'] = offer[['证券代码', '最近交易日']].apply(lambda x: label.loc[(pd.to_datetime(str(x['最近交易日'])), x['证券代码']), 'label_T_o2ul'] if (pd.to_datetime(str(x['最近交易日'])), x['证券代码']) in label.index else np.nan, axis=1)
def print_score(x, y):
    print(confusion_matrix(x, y))
    print(accuracy_score(x, y))
    print(precision_score(x, y))
    print(recall_score(x, y))

print_score(offer['当日是否一字板'], offer['收购价是否大于前收价'])
print_score(offer['当日是否一字板'], offer['收购涨幅大于0.1'])
print_score(offer['当日是否一字板'], offer['收购涨幅大于0.15'])





