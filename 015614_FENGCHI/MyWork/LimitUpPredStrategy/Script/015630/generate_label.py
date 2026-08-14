# coding: utf-8
# Author：fengchi863
# Date ：2021/3/19 10:39

from LimitUpPredStrategy.conf.path_conf import label_path, filterd_tick_pool_file_path
from backtest.factor_backtest.TickDataPrepare2 import TickDataPrepare
from LimitUpPredStrategy.dataApi import getData, tradeDate
import pandas as pd


def calc_and_save_label(label_type='cls_当日收盘是否涨停'):
    tdp = TickDataPrepare()
    limit_pool = tdp.get_data_by_date_list(item='LimitPool',
                                           start_date=20140101,
                                           end_date=20210228,
                                           # date_list=None,
                                           tick_list=None,  # 若传列表则忽略start_tick和end_tick参数
                                           return_idx=True  # True返回DataFrame, False返回2darray
                                           )

    limit_pool_res = limit_pool[limit_pool].stack()

    # 剔除ST\一字板\新股等样本
    filterd_tick_pool = pd.read_pickle(filterd_tick_pool_file_path)
    limit_pool_res = limit_pool_res.reindex(index=filterd_tick_pool.index)
    limit_pool_res.index.names = ['date', 'stk_id', 'time']

    date_list = tradeDate.get_date_range(20131220, 20210331)

    if label_type == 'cls_当日收盘是否涨停':
        # 第一种标签，当天收盘是否涨停，分类
        limit_up = getData.get_daily_1factor('limit_up', date_list=date_list)

        limit_pool_unstack = limit_pool_res.reset_index()
        res1 = limit_pool_unstack.drop_duplicates(['date', 'stk_id'], keep='first')
        res = res1.pivot('date', 'stk_id', 'time')
        res1 = limit_up.reindex_like(res)[res.notnull()]
        res1 = res1.stack().reset_index()
        res1 = res1.rename(columns={0: 'label'})
        limit_pool_unstack = pd.merge(limit_pool_unstack, res1, on=['date', 'stk_id'], how='left').ffill()

        label = limit_pool_unstack.set_index(['date', 'stk_id', 'time']).drop(0, axis=1)
        label = label.astype(int)

    elif label_type == 'reg_次日开盘溢价':
        limit_max = getData.get_daily_1factor('limit_max', date_list=date_list)
        adj_factor = getData.get_daily_1factor('adjfactor', date_list=date_list)
        limit_max_badj = limit_max * adj_factor
        limit_max_badj = limit_max_badj.apply(lambda x: round(x, 2))
        daily_open_badj = getData.get_daily_1factor('open_badj', date_list=date_list)
        next_day_ret = daily_open_badj.shift(-1) / limit_max_badj - 1

        limit_pool_unstack = limit_pool_res.reset_index()
        res1 = limit_pool_unstack.drop_duplicates(['date', 'stk_id'], keep='first')
        res = res1.pivot('date', 'stk_id', 'time')
        res1 = next_day_ret.reindex_like(res)[res.notnull()]
        res1 = res1.stack().reset_index()
        res1 = res1.rename(columns={0: 'label'})
        limit_pool_unstack = pd.merge(limit_pool_unstack, res1, on=['date', 'stk_id'], how='left').ffill()

        label = limit_pool_unstack.set_index(['date', 'stk_id', 'time']).drop(0, axis=1)

    # 保存
    label.to_pickle(label_path + '%s.pkl' % label_type)

if __name__ == '__main__':
    calc_and_save_label()
    # calc_and_save_label(label_type='reg_次日开盘溢价')