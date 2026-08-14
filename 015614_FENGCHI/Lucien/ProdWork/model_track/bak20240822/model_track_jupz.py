# coding: utf-8
# Author：fengchi863
# Date ：2023/5/22 14:04

from xquant.factordata import FactorData

s = FactorData()
import matplotlib.pyplot as plt
import xlsxwriter
from ProdWork.model_track.modeltrack_Tool_v2 import *
from ProdWork.model_track.config import *

#################--------JupiterZ---------#############
version_date_v1 = '2024-01-01'  # 第一个版本上线的时间
str_version_date_v1 = version_date_v1[:4] + version_date_v1[5:7] + version_date_v1[-2:]
local_basic_jupz = pd.DataFrame()

# 读取全部基础样本
for date in s.tradingday(str_version_date_v1, end_date):
    # by fenc: JupiterZ

    # 使用因子
    # dataalt1 = '/data/group/800463/project/projectS_prod/daily_data/%s_v1/sell_factor_v1_%s.pkl' % (date, date)
    # rawdata1 = pd.read_pickle(dataalt1).sort_index()
    # dataalt2 = '/data/group/800463/project/project1_prod/right_v2304/daily_data/%s/all_factor_zt_merge_v2304_%s.pkl' % (date, date)
    # rawdata2 = pd.read_pickle(dataalt2).sort_index().query('last_is_zt==1')
    # this_date_jupz = pd.concat([rawdata1.loc[rawdata2.index], rawdata2], axis=1)

    dataalt2 = '/data/group/800463/project/project1_prod/right_v2304/daily_data/%s/all_factor_zt_merge_v2304_%s.pkl' % (date, date)
    this_date_jupz = pd.read_pickle(dataalt2).sort_index().query('last_is_zt==1')
    concat_df_fpath = '/data/group/800463/project/projectS_prod/daily_data/%s_v1/sell_factor_v1_%s.pkl' % (date, date)
    concat_df = pd.read_pickle(concat_df_fpath)
    this_date_jupz = pd.concat([concat_df.loc[this_date_jupz.index], this_date_jupz], axis=1)
    local_basic_jupz = pd.concat([local_basic_jupz, this_date_jupz])

# 读取实盘触发的样本
trigger_samples = pd.DataFrame()
for date in s.tradingday(str_version_date_v1, end_date):
    date_str = date[0:4] + '-' + date[4:6] + '-' + date[6:8]
    if date_str <= '2024-02-29':
        this_date_trigger = pd.read_excel('/data/group/800463/日内强势股/log_parse/因子耗时/因子耗时_%s_prod.xlsx' % date_str, sheet_name='因子耗时', index_col=0)
        this_date_trigger['dt'] = pd.to_datetime(date)
        ZT_model0 = list(filter(lambda x: 'ZT' in x, this_date_trigger.columns.tolist()))[0]
        this_date_trigger = this_date_trigger[~this_date_trigger[ZT_model0].isna()]
    elif date_str > '2024-02-29':
        this_date_trigger = pd.read_excel('/data/group/800463/日内强势股/sell_log_parse/因子耗时/因子耗时_%s_prod.xlsx' % date_str, sheet_name='JupiterZ样本', index_col=0)
        this_date_trigger['dt'] = pd.to_datetime(date)
    trigger_samples = pd.concat([trigger_samples, this_date_trigger])
trigger_samples = trigger_samples.sort_values('dt').reset_index().set_index(['dt', 'index'])
trigger_samples.index.names = ['dt', 'Ticker']
# 全部基础样本与实盘触发样本取交集
basic_samples_trigger = local_basic_jupz.loc[trigger_samples.loc[:pd.Timestamp(end_date_lw)].index]

v1_model_name_all = ['totalafterZRegFSV11XgbXlyModel',
                     'totalAfterZRegFSV8XgbXlyModel',
                     'totalRegLgbFcModel',
                     'totalafterZRegLgbFSV8FcModel',
                     'totalAfterZRegXgbXbcModel',
                     'totalRegFSRSXgbSkkModel']
v1_model_name_proba1 = [x.split('Model')[0] + '_proba1' for x in v1_model_name_all]
v1_model_name_pool = v1_model_name_all + ['totalAfterZRegFSRSLrSkkModel', 'totalRegFSV8XgbSkkModel', 'totalAfterZRegXgbSkkModel', 'totalAfterZRegXgbFSRSWjModel']
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
    this_date_local_sample_index = local_basic_jupz[(local_basic_jupz.reset_index()['dt'] == pd.Timestamp(tradeDatestr)).values].index
    if tradeDatestr >= version_date_v1:
        pred_path = '/data/group/800463/wangj/model_signal/JupiterZ/prod_v2/%s/%s_%s_jupiterZ_fac_20230415_daily_pred.csv' % (tradeDatestr, tradeDatestr, tradeDatestr)
        tmp_day_df = pd.read_csv(pred_path)
        tmp_day_df.rename(columns=v1_rename_modeldict, inplace=True)
        tmp_day_df.rename(columns=v1_rename_probadict, inplace=True)
        tmp_day_df.rename(columns=v1_rename_modelpooldict, inplace=True)
        tmp_day_df.rename(columns=v1_rename_probapooldict, inplace=True)
        tmp_day_df['Ticker'] = tmp_day_df['Indexs'].apply(lambda x: x[:9])
        tmp_day_df['dt'] = tmp_day_df['Indexs'].apply(lambda x: x[9:])
        tmp_day_df['dt'] = tmp_day_df['dt'].apply(lambda x: pd.Timestamp(x))
        tmp_day_df = tmp_day_df.set_index(['dt', 'Ticker'])[v1_model_name_pool + v1_model_pool_proba1]
        this_date_tot_prob = pd.concat([this_date_tot_prob, tmp_day_df.reindex(this_date_local_sample_index)], axis=1)

    tot_local_prob = pd.concat([tot_local_prob, this_date_tot_prob])

tot_local_prob.fillna(0, inplace=True)
for column in tot_local_prob.columns:
    tot_local_prob[column] = tot_local_prob[column].astype(float)

jupz_signal = pd.concat([tot_local_prob, local_basic_jupz], axis=1, join_axes=[tot_local_prob.index]).loc[basic_samples_trigger.index].sort_index()
jupz_model_track_v1 = modeltrack_Tool('JupiterZ', version_date_v1, end_date_h, savepath, jupz_signal, v1_model_name_all, v1_model_name_pool, 4)
tot_local_returnv1, tot_local_predict_summaryv1 = jupz_model_track_v1.cal_modeltrack_data(type='vote')
tot_local_returnv1_pool, tot_local_predict_summaryv1_pool = jupz_model_track_v1.cal_modeltrack_data(type='all')

# 保存用于复盘的文件
jupz_local = pd.concat([jupz_model_track_v1.rawdata.copy(), jupz_model_track_v1.rawdata.copy(), jupz_model_track_v1.rawdata.copy()])
jupz_trigger = jupz_local.loc[basic_samples_trigger.index]

writer = pd.ExcelWriter('%sJupiterZ策略实盘与本地触发对比_%s_%s.xlsx' % (savepath, year_start_date, end_date_lw))
jupz_trigger.reset_index().to_excel(writer, sheet_name='JupiterZ实盘触发明细')
jupz_local.reset_index().to_excel(writer, sheet_name='JupiterZ本地触发明细')
writer.save()

# 写入excel
workbook = xlsxwriter.Workbook('%s%s模型跟踪v1_%s_%s.xlsx' % (savepath, jupz_model_track_v1.strategy, year_start_date, end_date_lw))
generate_sheet(workbook, savepath, jupz_model_track_v1.strategy, tot_local_predict_summaryv1, tot_local_returnv1, int(np.ceil(len(v1_model_name_all) / 2) + 2), '1')
generate_sheet(workbook, savepath, jupz_model_track_v1.strategy, tot_local_predict_summaryv1_pool, tot_local_returnv1_pool, len(v1_model_name_pool), '1modelpool')
workbook.close()