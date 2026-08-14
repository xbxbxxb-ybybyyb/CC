# coding: utf-8
# Author：fengchi863
# Date ：2020/7/15 8:40

root_path = '/data/group/800319/junkData/StrongStock/'
intrafactormodel_root_path = '/data/group/800319/junkData/IntraFactorModel/'

tick_data_path = intrafactormodel_root_path + 'IntradayData/TickData/'
trans_data_path = intrafactormodel_root_path + 'IntradayData/TransData/'

up_out_path = intrafactormodel_root_path + 'DataForTplusN/up_limit/'
down_out_path = intrafactormodel_root_path + 'DataForTplusN/down_limit/'
open_up_down_info_path = '/data/group/800319/junkData/IntraFactorModel/DataForTplusN/open_flatten/'

# factor path
intraday_factor_path = intrafactormodel_root_path + 'FactorByStock_from2017_whole_mkt/'
# intraday_factor_by_date_path = '/data/group/800319/junkData/IntraFactorModel/FactorByDate/'
intraday_factor_by_date_path = root_path + 'factor/intraday_factor/'
fix_factor_path = '/data/user/015518/quant_data/qualified_factor/x_day_lib/20181231/'
fix_factor_by_date_path = root_path + 'factor/fix_factor/'
fix_factor_by_date_h5_path = root_path + 'factor/fix_factor_h5/'
fix_factor_strong_by_date_path = '/data/group/800319/junkData/StrongStock/factor/strong_pool_fix_factor/'
preprocessed_ts_norm_by_factor_path = root_path + 'processed_factor_by_factor/ts_norm/'
preprocessed_ts_maxmin_by_factor_path = root_path + 'processed_factor_by_factor/ts_maxmin/'
preprocessed_ts_pct_by_factor_path = root_path + 'processed_factor_by_factor/ts_pct/'

all_mkt_preprocessed_ts_norm_by_date_path = root_path + 'processed_factor_all_pool_by_date/ts_norm/'
all_mkt_preprocessed_ts_pct_by_date_path = root_path + 'processed_factor_all_pool_by_date/ts_pct/'
all_mkt_preprocessed_ts_maxmin_by_date_path = root_path + 'processed_factor_all_pool_by_date/ts_maxmin/'

preprocessed_strong_by_date_path = root_path + 'factor/strong_pool_fix_factor_preprocessed_ts_norm/'
pool_info_path = intrafactormodel_root_path + 'StrongPoolInfo/FactorBackTestPool/'
interday_factor_path = ''
label_path = root_path + 'labels/'

log_path = root_path + 'Logs/'
hyperopt_log_path = log_path + 'hyperopt_logs/'

ghost_stock_path = '/data/group/800319/Faamonitor/妖股2014-2019.pkl'
strong_stock_path = '/data/group/800319/Faamonitor/强势个股2014-2019.pkl'

predictions_path = root_path + 'predictions/'

# model path
model_path = root_path + 'models/'
cnn_model_path = model_path + 'CNN/'

# factor sorted path
fix_factor_bigdata_evaluation_path = '/data/group/800319/Strong_stock/fix_bigdata_evaluation.pkl'
fix_factor_true_send_evaluation_path = '/data/group/800319/Strong_stock/fix_true_send_evaluation.pkl'
fix_factor_true_send_ic_sort_path = '/data/group/800319/Strong_stock/ic_sort.pkl'

deal_price_path = root_path + 'deal_price/'

factor_eval_res_path = '/data/group/800319/'
