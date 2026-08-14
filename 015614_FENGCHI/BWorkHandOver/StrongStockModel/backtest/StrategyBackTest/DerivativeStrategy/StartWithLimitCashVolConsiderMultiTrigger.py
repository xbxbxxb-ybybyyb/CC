# @Time : 2020/12/25 9:05
# @Author : Zhichen Lu
# @File : StartWithLimitCashVolConsiderMultiTrigger.py

import sys
sys.path.extend(['/data/user/015614/MyWork', '/data/user/015614/MyWork/StrongStockModel', '/data/user/015614/MyWork/StrongStockModel/System', '/data/user/015614/MyWork/LimitUpPredStrategy', '/data/user/015614/MyWork/FaaMonitor', '/data/user/015614/MyWork/R2D2', '/data/user/015614/MyWork/CrossFT', '/data/user/015614/MyWork/CrossFT/basic', '/data/user/015614/MyWork/ShortTermTrading/TradingPattern/baotuanqushigu/20211207定增上趋势股测试', '/data/user/015614/MyWork/ShortTermTrading/TradingPattern/baotuanqushigu/20211214测试趋势股卖出条件', '/data/user/015614/MyWork/SimiStock', '/data/user/015614/MyWork/GitProject/Factor', '/data/user/015614/MyWork/GitProject', '/data/user/015614/MyWork/GitProject/Riskfolio-Lib', '/data/user/015614/MyWork/GitProject/Riskfolio-Lib/riskfolio', '/data/user/015614/MyWork/SimiStock/dataApi', '/data/user/015614/MyWork/ensemblemonitor-strategy-python', '/data/user/015614/MyWork/MillenniumFalcon', '/data/user/015614/MyWork'])
from backtest.StrategyBackTest.PortfolioStrategyBase import PortfolioStrategyBase, InitailCashBasedEvaluationHelper
from tqdm import tqdm
import gc
import pandas as pd
import numpy as np
from StrongStockModel.conf.path_config import deal_price_path, root_path
from dataApi.getData import get_daily_1factor

class StartWithLimitCashVolConsiderMultiTrigger(PortfolioStrategyBase):
    def __init__(self, signal, start=20140101, end=20181231, stock_pool=None, target_point=None,
                 buy_cost=0.001, sell_cost=0.001, per_amt_ratio=0.0025, append_param={}, initial_cash=200000000, barly_max_buy=100, deal_percent=0.1,stk_min_amt=None):
        per_amt = round(initial_cash * per_amt_ratio, -5)
        super().__init__(start, end, stock_pool, target_point, buy_cost, sell_cost, per_amt, append_param=append_param)
        self.daily_high = get_daily_1factor('high', self.date_list, self.stk_list)
        self.daily_low = get_daily_1factor('low', self.date_list, self.stk_list)
        self.signal = signal.reindex(self.close.index)
        self.data_flow['signal'] = None
        self.last_buy_time = {}
        self.cash = initial_cash
        self.accout_value = initial_cash
        self.per_amt_ratio = per_amt_ratio
        self.barly_max_buy = barly_max_buy
        self.cash_series = pd.Series(np.nan, index=self.date_list)
        self.holding_value = pd.Series(np.nan, index=self.date_list)
        # self.vol_cumsum = pd.read_pickle(deal_price_path + 'vol_rolling_30_sum.pkl').reindex(self.close.index)
        self.past_5day_future_30min_vol = pd.read_pickle(deal_price_path + 'vol_rolling_future_30min_sum_5day_mean.pkl').reindex(self.close.index)
        self.past_5day_future_30min_vol.columns = [int(str(x)[:6]) for x in self.past_5day_future_30min_vol.columns]
        self.future_30_min_vol = pd.read_pickle(deal_price_path+'vol_future_rolling_30_sum.pkl').reindex(self.close.index)
        self.daily_info['pre_close'] = self.daily_info['close'] * self.daily_info['close_badj'].shift(1) / self.daily_info['close_badj']
        self.deal_percent = deal_percent
        self.buy_time_list = {}
        self.vol_percent_list = {}
        self.holding_num=pd.Series(index=self.date_list)
        self.holding_info = {}
        if stk_min_amt is None:
            self.stk_min_amt = self.per_amt * 0.2
        else:
            self.stk_min_amt = stk_min_amt
        print('deal_percent',self.deal_percent)

    def buy(self, stk, vol=None, amt=None):
        if not self.isinpool(stk):
            """
            不在股票池内时不可买
            """
            return 0, np.nan
        if stk in self.holding:
            holding = self.holding[stk]
        else:
            holding = 0

        if stk in self.available:
            available = self.available[stk]
        else:
            available = 0
        deal_price = self.trade(stk)  # self.bar_dealprice[stk]
        if deal_price == 0 or np.isnan(deal_price):
            return 0, np.nan
        if vol is None and amt is None:
            vol = round(self.per_amt / deal_price, -2)
        elif vol is None:
            vol = round(amt / deal_price, -2)
        elif amt is None:
            pass
        else:
            raise Exception('One of amt and vol must be not None')
        if np.isnan(vol) or vol == 0:
            return 0, deal_price

        vol = min(vol,int(self.bar_actual_future_vol[stk]//100*100))
        holding += vol
        self.holding[stk], self.available[stk] = holding, available
        if stk not in self.record:
            self.record[stk] = [[self.datetime[0], self.datetime[1], 'B', vol, deal_price, holding, available]]
        else:
            record = self.record[stk]
            record.append([self.datetime[0], self.datetime[1], 'B', vol, deal_price, holding, available])
            self.record[stk] = record
        return vol, deal_price

    def sell(self, stk, vol=None):
        available = self.available[stk]
        holding = self.holding[stk]
        if vol is None:
            vol = available
        else:
            vol = min(vol, available)
        if vol == 0 or np.isnan(vol):
            return 0, np.nan
        deal_price = self.trade(stk)
        if deal_price == 0 or np.isnan(deal_price):
            return 0, np.nan
        vol = min(vol, int(self.bar_actual_future_vol[stk] // 100 * 100))
        holding -= vol
        available -= vol
        if holding > 0:
            self.holding[stk] = holding
        else:
            del self.holding[stk]
        if available > 0:
            self.available[stk] = available
        else:
            del self.available[stk]
        if stk not in self.record:
            raise Exception('Sell without record')
        else:
            record = self.record[stk]
            record.append([self.datetime[0], self.datetime[1], 'S', -vol, deal_price, holding, available])
            self.record[stk] = record
        return vol, deal_price

    def sell_action(self, stk, target_vol=None):
        if target_vol==0:
            return
        buy_time_list = self.buy_time_list[stk]
        holding = self.holding[stk]
        target_list = []
        bar_date, bar_time, bar_date_idx, bar_time_idx = self.datetime
        for date, time_point, date_idx, time_idx in buy_time_list:
            if (bar_date_idx - date_idx) > 1 or ((bar_date_idx - date_idx) == 1 and bar_time >= time_point):
                target_list.append((date, time_point, date_idx, time_idx))
            else:
                break
        if not target_list:
            return
        vol_percent_list = self.vol_percent_list[stk]
        vol_list = [x*holding for x in vol_percent_list]
        soldable_vol = sum(vol_list[:len(target_list)])
        entrust_vol = min(target_vol,soldable_vol)
        vol,deal_price = self.sell(stk,entrust_vol)
        if vol==0:
            return
        self.cash+=vol*deal_price*(1-self.sell_cost)
        if stk not in self.holding:
            del self.buy_time_list[stk]
            del self.vol_percent_list[stk]
            return
        elif self.holding[stk]<1e-4:
            del self.holding[stk]
            del self.available[stk]
            del self.buy_time_list[stk]
            del self.vol_percent_list[stk]
            return
        else:
            pass
        left_vol = np.nan
        #三种情况：1)在第n个vol 上刚好卖完 2)第个上没有卖完 3)全部卖完
        for i,temp_vol in enumerate(vol_list):
            if vol>=temp_vol:
                vol-=temp_vol
            else:
                left_vol = temp_vol - vol
                vol = 0
                break
            if vol<1e-4:
                break
        if i >= len(target_list):
            raise Exception('Unexpected situation')
        if np.isnan(left_vol):
            self.buy_time_list[stk] = buy_time_list[i+1:]
            vol_percent_list = vol_percent_list[i+1:]
            vol_percent_list = [x/sum(vol_percent_list) for x in vol_percent_list]
            self.vol_percent_list[stk] = vol_percent_list
        else:
            self.buy_time_list[stk] = buy_time_list[i:]
            vol_list = vol_list[i:]
            vol_list[0] = left_vol
            self.vol_percent_list[stk] = [x/sum(vol_list) for x in vol_list]
            if abs(sum(vol_list)-self.holding[stk])>1e-4:
                raise Exception('Unexpected situation')

    def buy_action(self, stk, vol=None):
        deal_vol, deal_price = self.buy(stk, vol)
        if deal_vol > 0:
            if not np.isnan(deal_price):
                self.last_buy_time[stk] = self.datetime
                self.cash -= deal_vol * deal_price * (1 + self.buy_cost)
                if stk not in self.buy_time_list:
                    self.buy_time_list[stk] = [self.datetime]
                    self.vol_percent_list[stk] = [1]
                else:
                    self.buy_time_list[stk].append(self.datetime)
                    vol_percent_list = self.vol_percent_list[stk]
                    deal_vol_percent = deal_vol/self.holding[stk]
                    vol_percent_list = [x*(1-deal_vol_percent) for x in vol_percent_list] + [deal_vol_percent]
                    self.vol_percent_list[stk] = vol_percent_list
            else:
                raise Exception('Unexpected')
        return deal_vol

    def holding_another_round(self, stk):
        bar_date, bar_time, bar_date_idx, bar_time_idx = self.datetime
        buy_time_list = self.buy_time_list[stk]
        date, time_point, date_idx, time_idx = buy_time_list[0]
        if (bar_date_idx - date_idx) == 1 and bar_time == time_point:
            self.last_buy_time[stk] = buy_time_list[1:] + [self.datetime]
            vol_percent_list = self.vol_percent_list[stk]
            vol_percent_list = vol_percent_list[1:] + vol_percent_list[:1]
            self.vol_percent_list[stk] = vol_percent_list

    def daily_update(self, idx, date):
        super().daily_update(idx, date)
        self.data_flow['signal'] = self.signal[self.date_idx * self.step:(self.date_idx + 1) * self.step]
        self.data_flow['past_future_vol'] = self.past_5day_future_30min_vol[self.date_idx * self.step:(self.date_idx + 1) * self.step]
        self.data_flow['actual_future_vol'] = self.future_30_min_vol[self.date_idx * self.step:(self.date_idx + 1) * self.step]
        date_pool = self.stock_pool[self.date_idx:self.date_idx + 1].T[date]
        date_pool = date_pool[date_pool==False]

        not_tradable = self.untradable_pool[self.date_idx:self.date_idx + 1].T[self.date]

        self.data_flow['not_tradable'] = set(not_tradable[not_tradable].index.tolist())
        self.data_flow['not_available'] = set(date_pool.index.tolist())
        self.data_flow['daily_high'] = self.daily_high[self.date_idx:self.date_idx + 1].T[self.date]
        self.data_flow['daily_low'] = self.daily_low[self.date_idx:self.date_idx + 1].T[self.date]
        self.data_flow['pre_close'] = self.daily_info['pre_close'][self.date_idx:self.date_idx + 1].T[self.date]

        if self.data_flow['signal'].index[0][0] != self.date or self.data_flow['signal'].index[-1][0] != self.date:
            raise Exception('Broadcast date and signal date are not match!')

    def bar_handler(self):
        # date, time_point, date_idx, time_idx = self.datetime
        # signal = self.data_flow['signal'][time_idx:time_idx + 1].T[(date, time_point)]
        # signal = signal.dropna()
        # trigger_stk = set(signal.index)
        # avaliable_stk = set(self.available.keys()) - self.data_flow['not_available']
        # avaliable_trigger_stk = avaliable_stk.intersection(trigger_stk)
        # sell_stk = list(avaliable_stk - trigger_stk)
        # trigger_stk = list(trigger_stk - self.data_flow['not_available'])
        # historical_future_vol = round(self.data_flow['past_future_vol'][time_idx:time_idx + 1].T[(date, time_point)] * self.deal_percent, -2)
        date, time_point, date_idx, time_idx = self.datetime
        signal = self.data_flow['signal'][time_idx:time_idx + 1].T[(date, time_point)]
        signal = signal.dropna()
        trigger_stk = set(signal.index)
        # 盘中涨跌停
        bar_close = self.data_flow['close'][time_idx:time_idx + 1].T[(date, time_point)]
        # 可卖出股票 = 持仓股票剔除 停牌and一字板
        avaliable_stk = set(self.available.keys())
        #############
        available_close = bar_close[list(avaliable_stk)]
        limit_down_judge = ((available_close.values / self.data_flow['pre_close'][list(avaliable_stk)].values - 1) <= -0.098) & (
                available_close.values == self.data_flow['daily_low'][list(avaliable_stk)].values)
        limit_down_judge = pd.Series(limit_down_judge, index=list(avaliable_stk))
        limit_up_judge = ((available_close.values / self.data_flow['pre_close'][list(avaliable_stk)].values - 1) >= 0.098) & (
                available_close.values == self.data_flow['daily_high'][list(avaliable_stk)].values)
        limit_up_judge = pd.Series(limit_up_judge, index=list(avaliable_stk))
        avaliable_stk = set(limit_down_judge[~(limit_down_judge | limit_up_judge)].index.tolist())
        ##########
        avaliable_stk = avaliable_stk - self.data_flow['not_tradable']
        avaliable_trigger_stk = avaliable_stk.intersection(trigger_stk)
        sell_stk = list(avaliable_stk - trigger_stk)
        # 可买入股票 = 触发股票 剔除 不在股票池的股票 以及 有持仓个股
        trigger_stk = list(trigger_stk - self.data_flow['not_available'] ) # print({str(x).zfill(6)+'.SZ' if x <400000 else str(x)+'.SH' for x in trigger_stk})
        # trigger_stk = list(trigger_stk - set(self.holding.keys()))
        historical_future_vol = round(self.data_flow['past_future_vol'][time_idx:time_idx + 1].T[(date, time_point)] * self.deal_percent, -2)

        for stk in avaliable_trigger_stk:
            self.holding_another_round(stk)

        if self.cash < self.per_amt:
            not_buy = True
            for stk in sell_stk:
                try:
                    soldable_vol = min(historical_future_vol[stk], self.holding[stk])
                except:
                    raise Exception('')
                self.sell_action(stk, soldable_vol)
            return
        elif trigger_stk:
            not_buy = False
            target_close = bar_close[trigger_stk]
            limit_up_judge = ((target_close.values / self.data_flow['pre_close'][trigger_stk].values - 1) >= 0.098) & (
                        target_close.values == self.data_flow['daily_high'][trigger_stk].values)
            limit_up_judge = pd.Series(limit_up_judge, index=trigger_stk)
            trigger_stk = limit_up_judge[~limit_up_judge].index.tolist()
            target_vol = round(self.per_amt / target_close, -2)
            target_vol = pd.concat([target_vol, historical_future_vol[list(trigger_stk)]], axis=1).min(axis=1)
            target_vol = target_vol // 100 * 100
            target_amt = target_vol * target_close
            target_amt = target_amt.loc[signal[trigger_stk].sort_values(ascending=False).index.tolist()]
            target_amt = target_amt[target_amt >=  self.stk_min_amt]
            target_amt = target_amt[target_amt.cumsum() < self.cash]
            trigger_stk = target_amt.index.tolist()
            trigger_num = min(len(trigger_stk), int(self.cash // self.per_amt), self.barly_max_buy)
            # except:
            #     raise Exception('')
            trigger_stk = trigger_stk[:trigger_num]
            target_vol = target_vol[trigger_stk]
        else:
            target_vol = pd.Series()

        for stk in sell_stk:
            soldable_vol = min(historical_future_vol[stk], self.holding[stk])
            self.sell_action(stk, soldable_vol)

        for stk in target_vol.index:
            _ = self.buy_action(stk, target_vol[stk])

    def run_backtest(self, kernel=10):
        self.re_initial()
        bar = tqdm(self.date_list)
        for date_idx, date in enumerate(bar):
            bar.set_description('%d | holding:%d' % (date, len(self.holding)))
            self.daily_update(date_idx, date)
            for time_idx, time_point in enumerate(self.trading_point):
                self.bar_dealprice = self.data_flow['deal_price'][time_idx:time_idx + 1].T[(date, time_point)]
                self.bar_actual_future_vol = self.data_flow['actual_future_vol'][time_idx:time_idx + 1].T[(date, time_point)]*self.deal_percent
                self.datetime = (date, time_point, date_idx, time_idx)
                self.bar_point = date_idx * self.step + time_idx
                self.bar_handler()
                # print(self.datetime)
            self.cash_series[self.date] = self.cash
            daily_close = self.daily_info['close'][self.date_idx:self.date_idx + 1].T[self.date][list(self.holding.keys())]
            self.accout_value = (daily_close * pd.Series(self.holding)).sum() + self.cash
            self.holding_value[self.date] = self.accout_value
            self.per_amt = round(self.accout_value * self.per_amt_ratio, -5)
            self.holding_info[date] = pd.Series(self.holding)
            self.holding_num[date] = len(self.holding)

        pre_close_padj, pre_close, pre_adj_ratio = self.daily_info['close_padj'][self.date_idx:self.date_idx + 1].T[date], \
                                                   self.daily_info['close'][self.date_idx:self.date_idx + 1].T[date], \
                                                   self.daily_info['adj_ratio'][self.date_idx:self.date_idx + 1].T[date]
        for stk in self.holding:
            holding = self.holding[stk]
            stk_close_padj, stk_close, stk_adj_ratio = pre_close_padj[stk], pre_close[stk], pre_adj_ratio[stk]
            available = self.available[stk] if stk in self.available else 0
            if holding > 0:
                record = self.record[stk]
                record.append([self.date, 1500, 'H', stk_close_padj, stk_close, holding, available])
                self.record[stk] = record

        record = list(self.record.keys())
        for each in record:
            self.record[each] = pd.DataFrame(self.record[each], columns=['date', 'time', 'flag', 'vol', 'deal_price', 'holding', 'available']).set_index(['date', 'time'])
        gc.collect()
        return self.record._getvalue()



import os
para = {    'XGB_lightGBM_CatBoost':[
'/data/group/800319/wyl/model_record/catboostnew2_ic_all_t.pkl',
 '/data/group/800319/wyl/model_record/lightgbmnew_ic_all_t.pkl',
'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_c_train200_test10_factor_num400_norm_window_40.pkl',
'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_d_train200_test10_factor_num400_norm_window_40.pkl',
'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_t_train200_test10_factor_num400_norm_window_40.pkl',
    ],}

pct_threshold = 0.05
bar_list = [1000, 1030, 1100, 1300, 1330, 1400, 1430]
cost = 0.001
initial_cash = 2e8
per_amt_ratio = 0.005
tag = 'XGB_lightGBM_CatBoost'
# file_list = para[tag]
deal_ratio = 0.1

if os.path.exists('/data/user/015664/AFuckingTrigger/限制买入和持仓/信号存储/signal_%s_%.2f.pkl' % (tag, pct_threshold)):
    print(pct_threshold, 'signal exist')
    signal, pred_ret = pd.read_pickle('/data/user/015664/AFuckingTrigger/限制买入和持仓/信号存储/signal_%s_%.2f.pkl' % (tag, pct_threshold))
else:
    raise Exception('Wrong')

# pred_ret = pd.read_pickle('/data/group/800319/信号存储/20200111LinearCompareMV.pkl')
tag = tag+'MultiTrigger_deal_ratio_%.1f_per_ratio_%.4f_threshold_%.2f_inital_%d'%(deal_ratio,per_amt_ratio,pct_threshold,int(initial_cash))
pred_ret[~signal.fillna(False)] = np.nan

alpha_pool = pd.read_pickle('/data/group/800319/信号存储/daily_stock_score_v3_20210127.pkl').shift(1).loc[20160101:20181231].rank(ascending=False,axis=1)<600
# alpha_pool = pd.read_pickle('/data/group/800319/信号存储/daily_stock_score_v3Trigger_20210127.pkl').shift(1).loc[20160101:20181231]
original_pool = pd.read_pickle('/data/group/800319/junkData/StrongStock/stock_pool_without_limit_up_down.pkl').shift(1).loc[20160101:20181231]
original_pool = original_pool.drop(alpha_pool.index,axis=0)
alpha_pool = pd.concat([original_pool,alpha_pool]).sort_index()>0.5
tag = tag.replace('MultiTrigger','MultiTriggerAlphaPoolV3Top600')
if True:#not os.path.exists('/data/user/015664/AFuckingTrigger/限制买入和持仓/OnlineEraMultiTrigger/reocrd/record_%sVolConsiderMultiTrigger_UpBuy100_%dbp_cost.pkl' % (tag, int(10000 * cost))):
    instance = StartWithLimitCashVolConsiderMultiTrigger(pred_ret, 20160104, 20181231,target_point=bar_list,buy_cost=cost, sell_cost=cost,
                                             per_amt_ratio=per_amt_ratio,append_param={'deal_price_path':deal_price_path+'deal_price_vwap_30min_FullSample.pkl'},
                                             deal_percent=deal_ratio)
    record = instance.run_backtest()
    cash_series = instance.cash_series
    holding_num = instance.holding_num

    pd.to_pickle([record,cash_series,holding_num,instance.holding_info],
             '/data/user/015664/AFuckingTrigger/限制买入和持仓/OnlineEraMultiTrigger/reocrd/record_%sVolConsiderMultiTrigger_UpBuy100_%dbp_cost.pkl' % (tag, int(10000 * cost)))
else:
    record, cash_series, holding_num, holding_info = pd.read_pickle('/data/user/015664/AFuckingTrigger/限制买入和持仓/OnlineEraMultiTrigger/reocrd/record_%sVolConsiderMultiTrigger_UpBuy100_%dbp_cost.pkl' % (tag, int(10000 * cost)))
helper = InitailCashBasedEvaluationHelper(sell_cost_ratio=cost,buy_cost_ratio=cost)
cash_series.index = cash_series.index.astype(int).astype(str)
out_path = '/data/user/015664/AFuckingTrigger/限制买入和持仓/OnlineEraMultiTrigger/%sVolConsiderMultiTrigger_UpBuy100_%dbp_cost.xlsx' % (tag, int(10000 * cost))
helper.one_wave_run(record,cash_series,48,output_path=out_path ,signal_record_save=True,holding_num=holding_num)

print(out_path)


from dataApi.getData import get_daily_1factor

close = get_daily_1factor('close', date_list=sorted(list(holding_info.keys())))

amt = {}
stat = {}
for date in holding_info:
    holding = holding_info[date]
    temp_close = close.loc[date,list(holding.keys())]
    amt[date] = temp_close*holding
    amt[date] = amt[date]/amt[date].sum()
    temp_stat={'%d_percentile'%x:amt[date].quantile(x*0.01) for x in [10,30,50,70,90] }
    temp_stat.update({'max':amt[date].max(),'min':amt[date].min(),'mean':amt[date].mean(),'std':amt[date].std()})
    stat[date] = temp_stat
    print(date)

pd.DataFrame(stat).T.to_excel('/data/user/015664/AFuckingTrigger/限制买入和持仓/OnlineEraMultiTrigger/%s_stat.xlsx'%tag)