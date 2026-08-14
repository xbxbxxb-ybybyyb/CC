import sys
sys.path.append('/data/group/800442/800319/AWorkHandOver/alphaResearch/dataUpdate/')
sys.path.append('/data/group/800442/800319/')

from HFfactor.MinFactorSuper.Utility.LoadBigData import make_label as make_super_label, make_idx
from HFfactor.MinFactorSuper.Utility.Parallel import multidask
from HFfactor.MinFactorSuper.Research.MakeMaterial import MakeMaterial
from HFfactor.MinFactorSuper.Research.MakeLabel import make_label
from HFfactor.MinFactorSuper.Research.MakeStockPool import make_stock_pool
from HFfactor.MinFactorSuper.Research.FactorVal import FactorVal
from dataApi.tradeDate import get_pre_trade_date, get_recent_trade_date, get_date_range
import pandas as pd
import numpy as np
import gc
import os


class WeeklyMaintainM5(object):
    def __init__(self, start_date, end_date, factor_list=None, desample_factor_list=None,
                 stock_pool='stock_pool', fold='FactorData', model_times=47,
                 offline_path='/arch1/group/800442/800319/MinFactorSuper/',
                 online_path='/data/group/800442/800319/strategy_HFfactor/'):
        _stock_pool = np.load(f'{offline_path}/Label/{stock_pool}.npy')
        date_num = _stock_pool.shape[0]
        # start_date = get_pre_trade_date(20140101, -date_num)
        # end_date = get_recent_trade_date(dividing_point=19)
        # mk = MakeMaterial(start_date, end_date, offline_path)
        # del mk
        gc.collect()
        # make_stock_pool(end_date, start_date, offline_path)
        make_label(end_date, start_date, offline_path)
        # make_idx(model_times, stock_pool, fold, offline_path)
        # make_super_label(stock_pool, fold, offline_path)
        self.set_factor_list(factor_list, desample_factor_list, online_path)
        # fv = FactorVal(start_date, end_date, reduce=False, stock_pool=stock_pool,
        #                store=fold, address=offline_path)
        # def _func(sub_list):
        #     for factor_line in sub_list:
        #         fv.factor_store(factor_line)
        # multidask('追加存储1分钟因子', [[_func, (self.factor_list[x::24],)] for x in range(24)])
        # del fv, _func
        # gc.collect()
        fv = FactorVal(start_date, end_date, reduce=True, stock_pool=stock_pool,
                       store=fold, address=offline_path)
        def _func(sub_list):
            for factor_line in sub_list:
                fv.factor_store(factor_line)
        multidask('追加存储5分钟因子', [[_func, (self.desample_factor_list[x::24],)] for x in range(24)])
        del fv, _func
        gc.collect()

    def set_factor_list(self, factor_list=None, desample_factor_list=None,
                        online_path='/data/group/800442/800319/strategy_HFfactor/'):
        # if factor_list == None:
        #     dll = sorted([x for x in os.listdir(
        #         f'{online_path}/subscript_factor_list/') if x.startswith('factor_list')])[-1]
        #     self.factor_list = pd.read_pickle(f'{online_path}/subscript_factor_list/{dll}')
        # else:
        #     self.factor_list = factor_list
        # if desample_factor_list == None:
        #     dll = sorted([x for x in os.listdir(
        #         f'{online_path}/subscript_factor_list/') if x.startswith('desample_factor_list')])[-1]
        #     self.desample_factor_list = pd.read_pickle(f'{online_path}/subscript_factor_list/{dll}')
        # else:
        #     self.desample_factor_list = desample_factor_list
        self.factor_list = []
        self.desample_factor_list = pd.read_pickle('/data/group/800442/800319/strategy_HFfactor3/desample_factor_list.pkl')


for year in [2015, 2017, 2019]:
    if year == 2015:
        start_date = 20140801
    else:
        start_date = year * 10000 + 101
    if year == 2019:
        end_date = 20220322
    else:
        end_date = (year + 1) * 10000 + 1231
    date_list = get_date_range(start_date, end_date)
    start_date, end_date = date_list[0], date_list[-1]
    mk = WeeklyMaintainM5(start_date, end_date)
    del mk
    gc.collect()