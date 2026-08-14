# coding: utf-8
# Author：fengchi863
# Date ：2021/3/5 15:40

root_path = '/data/group/800319/'
proj_root_path = root_path + 'Afengchi/LimitUpPredStrategy/'
proj_root_path2 = root_path + 'LimitUpStrategy/'

factor_path = root_path + 'ZTfactors/Approved/'
factor_std_path = root_path + 'ZTfactors_std/'
limit_pool_file = root_path + 'LimitTickData2/HighFreqData/LimitPool.npy'

label_path = proj_root_path + 'label/'
samples_path = proj_root_path + 'samples/'
samples_path_20210513 = root_path + 'ZTStrategy/ZTFactorFilter/FactorPool_20210513/'

# 股票池
filterd_tick_pool_file_path = proj_root_path2 + 'FilteredTick.pkl'
strategy_pool_file_path = proj_root_path2 + 'StrategyPool.h5'

## 结果输出位置
pred_output_path = proj_root_path + 'predict_result/'
bt_output_path = proj_root_path + 'backtest_result/'
ensemble_path = proj_root_path + 'ensemble_result/'

### filtered_factor
filtered_factor_file_path = proj_root_path + '因子筛选/filtered_factor.xlsx'
corr_IC_filtered_factor_file_path = proj_root_path2 + 'corr_IC_filtered_factor.xlsx'
factor_evaluation_bt_path = root_path + 'ZTStrategy/ZTFactorFilter/FilterResult/'
factor_evaluation_bt_path_20210513 = root_path + 'ZTStrategy/ZTFactorFilter/FilterResult_20210513/'