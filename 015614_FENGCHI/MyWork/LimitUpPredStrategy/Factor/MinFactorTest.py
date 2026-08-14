from dataApi.tradeDate import *
from backtest.factor_backtest.TickDataPrepare2 import TickDataPrepare, search_index
from backtest.factor_backtest.StrategyFactorTest2 import StrategyFactorTest2, search_index
from HFfactor.MinFactorLab.RealTime.UsefulList import MaterialList
from HFfactor.MinFactorLab.Research.AnalyseProgram import get_program_factor, analyse_program
from HFfactor.MinFactorLab.RealTime.Operators import *
import pandas as pd
import numpy as np
from tqdm import tqdm
import gc
import re
import warnings
from HFfactor.MinFactorLab.Research.FactorValTick import load_material, SimpleFactorVal

code_list = pd.read_pickle(f'/arch1/group/800442/800319/MinFactor/DateCode/code_list.pkl')

MaterialList = [
    'turn_order_passive_sell',
    'turn_order_active_sell',
    'turn_order_passive_buy',
    'ret_order_passive_sell',
    'ret_order_passive_buy',
    'turn_order_active_buy',
    'ret_order_active_sell',
    'ret_order_active_buy',
    'turn_order_passive',
    'turn_order_active',
    'ret_order_passive',
    'ret_order_active',
    'turn_cancel_sell',
    'turn_trade_sell',
    'ret_cancel_sell',
    'turn_order_sell',
    'turn_cancel_buy',
    'turn_trade_buy',
    'ret_high_close',
    'ret_close_vwap',
    'ret_order_sell',
    'ret_cancel_buy',
    'ret_trade_sell',
    'turn_order_buy',
    'ret_low_close',
    'turn_acc_sell',
    'ret_order_buy',
    'ret_trade_buy',
    'turn_acc_buy',
    'turn_cancel',
    'ret_cancel',
    'turn_total',
    'turn_order',
    'num_total',
    'ret_close',
    'ret_trade',
    'adj_close',
    'ret_order',
    'ret_vwap',
    'pcf_hist',
    'peg_hist',
    'num_sell',
    'ret_high',
    'adj_high',
    'turn_acc',
    'adj_opn',
    'ret_low',
    'adj_low',
    'adj_vol',
    'pe_hist',
    'num_buy',
    'pb_hist',
    'adj_amt',
    'pb_f1',
    'pe_f1',
    'pe_f2'
]

trade_minute = [
    925, 930, 931, 932, 933, 934, 935, 936, 937, 938, 939, 940, 941, 942, 943, 944, 945, 946, 947, 948,
    949, 950, 951, 952, 953, 954, 955, 956, 957, 958, 959, 1000, 1001, 1002, 1003, 1004, 1005, 1006, 1007, 1008,
    1009, 1010, 1011, 1012, 1013, 1014, 1015, 1016, 1017, 1018, 1019, 1020, 1021, 1022, 1023, 1024, 1025, 1026, 1027,
    1028, 1029, 1030, 1031, 1032, 1033, 1034, 1035, 1036, 1037, 1038, 1039, 1040, 1041, 1042, 1043, 1044, 1045, 1046,
    1047, 1048, 1049, 1050, 1051, 1052, 1053, 1054, 1055, 1056, 1057, 1058, 1059, 1100, 1101, 1102, 1103, 1104, 1105,
    1106, 1107, 1108, 1109, 1110, 1111, 1112, 1113, 1114, 1115, 1116, 1117, 1118, 1119, 1120, 1121, 1122, 1123, 1124,
    1125, 1126, 1127, 1128, 1129, 1300, 1301, 1302, 1303, 1304, 1305, 1306, 1307, 1308, 1309, 1310, 1311, 1312, 1313,
    1314, 1315, 1316, 1317, 1318, 1319, 1320, 1321, 1322, 1323, 1324, 1325, 1326, 1327, 1328, 1329, 1330, 1331, 1332,
    1333, 1334, 1335, 1336, 1337, 1338, 1339, 1340, 1341, 1342, 1343, 1344, 1345, 1346, 1347, 1348, 1349, 1350, 1351,
    1352, 1353, 1354, 1355, 1356, 1357, 1358, 1359, 1400, 1401, 1402, 1403, 1404, 1405, 1406, 1407, 1408, 1409, 1410,
    1411, 1412, 1413, 1414, 1415, 1416, 1417, 1418, 1419, 1420, 1421, 1422, 1423, 1424, 1425, 1426, 1427, 1428, 1429,
    1430, 1431, 1432, 1433, 1434, 1435, 1436, 1437, 1438, 1439, 1440, 1441, 1442, 1443, 1444, 1445, 1446, 1447, 1448,
    1449, 1450, 1451, 1452, 1453, 1454, 1455, 1456, 1457, 1458, 1459, 1500
]




def get_idx_list(start_date, end_date, address='/arch1/group/800442/800319/LimitTickData'):

    dp = TickDataPrepare(address=address)
    LimitPool = dp.get_data_by_date_list(item='LimitPool',
                                         start_date=start_date,
                                         end_date=end_date,
                                         date_list=None,
                                         start_tick=91500,
                                         end_tick=150000,
                                         tick_list=None,
                                         return_idx=True
                                         )

    date_list = get_date_range(start_date, end_date)
    code_list = pd.read_pickle(f'/arch1/group/800442/800319/MinFactor/DateCode/code_list.pkl')

    stock_stack = LimitPool[LimitPool].stack().reset_index().rename(columns={'level_2': 'tick'})
    stock_stack = stock_stack[stock_stack['tick'] > 92500]
    stock_stack['time'] = [int(trade_minute[trade_minute.index(x//100)-1]) for x in stock_stack['tick']]
    stock_stack['date_idx'] = [date_list.index(x) for x in stock_stack['date']]
    stock_stack['time_idx'] = [trade_minute.index(x) for x in stock_stack['time']]
    stock_stack['code_idx'] = [code_list.index(x) for x in stock_stack['code']]
    stock_stack = stock_stack.set_index(['date', 'code', 'tick'])

    return stock_stack['date_idx'].tolist(), stock_stack['time_idx'].tolist(), \
           stock_stack['code_idx'].tolist(), stock_stack.index


date_idx, time_idx, code_idx, factor_idx = get_idx_list(20140701, 20191231)


class FactorTest(object):

    def __init__(self, start_date=20140101, backtest_start_date=20140701, end_date=20191231,
                 stock_pool_address='/data/group/800442/800319/LimitUpStrategy/FilteredTick.pkl'):

        date_list = get_date_range(start_date, end_date)
        backtest_date_list = get_date_range(backtest_start_date, end_date)

        start_date = date_list[0]
        end_date = date_list[-1]
        backtest_start_date = backtest_date_list[0]

        stock_pool = pd.read_pickle(stock_pool_address)
        stock_pool.query('date >= @start_date & date <= @end_date', inplace=True)

        self.date_list = date_list
        self.backtest_date_list = backtest_date_list
        self.start_date = start_date
        self.end_date = end_date
        self.backtest_start_date = backtest_start_date
        self.stock_pool = stock_pool
        self.stock_pool_address = stock_pool_address

    def trans_min_to_tick(self, min_factor):

        tick_factor = pd.Series(min_factor[date_idx, time_idx, code_idx], index=factor_idx)

        return tick_factor

    def factor_std(self, factor_s, n=60):

        factor_s = factor_s.reindex(self.stock_pool.set_index(['date', 'code', 'tick']).index)
        # factor_s.index = self.stock_pool.set_index(['date', 'code', 'tick']).index
        factor_s.name = 'value'
        factor_s = factor_s.loc[(factor_s.index.get_level_values('date') >= self.start_date) &
                                (factor_s.index.get_level_values('date') <= self.end_date)]

        null_pct = factor_s.isnull().sum() / len(factor_s)
        inf_pct = (np.isinf(factor_s)).sum() / len(factor_s)
        zero_pct = (factor_s == 0).sum() / len(factor_s)

        factor_s = factor_s.fillna(0)

        num = factor_s.groupby('date').count()
        f1 = factor_s.groupby('date').sum().fillna(0)
        f2 = (factor_s ** 2).groupby('date').sum().fillna(0)

        factor_mean = f1.rolling(n).sum() / num.rolling(n).sum()
        factor_mean.name = 'mean'
        factor_std = np.sqrt(
            (f2.rolling(n).sum() - (num.rolling(n).sum()) * (factor_mean ** 2)) / (num.rolling(n).sum() - 1))
        factor_std.name = 'std'

        factor_mean_tick = pd.merge(factor_s.reset_index(), factor_mean.shift(1).reset_index(), how='left',
                                    on='date')[['date', 'code', 'tick', 'mean']].set_index(['date', 'code', 'tick'])
        factor_std_tick = pd.merge(factor_s.reset_index(), factor_std.shift(1).reset_index(), how='left',
                                   on='date')[['date', 'code', 'tick', 'std']].set_index(['date', 'code', 'tick'])

        factor_std = (factor_s - factor_mean_tick['mean']) / factor_std_tick['std']
        factor_std = factor_std.loc[(factor_std.index.get_level_values('date') >= self.backtest_start_date) &
                                    (factor_std.index.get_level_values('date') <= self.end_date)]

        return factor_std

    def factor_test(self, factor):

        result = pd.Series()
        factor_raw = self.trans_min_to_tick(factor)
        factor_s = factor_raw.loc[(factor_raw.index.get_level_values('date') >= self.backtest_start_date) &
                                  (factor_raw.index.get_level_values('date') <= self.end_date)]
        null_pct = factor_s.isnull().sum() / len(factor_s)
        inf_pct = (np.isinf(factor_s)).sum() / len(factor_s)
        zero_pct = (factor_s == 0).sum() / len(factor_s)

        result.loc['null_pct'] = null_pct
        result.loc['inf_pct'] = inf_pct
        result.loc['zero_pct'] = zero_pct

        # factor_std = self.factor_std(factor_raw)

        if null_pct > 0.2 or inf_pct > 0.2 or zero_pct > 0.4 or null_pct + inf_pct + zero_pct > 0.5:
            print('缺失值/无穷值/0值占比太高')

        else:
            pass

        sft = StrategyFactorTest2(start_date=self.backtest_start_date, end_date=self.end_date,
                                  back_data_address='/arch1/group/800442/800319/LimitTickData/HighFreqData/LimitUpPredPoolWhole.pkl')
        sft.set_stock_pool(start_tick=93000, stock_pool_address=self.stock_pool_address)
        sft.set_test_params(strength_limit=1., close_limit_up=True)
        try:

            ft = sft.test_factor(factor=factor_raw,  # 因子名称, 可以传入str文件名, 也可直接传入DataFrame
                                 address=None,  # 因子路径, 若直接传DataFrame, 此处需为None
                                 groups=10,  # 连续型因子分组收益的分组数, 若因子值为离散值则此传参无意义
                                 output=None  # 回测结果输出路径, None表示不输出
                                 )

            corr = ft[0]
            ret = ft[1]
            tail_amt = ft[2]
            head_amt = ft[3]

            corr_tmr30 = corr['ret_tmr30']
            ret_tmr30 = pd.DataFrame(ret.loc[ret.index, (slice(None), 'ret_tmr30')].values,
                                     index=ret.index,
                                     columns=ret.loc[ret.index, (slice(None), 'ret_tmr30')].columns.levels[0])
            head_ret_tmr30 = ret_tmr30.apply(lambda x: x.tolist()[-2] if x.tolist()[-1] > 0 else x.tolist()[0],
                                             axis=0)

            if (abs(corr_tmr30.loc['ALL']) >= 0.01 and (abs(corr_tmr30) >= 0.01).sum() >= 6 and
                    ((head_ret_tmr30.loc['ALL'] > 0 or (((head_ret_tmr30 > 0).sum() >= 3) and
                                                        ((head_ret_tmr30[4:] > 0).sum() > 0))))):
                result.loc['pass'] = True
            else:
                result.loc['pass'] = False
            corr_tmr30.index = [str(x) + '_IC' for x in corr_tmr30.index]
            head_ret_tmr30.index = [str(x) + '_ret' for x in head_ret_tmr30.index]
            result = pd.concat([result, corr_tmr30, head_ret_tmr30], axis = 0)

        except:
            pass



        return result




self = FactorTest(start_date=20140701,
                  backtest_start_date=20150101, end_date=20191231,
                  stock_pool_address='/data/group/800442/800319/LimitUpStrategy/FirstTick.pkl')

ft = SimpleFactorVal(20140701, 20191231)
factor = ft.factor_val('max2(ts_cumstd(turn_acc), ret_high)')
factor_result = self.factor_test(factor)
