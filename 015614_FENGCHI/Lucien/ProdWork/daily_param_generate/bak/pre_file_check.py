# -*- coding: utf-8 -*-
# @Time    : 2021/5/25 10:07
# @Author  : wangweidi
import os
import pandas
from xquant.factordata import FactorData
s = FactorData()

def pre_check(today):
    yesterday = s.tradingday(today, -2)[0]
    file_list = [#股票池
                 '/data/group/800463/stock_list/white_list/%s.xls' % (today),
                 '/data/group/800463/stock_list/grey_list/grey_list_%s.xlsx' % (today),
                 '/data/group/800463/stock_list/abnormal_notice_list/abnormal_notice_list_%s.xlsx' % (today),
                 '/data/group/800463/stock_list/pre_st_list/pre_st_list_%s.xlsx' % (yesterday),
                 '/data/group/800463/stock_list/after_dt_list/after_dt_list_%s.xlsx' % (yesterday),
                 '/data/group/800463/stock_list/defer_reply_list/defer_reply_list_%s.xlsx' % (yesterday),
                 #pre_close
                 '/data/group/800463/param/pre_close/%s.pkl'%(today),
                 #因子数据
                 '/data/group/800463/param/factor_param/saturn_param_v6_%s.pkl'% (today),
                 '/data/group/800463/param/factor_param/ceres_param_v3_%s.pkl'% (today),
                 '/data/group/800463/param/factor_param/N_all_factor_zt_merge_v2212_%s.pkl'%(today),
                 '/data/group/800463/param/factor_param/prepare_dic_v2212_%s.pkl' % (today),
                 #持仓数据
                 '/data/group/800463/position/综合信息查询_组合证券_537_%s.xls'%(today),
                 '/data/group/800463/position/O45_组合证券_%s.xlsx'%(today)]

    not_ready_list = []
    for file in file_list:
        if not os.path.exists(file):
            not_ready_list.append(file)

    if len(not_ready_list)==0:
        return True, ''
    else:
        return False, not_ready_list
