# @Time : 2020/8/31 15:04
# @Author : Zhichen Lu
# @File : StockStrategyBySignalMultyTrigger.py

import sys
import os
sys.path.append('/data/user/015664/TriggeredTrading/StrongStockModel/')
sys.path.append('/data/user/015664/TriggeredTrading/')
from backtest.StrategyBackTest.StockStrategyBase import StockStrategyBase
import pandas as pd
import time
from backtest.StrategyBackTest.UniverseEvaluation import UniverseEvaluation
from dataApi import tradeDate, stockList, dividend, indName, getData
from StrongStockModel.conf.path_config import root_path
from multiprocessing import Manager
import itertools
from StrongStockModel.model.ModelResultLoadingTool import get_signal_by_val_pct_threshold

class StockStrategyBySignalMultyTrigger(StockStrategyBase):

    def __init__(self, stk, start_date, end_date, price_rolling_window=10, amt_per_signal=5000000, available_flag=None,
                 isin_pool_flag=None):
        super().__init__(stk, start_date, end_date, price_rolling_window, amt_per_signal, available_flag,
                         isin_pool_flag)
        if stk in signal_global:
            self.signal = pd.DataFrame(signal_global[stk])
        else:
            self.signal = None
            self.market_flow = None
        self.stock = stk
        target_index = pd.MultiIndex.from_tuples(list(itertools.product(self.date_list, [1000, 1030, 1100, 1300, 1330, 1400, 1430])))
        self.signal = self.signal.reindex(target_index)
        self.buy_datetime_list = []
        self.vol_percentage_list = []
        self.over_24h = False

    def daily_update(self):
        # 每天基类会更新行情数据，此函数用于每天额外更新策略中需要使用的数据，如没有额外需要使用的数据，可不定义该函数
        # 每天额外更新数据
        if self.trading_day in self.signal.index:
            self.dataflow['signal'] = self.signal[self.i * 7:self.i * 7 + 7]
        else:
            self.dataflow['signal'] = None

    def bar_handler(self):
        # 每只股票每分钟信号逻辑定义
        if self.datetime==(20141216,1000):
            print(1)
        if self.dataflow['signal'] is None:
            return
        # self.datetime (20170103,930)
        if not self.datetime in self.dataflow['signal'].index:
            return

        signal = self.dataflow['signal'].at[self.datetime, self.stk_id]
        if signal == 1 and self.position['available'] == 0 and self.datetime[0]<self.date_list[-5]:
            # 买入函数可输入具体买入手数，该参数默认为 None, 如不输入，则默认买入self.amt_per_signal/均价 （四舍五入到手）
            buy_vol = self.buy()
            self.buy_datetime_list.append(self.datetime + (self.i,))
            buy_vol_to_holding_percentage = buy_vol/self.position['holding']
            rest_percentage = 1- buy_vol_to_holding_percentage
            self.vol_percentage_list = [x*rest_percentage for x in self.vol_percentage_list] + [buy_vol_to_holding_percentage]
            if abs(sum(self.vol_percentage_list)-1)>1e-6:
                raise Exception('sum of vol_percentage_list does not equl to 1 but %f'%sum(self.vol_percentage_list))
            elif sum(self.vol_percentage_list)!=1:
                self.vol_percentage_list = [x/sum(self.vol_percentage_list) for x in self.vol_percentage_list]
        if signal != 1 and self.position['available'] > 0:
            # 卖出函数可输入具体卖出手数，该参数默认为None, 如不输入，则默认卖出所有持仓
            if not self.buy_datetime_list:
                raise Exception('Wrong situation')

            head_date,head_time,head_idx = self.buy_datetime_list[0]
            holding_days = self.i - head_idx
            head_vol = self.vol_percentage_list[0]*self.position['holding']
            while holding_days > 1 or (holding_days == 1 and head_time <= self.datetime[1]):
                sold_vol = self.sell(head_vol)
                if sold_vol==head_vol:
                    self.vol_percentage_list = self.vol_percentage_list[1:]
                    self.buy_datetime_list = self.buy_datetime_list[1:]
                    if len(self.buy_datetime_list)>0 and len(self.vol_percentage_list)>0:
                        continue_flag = True
                    else:
                        return
                elif sold_vol<head_vol:
                    head_unfinished_percentage = 1-sold_vol/head_vol
                    self.vol_percentage_list[0] = self.vol_percentage_list[0]*head_unfinished_percentage
                    continue_flag = False
                else:
                    raise Exception('Sold volume is bigger than target')
                left_percentage = sum(self.vol_percentage_list)
                self.vol_percentage_list = [x/left_percentage for x in self.vol_percentage_list]
                if continue_flag:
                    head_date, head_time, head_idx = self.buy_datetime_list[0]
                    holding_days = self.i - head_idx
                    head_vol = self.vol_percentage_list[0] * self.position['holding']
                    continue
                else:
                    return

start = 20160101#20190101
end = 20181231


"""
def main_beta():
    
    示例2：一波全回测评估并输出
    :return:
    
#    strong_stock = pd.read_pickle('/data/group/800319/Faamonitor/强势个股2014-2019.pkl')
#    strong_stock.index = strong_stock.index.map(lambda x: int(x))
#    strong_stock.columns = strong_stock.columns.map(lambda x: stockList.trans_windcode2int(x))
#    strong_stock = (strong_stock.shift(1).fillna(0)).astype(bool)

#    is_valid = strong_stock

    stock_pool = clean_stock_list(stock_list='ALL', no_ST=True, least_live_days=240,
                                  no_pause=True, least_recover_days=1,
                                  no_pause_limit=0.5, no_pause_stats_days=120,
                                  no_limit_up=False, no_limit_down=False,
                                  other_limit=None, start_date=start, end_date=end)

    stk_list = list(signal.keys())

    strats = UniverseEvaluation(StockStrategyBySignalMultyTrigger, available_info=None, universe_info=stock_pool, buy_cost_ratio=cost, sell_cost_ratio=cost)
    # strats.backtest_one_stock(2989, 20130101, 20191231)
    e = time.time()
    # 并行回测
    file_name = '_'.join(signal_file[:-4].replace('all_mkt_', '').replace('all_mkt', '').split('/')[-3:][::-1]).strip('_')+'_beta'
    print(file_name)
    base_path = root_path + 'backtest_result_all_mkt_%dbp_cost_revised_framework20201013/'%int(cost*10000)
    if not os.path.exists(base_path):
        os.mkdir(base_path)
    # output_path = root_path + base_path+'%s_%.2f.xlsx' % (file_name,th)
    output_path = base_path+'%s_%d_pct_val_threshold.xlsx' % (file_name,int(pct_threshold*100))
    strats.one_wave_run(stk_list, start, end, kernel=24, output_path=output_path, mode='multi',signal_record_save=True)
    # pd.to_pickle(strats.record._getvalue(), '/data/group/800319/Faamonitor/factors/record_zxf_code_excute_by_lzc.pkl')
    # strats.one_wave_run(stk_list, 20100101, 20200728, kernel=10, output_path='/data/group/800319/Faamonitor/kdj_result_multi.xlsx', mode='multi')
    print('strategy time:', time.time() - e)
    print(output_path)

"""

def main_sesitive():
    """
    示例2：一波全回测评估并输出
    :return:
    """
#    strong_stock = pd.read_pickle('/data/group/800319/Faamonitor/强势个股2014-2019.pkl')
#    strong_stock.index = strong_stock.index.map(lambda x: int(x))
#    strong_stock.columns = strong_stock.columns.map(lambda x: stockList.trans_windcode2int(x))
#    strong_stock = (strong_stock.shift(1).fillna(0)).astype(bool)

#    is_valid = strong_stock

    # stock_pool = clean_stock_list(stock_list='ALL', no_ST=True, least_live_days=240,
    #                               no_pause=True, least_recover_days=1,
    #                               no_pause_limit=0.5, no_pause_stats_days=120,
    #                               no_limit_up=False, no_limit_down=False,
    #                               other_limit=None, start_date=start, end_date=end)
    stock_pool = pd.read_pickle(root_path+ 'stock_pool_without_limit_up_down.pkl')
    stk_list = list(signal.keys())

    strats = UniverseEvaluation(StockStrategyBySignalMultyTrigger, available_info=None, universe_info=stock_pool, buy_cost_ratio=cost, sell_cost_ratio=cost)
    # strats.backtest_one_stock(2989, 20130101, 20191231)
    e = time.time()
    # 并行回测
    file_name = 'XGB_T'
    # base_path = root_path + 'backtest_result_all_mkt_%dbp_cost_revised_framework20201013/'%int(cost*10000)
    base_path = '/data/user/015664/AFuckingTrigger/不限制买入卖出信号(老版本)/'
    if not os.path.exists(base_path):
        os.mkdir(base_path)
    # output_path = root_path + base_path+'%s_%.2f.xlsx' % (file_name,th)
    output_path = base_path+'%s_%d_pct_threshold.xlsx' % (file_name,int(pct_threshold*100))
    strats.one_wave_run(stk_list, start, end, kernel=24, output_path=output_path, mode='multi',signal_record_save=True)
    # pd.to_pickle(strats.record._getvalue(), '/data/group/800319/Faamonitor/factors/record_zxf_code_excute_by_lzc.pkl')
    # strats.one_wave_run(stk_list, 20100101, 20200728, kernel=10, output_path='/data/group/800319/Faamonitor/kdj_result_multi.xlsx', mode='multi')
    print('strategy time:', time.time() - e)
    print(output_path)


if __name__ == "__main__":
    pct_threshold = 0.05
    cost = 0.001
    bar_list = [1000,1030,1100,1300,1330,1400,1430]
    signal_file = '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEval/XGBFactorEval_ic_all_t_train200_test10_factor_num400_norm_window_40.pkl'
    # signal, pred_ret = pd.read_pickle( '/data/user/015664/AFuckingTrigger/限制买入和持仓/信号存储/signal_XGB_T.pkl')
    # signal, pred_ret = pd.read_pickle('/data/user/015664/AFuckingTrigger/saved_signal/XGB5min30BarFactorEval_ICT_signal_%d_threshold.pkl' % (int(pct_threshold * 100)))
    signal,pred_ret = get_signal_by_val_pct_threshold(pct_threshold, signal_file.replace('.pkl','_val_pred/'), signal_file, loading_type='old', bar_list=bar_list, val_tag=0)
    signal_dict = dict(signal*1)
    signal_global = Manager().dict(signal)
    main_sesitive()
    #
    # stat = {}
    # for th in [0.75,0.8,0.85,0.9,0.95]:
    #     signal = get_signal(th, signal_file.replace('.pkl', '_val_pred/'), signal_file)
    #     signal = signal.eq(1)
    #     trigger_count_daily = pd.DataFrame((signal.groupby('date').sum()>0).sum(axis=1))
    #     trigger_count_daily['year'] = [x//10000 for x in trigger_count_daily.index]
    #     stat[th] = trigger_count_daily.groupby('year').mean()
    #     print(th)
    #
    # stat = pd.DataFrame({x : stat[x][0] for x in stat})