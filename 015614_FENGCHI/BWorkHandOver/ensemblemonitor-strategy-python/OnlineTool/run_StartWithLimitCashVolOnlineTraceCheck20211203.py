# @Time : 2020/12/16 21:24
# @Author : Zhichen Lu
# @File : run_StartWithLimitCash.py
import sys, datetime

sys.path.append('/data/user/015664/TriggeredTrading/ensemblemonitor-strategy-python/')
sys.path.append('/data/user/015664/TriggeredTrading/StrongStockModel/')
sys.path.append('/data/user/015664/TriggeredTrading/')
import numpy as np
from StrongStockModel.conf.path_config import deal_price_path
from StrongStockModel.backtest.StrategyBackTest.DerivativeStrategy.StartWithLimitCashVolConsiderChangingCash import StartWithLimitCashVolConsiderChangingCash, \
    InitailCashBasedEvaluationHelper
from StrongStockModel.model.ModelResultLoadingTool import get_signal_by_val_pct_threshold_integration
import pandas as pd
from dataApi.tradeDate import get_date_range, get_pre_trade_date
import configparser, os
from online_conf import code_list_path, local_config_path
from Script.lzc.pitches_integration import model_list, out_signal
from dataApi.getData import trans_windcode2int
from OnlineTool.daily_statOnline import main_compare


def get_signal_by_zscore_integration(path_file_list, threshold=0.05):
    res_list = {}
    for each in path_file_list:
        temp = pd.read_pickle(each)
        res_list[each] = temp['adjusted_prediction']
    res_df = pd.DataFrame(res_list)
    pred_ret = res_df.mean(axis=1)
    pred_ret = pred_ret.reset_index()
    pred_ret = pred_ret.pivot_table(index=[pred_ret.columns[0], pred_ret.columns[1]], columns=pred_ret.columns[2], values=0)
    return pred_ret > threshold, pred_ret


pct_threshold = 0.05
bar_list = [1000, 1030, 1100, 1300, 1330, 1400, 1430]
cost = 0.001

para = {
    'XGB_Cat_Light': [
        '/data/user/015664/AFuckingTrigger/OnlineModel/XGB_d.pkl',
        '/data/user/015664/AFuckingTrigger/OnlineModel/XGB_t.pkl',
        '/data/user/015664/AFuckingTrigger/OnlineModel/XGB_c.pkl',
 '/data/group/800442/800319/wyl/model_record/lightgbmnew_ic_all_t_out_of_sample.pkl',
 '/data/group/800442/800319/wyl/model_record/catboostnew2_ic_all_t_out_sample.pkl'
    ],
    # 'XGB_Light': [
    #     '/data/group/800442/800319/wyl/model_record/lightgbmnew_ic_all_t_out_of_sample.pkl',
    #     '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_c_train200_test10_factor_num400_norm_window_40.pkl',
    #     '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_d_train200_test10_factor_num400_norm_window_40.pkl',
    #     '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_t_train200_test10_factor_num400_norm_window_40.pkl',
    #
    # ]

}

backtest_start_date = 20210406
per_amt_ratio = 0.005

per_ratio_change = {
    20210525: 0.02,
    20210617:0.01,
    20210624:0.005,
    20210727:0.006,
    20210729:0.00167,
    20210730:0.005,
    20210803:0.003125,
    20210804:0.005,
}
pct_threshold_change = {
    20210525: 0.04,20210527:0.05
}

cash_flow = {20210413:28000000,
             20210420:-20000000,
            20210506:20000000,
            20210513:50000000,
             20210525:120000000,
             20210527:-170000000,
            20210603:50000000,
            20210604:70000000,
             20210616:-10000000,
             20210706:60000000,
            20210727:-50000000,
             20210730:-100000000-7925804.88,
             20210802:30000000,
             20210804:-30000000,
             20210817:-30859736.86,
            20210825:20000000,
             20210827:30000000,
            20210928:-36846732.2,
            20210930:36846732.2,
            20211015:-44401839.49,
            20211105:30000000,
            20211111:50000000,
            20211126:-80000000
             }
max_trigger_num = {20210729:28,20210730:100,20210803:28}
tag = 'XGB_Cat_Light'
file_list = para[tag]
print(file_list)
deal_ratio = 0.1
tag = tag + '_OnlineTest'

today = 20211206#int(datetime.date.today().strftime('%Y%m%d'))
pre_date = get_pre_trade_date(today)

cash_flow[get_pre_trade_date(backtest_start_date)] = 2000000
main_compare(today,cash_flow=cash_flow)



