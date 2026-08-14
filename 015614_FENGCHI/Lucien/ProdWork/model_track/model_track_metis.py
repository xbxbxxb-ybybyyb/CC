# coding: utf-8
# Author：fengchi863
# Date ：2023/5/22 14:04

from xquant.factordata import FactorData

s = FactorData()
import matplotlib.pyplot as plt
import xlsxwriter
from ProdWork.model_track.modeltrack_Tool_v2 import *
from ProdWork.model_track.config import *

#################--------Metis---------#############
# 先进行本地的Basic拼接和筛选
version_date_v1 = '2023-09-01'  # 当时样本外区间最多到20230831
str_version_date_v1 = version_date_v1[:4] + version_date_v1[5:7] + version_date_v1[-2:]
local_basic_metis = pd.DataFrame()

if str_version_date_v1 < year_start_date:
    eur_date = year_start_date
else:
    eur_date = str_version_date_v1
for date in s.tradingday(year_start_date, end_date):
    this_date_basic = pd.read_hdf('/data/group/800463/project/project1_prod/left_v2212/daily_data/%s/Basic_metis_%s_%s.h5' % (date, date, date))
    local_basic_metis = pd.concat([local_basic_metis, this_date_basic])

Basic_samples = pd.read_excel('/data/group/800463/日内强势股/metis_log_parse/因子耗时/实盘触发标签汇总Metis_%s.xlsx' % end_date_str)
Basic_samples = Basic_samples.sort_values(by='dt')
Basic_samples['dt'] = Basic_samples['dt'].apply(lambda x: pd.Timestamp(x))
Basic_samples_non_zt = Basic_samples[(Basic_samples['dt'] >= year_start_date_h)].set_index(['dt', 'Ticker'])
Basic_samples_metis_need = local_basic_metis.loc[Basic_samples_non_zt.loc[:pd.Timestamp(end_date_lw)].index]

# 这里重新集成。。。。。。模型对比里的不靠谱

v1_model_name_all =['totalRegFSRSXgbXbcModel',
                     'totalRegFSRSXgbWjModel',
                     'totalRegFSV10XgbZwhModel',
                     'totalRegFSRSXgbZwhModel',
                     'totalRegXgbSkkModel',
                     'totalRegFSV10LgbWjModel']
v1_model_name_proba1 = [x.split('Model')[0] + '_proba1' for x in v1_model_name_all]
v1_model_name_pool = ['totalRegFSV10LgbWjModel',
                     'totalRegXgbSkkModel',
                     'totalRegFSRSXgbSkkModel',
                     'totalRegFSRSXgbZwhModel',
                     'totalRegFSV10XgbZwhModel',
                     'totalRegFSRSXgbWjModel',
                     'totalRegFSRSXgbXbcModel',
                     'totalRegFSRSLgbFcModel',
                     'totalRegFSV8XgbWjModel',
                     'totalRegFSV11XgbXlyModel']
v1_model_pool_proba1 = [x.split('Model')[0] + '_proba1' for x in v1_model_name_pool]
v1_rename_modeldict = dict(zip(v1_model_name_all,['v1'+x for x in v1_model_name_all]))
v1_rename_probadict = dict(zip(v1_model_name_proba1,['v1'+x for x in v1_model_name_proba1]))
v1_rename_modelpooldict = dict(zip(v1_model_name_pool, ['v1' + x for x in v1_model_name_pool]))
v1_rename_probapooldict = dict(zip(v1_model_pool_proba1, ['v1' + x for x in v1_model_pool_proba1]))
v1_model_name_all, v1_model_name_proba1 = list(v1_rename_modeldict.values()), list(v1_rename_probadict.values())
v1_model_name_pool, v1_model_pool_proba1 = list(v1_rename_modelpooldict.values()), list(v1_rename_probapooldict.values())

tot_local_prob = pd.DataFrame()
for tradeDatestr in s.tradingday(year_start_date, end_date_lw):
    this_date_tot_prob = pd.DataFrame() # prob和only_prob好像没用，其实只用其中一个就可以
    this_date_local_sample_index = local_basic_metis[(local_basic_metis.reset_index()['dt'] == pd.Timestamp(tradeDatestr)).values].index
    if tradeDatestr >= version_date_v1:
        pred_path = '/data/group/800463/wangj/model_signal/Metis/v1/%s/%s_%s_metis_fac_20230821_new_daily_pred.csv' % (tradeDatestr, tradeDatestr, tradeDatestr)
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

# metis_signal = pd.concat([tot_local_prob, local_basic_metis], axis=1, join_axes=[tot_local_prob.index]).loc[Basic_samples_metis_need.index].sort_index()
metis_signal = pd.concat([tot_local_prob, local_basic_metis], axis=1, join_axes=[tot_local_prob.index]).sort_index()
metis_model_track_v1 = modeltrack_Tool('Metis', version_date_v1, end_date_h, savepath, metis_signal, v1_model_name_all, v1_model_name_pool, 4)
tot_local_returnv1, tot_local_predict_summaryv1 = metis_model_track_v1.cal_modeltrack_data(type='vote')
tot_local_returnv1_pool, tot_local_predict_summaryv1_pool = metis_model_track_v1.cal_modeltrack_data(type='all')

# 保存用于复盘的文件
metis_local = pd.concat([metis_model_track_v1.rawdata.copy(), metis_model_track_v1.rawdata.copy(), metis_model_track_v1.rawdata.copy()])
# metis_trigger = metis_local.loc[Basic_samples_metis_need.index]
metis_trigger = metis_local

writer = pd.ExcelWriter('%sMetis策略实盘与本地触发对比_%s_%s.xlsx' % (savepath, year_start_date, end_date_lw))
metis_trigger.reset_index().to_excel(writer, sheet_name='Metis实盘触发明细')
metis_local.reset_index().to_excel(writer, sheet_name='Metis本地触发明细')
writer.save()

# 写入excel
workbook = xlsxwriter.Workbook('%s%s模型跟踪v1_%s_%s.xlsx' % (savepath, metis_model_track_v1.strategy, year_start_date, end_date_lw))
generate_sheet(workbook, savepath, metis_model_track_v1.strategy, tot_local_predict_summaryv1, tot_local_returnv1, int(np.ceil(len(v1_model_name_all) / 2) + 2), '1')
generate_sheet(workbook, savepath, metis_model_track_v1.strategy, tot_local_predict_summaryv1_pool, tot_local_returnv1_pool, len(v1_model_name_pool), '1modelpool')
workbook.close()