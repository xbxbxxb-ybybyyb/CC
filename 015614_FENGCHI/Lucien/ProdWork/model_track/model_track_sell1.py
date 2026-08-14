# coding: utf-8
# Author：fengchi863
# Date ：2023/5/22 14:04

from xquant.factordata import FactorData

s = FactorData()
import matplotlib.pyplot as plt
import xlsxwriter
from ProdWork.model_track.modeltrack_Tool_v2 import *
from ProdWork.model_track.config import *

#################--------Sell1---------#############
version_date_v1 = '2023-05-09'  # 第一个版本上线的时间
str_version_date_v1 = version_date_v1[:4] + version_date_v1[5:7] + version_date_v1[-2:]
local_basic_sell1 = pd.DataFrame()

# 读取全部基础样本
for date in s.tradingday(year_start_date, end_date):
    # by fenc: sell1和sell3样本一样
    this_date_sell1 = pd.read_hdf('/data/group/800463/project/projectS_prod/daily_data/%s_v1/Basic_closed_hf_finish_%s_%s.h5' % (date, date, date))
    local_basic_sell1 = pd.concat([local_basic_sell1, this_date_sell1])

# 读取实盘触发的样本
trigger_samples = pd.DataFrame()
for date in s.tradingday(year_start_date, end_date):
    date_str = date[0:4] + '-' + date[4:6] + '-' + date[6:8]
    this_date_trigger = pd.read_excel('/data/group/800463/日内强势股/log_parse/因子耗时/因子耗时_%s_prod.xlsx' % date_str, sheet_name='Sell1样本', index_col=0)
    this_date_trigger['dt'] = pd.to_datetime(date)
    trigger_samples = pd.concat([trigger_samples, this_date_trigger])
trigger_samples = trigger_samples.sort_values('dt').reset_index().set_index(['dt', 'index'])
trigger_samples.index.names = ['dt', 'Ticker']
# 全部基础样本与实盘触发样本取交集
basic_samples_trigger = local_basic_sell1.loc[trigger_samples.loc[:pd.Timestamp(end_date_lw)].index]

v1_model_name_all = ['totalRegXgbXbcModel',
                     'totalRegXgbSkkModel',
                     'totalRegFSV11XgbSkkModel',
                     'totalRegFSV10LrXbcModel',
                     'pat34RegFSV8LrXlyModel',
                     'totalRegLgbFcModel']
v1_model_name_proba1 = [x.split('Model')[0] + '_proba1' for x in v1_model_name_all]
v1_model_name_pool = v1_model_name_all + ['totalRegXgbWjModel', 'totalRegFSV8XgbSkkModel', 'totalRegFSV10XgbXbcModel', 'totalRegLgbWjModel']
v1_model_pool_proba1 = [x.split('Model')[0] + '_proba1' for x in v1_model_name_pool]
v1_rename_modeldict = dict(zip(v1_model_name_all, ['v1' + x for x in v1_model_name_all]))
v1_rename_probadict = dict(zip(v1_model_name_proba1, ['v1' + x for x in v1_model_name_proba1]))
v1_rename_modelpooldict = dict(zip(v1_model_name_pool, ['v1' + x for x in v1_model_name_pool]))
v1_rename_probapooldict = dict(zip(v1_model_pool_proba1, ['v1' + x for x in v1_model_pool_proba1]))
v1_model_name_all, v1_model_name_proba1 = list(v1_rename_modeldict.values()), list(v1_rename_probadict.values())
v1_model_name_pool, v1_model_pool_proba1 = list(v1_rename_modelpooldict.values()), list(v1_rename_probapooldict.values())

tot_local_prob = pd.DataFrame()
for tradeDatestr in s.tradingday(str_version_date_v1, end_date_lw):
    this_date_tot_prob = pd.DataFrame() # prob和only_prob好像没用，其实只用其中一个就可以
    this_date_local_sample_index = local_basic_sell1[(local_basic_sell1.reset_index()['dt'] == pd.Timestamp(tradeDatestr)).values].index
    if tradeDatestr >= version_date_v1:
        pred_path = '/data/group/800463/wangj/model_signal/Sell1/prod_v1/%s/%s_%s_Sell12_fac_20230330_new_daily_pred.csv' % (tradeDatestr, tradeDatestr, tradeDatestr)
        tmp_day_df = pd.read_csv(pred_path)
        tmp_day_df.rename(columns=v1_rename_modeldict, inplace=True)
        tmp_day_df.rename(columns=v1_rename_probadict, inplace=True)
        tmp_day_df.rename(columns=v1_rename_modelpooldict, inplace=True)
        tmp_day_df.rename(columns=v1_rename_probapooldict, inplace=True)
        tmp_day_df['dt'] = tmp_day_df['dt'].apply(lambda x: pd.Timestamp(x))
        tmp_day_df = tmp_day_df.set_index(['dt', 'Ticker'])[v1_model_name_pool + v1_model_pool_proba1]
        this_date_tot_prob = pd.concat([this_date_tot_prob, tmp_day_df.reindex(this_date_local_sample_index)], axis=1)

    tot_local_prob = pd.concat([tot_local_prob, this_date_tot_prob])

tot_local_prob.fillna(0, inplace=True)
for column in tot_local_prob.columns:
    tot_local_prob[column] = tot_local_prob[column].astype(float)

sell1_signal = pd.concat([tot_local_prob, local_basic_sell1], axis=1, join_axes=[tot_local_prob.index]).loc[basic_samples_trigger.index].sort_index()
sell1_model_track_v1 = modeltrack_Tool('JupiterNSell', version_date_v1, end_date_h, savepath, sell1_signal, v1_model_name_all, v1_model_name_pool, 4)
tot_local_returnv1, tot_local_predict_summaryv1 = sell1_model_track_v1.cal_modeltrack_data(type='vote')
tot_local_returnv1_pool, tot_local_predict_summaryv1_pool = sell1_model_track_v1.cal_modeltrack_data(type='all')

# 保存用于复盘的文件
sell1_local = pd.concat([sell1_model_track_v1.rawdata.copy(), sell1_model_track_v1.rawdata.copy(), sell1_model_track_v1.rawdata.copy()])
sell1_trigger = sell1_local.loc[basic_samples_trigger.index]

writer = pd.ExcelWriter('%sJupiterNSell策略实盘与本地触发对比_%s_%s.xlsx' % (savepath, year_start_date, end_date_lw))
sell1_trigger.reset_index().to_excel(writer, sheet_name='Sell1实盘触发明细')
sell1_local.reset_index().to_excel(writer, sheet_name='Sell1本地触发明细')
writer.save()

# 写入excel
workbook = xlsxwriter.Workbook('%s%s模型跟踪v1_%s_%s.xlsx' % (savepath, sell1_model_track_v1.strategy, year_start_date, end_date_lw))
generate_sheet(workbook, savepath, sell1_model_track_v1.strategy, tot_local_predict_summaryv1, tot_local_returnv1, int(np.ceil(len(v1_model_name_all) / 2) + 2), '1')
generate_sheet(workbook, savepath, sell1_model_track_v1.strategy, tot_local_predict_summaryv1_pool, tot_local_returnv1_pool, len(v1_model_name_pool), '1modelpool')
workbook.close()