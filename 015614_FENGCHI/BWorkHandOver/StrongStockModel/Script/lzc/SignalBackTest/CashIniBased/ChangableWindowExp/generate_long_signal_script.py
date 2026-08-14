# @Time : 2022/1/20 15:37
# @Author : Zhichen Lu
# @File : generate_signal.py
import pandas as pd
from StrongStockModel.model.ModelResultLoadingTool import get_signal_by_val_pct_threshold_long_integration
from dataApi.tradeDate import get_pre_trade_date
import os
import numpy as np
import itertools

param_map = {
    'XGBWithSWSHIFReSaveTWithOrigin_Cat_Light': [
        '/data/group/800442/800319/wyl/model_record/catboostnew2_ic_all_t/',
        '/data/group/800442/800319/wyl/model_record/lightgbmnew_ic_all_t/',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCrossSWMeanOnlyShiftReSave20211122/XGBV4FactorListMixCrossSWMeanOnlyShiftReSave20211122_ic_d_train200_test10_factor_num400/',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCrossSWMeanOnlyShiftReSave20211122/XGBV4FactorListMixCrossSWMeanOnlyShiftReSave20211122_ic_t_train200_test10_factor_num400/',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCrossSWMeanOnlyShiftReSave20211122/XGBV4FactorListMixCrossSWMeanOnlyShiftReSave20211122_ic_c_train200_test10_factor_num400/',

        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_d_train200_test10_factor_num400/',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_t_train200_test10_factor_num400/',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_c_train200_test10_factor_num400/',
    ],
}

out_path = '/data/user/015664/AFuckingTrigger/限制买入和持仓/信号存储/long_nonfix_window/'
if not os.path.exists(out_path):
    os.makedirs(out_path)

for tag in param_map:
    threshold_tag = 'actual_label'
    params = dict(
    pct = 0.05,
    signal_file_name_list =  param_map[tag],
    subset_path_list = [x[:-1]+'_val_pred/' for x in param_map[tag]],
    start = 20170101,
    end = 20210531,
        threshold_tag=threshold_tag
    )
    out_file = f'{out_path}/signal_long_{tag}_pct_{params["pct"]}.pkl'
    if os.path.exists(out_file):
        print(out_file,'exist')
        continue
    res = get_signal_by_val_pct_threshold_long_integration(**params)
    print(tag)
    pd.to_pickle(res,out_file)


def eval_pool(ret,stock_pool):
    pool_ret = ret[stock_pool]
    pool_ret.index = pd.MultiIndex.from_tuples([(x[0] // 10000,) + x for x in pool_ret.index.tolist()])
    pool_ret_series = pool_ret.stack()
    yearly = pool_ret_series.groupby(level=0).mean()
    yearly_pointly = pool_ret_series.groupby(level=[0, 2]).mean().unstack()
    return yearly,yearly_pointly


pool_new = pd.read_pickle('/data/group/800442/800319/AlphaPool/FixEndV2.pkl')
pool_old = pd.read_pickle('/data/group/800442/800319/AlphaPool/CS_XGB|OLS_condition_style_rank_ex20_F600T488P1_future925t241h123d_uniform20t50.pkl')
pool2_arr = np.repeat(pool_old.shift(1).values[:, None, :], 7, 1).reshape(pool_old.shape[0] * 7, pool_old.shape[1])
index = pd.MultiIndex.from_tuples(list(itertools.product(pool_old.index.tolist(), pool_new.index.levels[1].tolist())))
pool2_fix = pd.DataFrame(pool2_arr, index=index, columns=pool_old.columns)


signal,_,_,future = pd.read_pickle('/data/user/015664/AFuckingTrigger/限制买入和持仓/信号存储/long_nonfix_window//signal_long_XGBWithSWSHIFReSaveTWithOrigin_Cat_Light_pct_0.05.pkl')
pool_new = pool_new.reindex(future.columns, axis=1).loc[20170101:20210531].rank(axis=1, ascending=False) < 600
pool2_fix = pool2_fix.reindex(future.columns, axis=1).loc[20170101:20210531].rank(axis=1, ascending=False) < 600
signal = signal.fillna(False)
yearly_new_signal,yearly_point_new_signal = eval_pool(future[signal], pool_new)
yearly_old_signal,yearly_point_old_signal = eval_pool(future[signal],pool2_fix)
yearly_new,yearly_point_new = eval_pool(future, pool_new)
yearly_old,yearly_point_old = eval_pool(future,pool2_fix)



year = pd.DataFrame({'日频股票池':yearly_old,'日内股票池':yearly_new,
                     '日频股票池信号':yearly_old_signal,'日内股票池信号':yearly_new_signal})
year_point = pd.DataFrame({'日频股票池':yearly_point_old.stack(),'日内股票池':yearly_point_new.stack(),
                     '日频股票池信号':yearly_point_old_signal.stack(),'日内股票池信号':yearly_point_new_signal.stack()})

out_path = './日内股票池收益及信号收益.xlsx'
with pd.ExcelWriter(out_path) as writer:
    year.to_excel(writer,sheet_name='逐年')
    year_point.to_excel(writer,sheet_name='逐时点')

    writer.close()
from dataApi.sendInfo import send_file
send_file(['015664'],out_path)
