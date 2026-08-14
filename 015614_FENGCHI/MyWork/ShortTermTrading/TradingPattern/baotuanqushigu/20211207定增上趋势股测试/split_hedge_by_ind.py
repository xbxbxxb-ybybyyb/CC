# coding: utf-8
# Author：fengchi863
# Date ：2022/5/19 19:35

from SimiStock.config.path_config import *
from SimiStock.SimiStockGenerator.util import util
from SimiStock.dataApi import indName, getData, tradeDate
import pandas as pd
from tqdm import tqdm
sw1 = getData.get_daily_1factor('SW1', date_list=tradeDate.get_date_range(20210101, 20210930))


def getIndName(stk_id, trade_date):
    return indName.sw_level1[sw1.loc[trade_date, stk_id]]


good_ind = ['银行', '非银金融', '钢铁']
middle_ind = ['公用事业', '家用电器', '建筑装饰', '房地产', '汽车', '商业贸易', '采掘']
bad_ind = ['纺织服装', '综合', '休闲服务', '建筑材料']

top10_ind = good_ind + middle_ind
tail14_ind = list(set(list(indName.sw_level1.values())).difference(set(top10_ind)).difference(set(bad_ind)))

hedge_result11 = '两个版本对比1_7_(0.6, 1)_(0.7, 1)_(120, 120)_95_20210101_20210930_result.pkl'
hedge_result12 = '两个版本对比1_7_(0.5, 1)_(0.5, 1)_(120, 120)_95_20210101_20210930_result.pkl'
hedge_result21 = '两个版本对比2_7_(0.6, 1)_(0.7, 1)_(120, 120)_95_20210101_20210930_result.pkl'
hedge_result22 = '两个版本对比2_7_(0.5, 1)_(0.5, 1)_(120, 120)_95_20210101_20210930_result.pkl'
hedge_result11 = pd.read_pickle(hedge_path + hedge_result11)
hedge_result12 = pd.read_pickle(hedge_path + hedge_result12)
hedge_result21 = pd.read_pickle(hedge_path + hedge_result21)
hedge_result22 = pd.read_pickle(hedge_path + hedge_result22)

"""整体"""
hedge_list = list()
for _hedge in tqdm(hedge_result11):
    _stk_id = _hedge['stk_id']
    _trade_date = _hedge['date']
    sw_name = getIndName(_stk_id, _trade_date)
    if sw_name in tail14_ind:
        hedge_list.append(_hedge)

for _hedge in tqdm(hedge_result12):
    _stk_id = _hedge['stk_id']
    _trade_date = _hedge['date']
    sw_name = getIndName(_stk_id, _trade_date)
    if sw_name in top10_ind:
        hedge_list.append(_hedge)

util.save_list2pkl(hedge_list, hedge_path, '整体_相似度版本对冲池.pkl')

hedge_list = list()
for _hedge in tqdm(hedge_result21):
    _stk_id = _hedge['stk_id']
    _trade_date = _hedge['date']
    sw_name = getIndName(_stk_id, _trade_date)
    if sw_name in tail14_ind:
        hedge_list.append(_hedge)

for _hedge in tqdm(hedge_result22):
    _stk_id = _hedge['stk_id']
    _trade_date = _hedge['date']
    sw_name = getIndName(_stk_id, _trade_date)
    if sw_name in top10_ind:
        hedge_list.append(_hedge)

util.save_list2pkl(hedge_list, hedge_path, '整体_K线版本2对冲池.pkl')

"""分开"""
hedge_list = list()
for _hedge in tqdm(hedge_result11):
    _stk_id = _hedge['stk_id']
    _trade_date = _hedge['date']
    sw_name = getIndName(_stk_id, _trade_date)
    if sw_name in tail14_ind:
        hedge_list.append(_hedge)
util.save_list2pkl(hedge_list, hedge_path, '分开_相似度版本0.6阈值14个行业结果.pkl')

hedge_list = list()
for _hedge in tqdm(hedge_result12):
    _stk_id = _hedge['stk_id']
    _trade_date = _hedge['date']
    sw_name = getIndName(_stk_id, _trade_date)
    if sw_name in top10_ind:
        hedge_list.append(_hedge)
util.save_list2pkl(hedge_list, hedge_path, '分开_相似度版本0.5阈值10个行业结果.pkl')

hedge_list = list()
for _hedge in tqdm(hedge_result21):
    _stk_id = _hedge['stk_id']
    _trade_date = _hedge['date']
    sw_name = getIndName(_stk_id, _trade_date)
    if sw_name in tail14_ind:
        hedge_list.append(_hedge)
util.save_list2pkl(hedge_list, hedge_path, '分开_K线版本2_0.6阈值14个行业结果.pkl')

hedge_list = list()
for _hedge in tqdm(hedge_result22):
    _stk_id = _hedge['stk_id']
    _trade_date = _hedge['date']
    sw_name = getIndName(_stk_id, _trade_date)
    if sw_name in top10_ind:
        hedge_list.append(_hedge)
util.save_list2pkl(hedge_list, hedge_path, '分开__K线版本2_0.5阈值10个行业结果.pkl')

########

hedge_list = list()
for _hedge in tqdm(hedge_result11):
    _stk_id = _hedge['stk_id']
    _trade_date = _hedge['date']
    sw_name = getIndName(_stk_id, _trade_date)
    if sw_name in top10_ind:
        hedge_list.append(_hedge)
util.save_list2pkl(hedge_list, hedge_path, '分开_相似度版本0.6阈值10个行业结果.pkl')

hedge_list = list()
for _hedge in tqdm(hedge_result12):
    _stk_id = _hedge['stk_id']
    _trade_date = _hedge['date']
    sw_name = getIndName(_stk_id, _trade_date)
    if sw_name in tail14_ind:
        hedge_list.append(_hedge)
util.save_list2pkl(hedge_list, hedge_path, '分开_相似度版本0.5阈值14个行业结果.pkl')

hedge_list = list()
for _hedge in tqdm(hedge_result21):
    _stk_id = _hedge['stk_id']
    _trade_date = _hedge['date']
    sw_name = getIndName(_stk_id, _trade_date)
    if sw_name in top10_ind:
        hedge_list.append(_hedge)
util.save_list2pkl(hedge_list, hedge_path, '分开_K线版本2_0.6阈值10个行业结果.pkl')

hedge_list = list()
for _hedge in tqdm(hedge_result22):
    _stk_id = _hedge['stk_id']
    _trade_date = _hedge['date']
    sw_name = getIndName(_stk_id, _trade_date)
    if sw_name in tail14_ind:
        hedge_list.append(_hedge)
util.save_list2pkl(hedge_list, hedge_path, '分开__K线版本2_0.5阈值14个行业结果.pkl')
