# coding: utf-8
# Author：fengchi863
# Date ：2023/5/22 16:57
from xquant.factordata import FactorData

s = FactorData()
import xlsxwriter
from ProdWork.model_track.config import *

version_date_v9 = '2023-02-13'
str_version_date_v9 = version_date_v9[:4] + version_date_v9[5:7] + version_date_v9[-2:]
str_ver9_before1 = s.tradingday(version_date_v9[:4] + version_date_v9[5:7] + version_date_v9[-2:], -2)[0]
version_date_v10 = '2024-10-21'  # v9-v10的时间，20241018是纯样本外最后一天，20241224是上实盘第一天
str_version_date_v10 = version_date_v10[:4] + version_date_v10[5:7] + version_date_v10[-2:]
str_ver10_before1 = s.tradingday(version_date_v10[:4] + version_date_v10[5:7] + version_date_v10[-2:], -2)[0]

# 先进行本地的Basic拼接和筛选
local_basic_file = pd.DataFrame()
for date in s.tradingday(str_version_date_v9, end_date):
    this_date_basic = pd.read_hdf('/data/group/800463/project/project1_prod/left_v2212/daily_data/%s/Basic_zt_%s_%s.h5' % (date, date, date))
    local_basic_file = pd.concat([local_basic_file, this_date_basic])

# 实盘触发的basic
Basic_samples = pd.read_excel('/data/group/800463/日内强势股/log_parse/因子耗时/实盘触发标签汇总_%s.xlsx' % end_date_str)
Basic_samples = Basic_samples.sort_values(by='dt')
Basic_samples['dt'] = Basic_samples['dt'].apply(lambda x: pd.Timestamp(x))
# Basic_samples_non_zt = Basic_samples[Basic_samples['ZTBysModel_local_prob'].isnull() & (Basic_samples['dt'] >= year_start_date_h)].set_index(['dt', 'Ticker'])
Basic_samples_non_zt = Basic_samples[(Basic_samples['dt'] >= year_start_date_h)].set_index(['dt', 'Ticker'])
Basic_samples_non_zt_need = local_basic_file.loc[Basic_samples_non_zt.loc[:pd.Timestamp(end_date_lw)].index]

# jupiter 所有子模型信号拼接
v9_model_name_all = ['totalRegFSV8LrXlyModel', 'hmlRegFSV8XgbWjModel', 'hmlRegFSV8XgbXlyModel',
                     'totalRegO2ulFSV8XgbXbcModel', 'totalRegXgbXbcModel', 'totalRegFSV8XgbWjModel']
v9_model_name_pool = v9_model_name_all + ['totalRegFSRSXgbXlyModel',
                                          'totalRegXgbSkkModel',
                                          'totalRegFSV8LgbXbcModel',
                                          'totalRegFSV8LgbWjModel']
v9_model_name_proba1 = [x.split('Model')[0] + '_proba1' for x in v9_model_name_all]
v9_model_name_pool_proba1 = [x.split('Model')[0] + '_proba1' for x in v9_model_name_pool]

v10_model_name_all = ['totalRegp5_FSZWHXgbZwhModel',
                      'totalRegp5_FSRSXgbXbcModel',
                      'totalRegp5_FSV8XgbZwhModel',
                      'totalRegp5_FSRSXgbFcModel',
                      'totalRegp5_FSV8XgbWjModel',
                      'totalRegp5_FSRSXgbSkkModel']
v10_model_name_pool = v10_model_name_all + ['totalRegp5_FSRSXgbZwhModel',
                                            'totalRegp5_FSV8XgbSkkModel',
                                            'totalRegp5_FSRSXgbXlyModel',
                                            'totalRegp5_FSV10XgbWjModel']
v10_model_name_proba1 = [x.split('Model')[0] + '_proba1' for x in v10_model_name_all]
v10_model_name_pool_proba1 = [x.split('Model')[0] + '_proba1' for x in v10_model_name_pool]


tot_local_prob = pd.DataFrame()
tot_local_only_prob = pd.DataFrame()

for tradeDatestr in s.tradingday(str_version_date_v9, end_date_lw):
    print('JupiterN:%s' % tradeDatestr)
    this_date_sample_index = local_basic_file[(local_basic_file.reset_index()['dt'] == pd.Timestamp(tradeDatestr)).values].index
    hml0_index = local_basic_file[(local_basic_file.reset_index()['dt'] == pd.Timestamp(tradeDatestr)).values].query('hml_factor==0').index
    hml1_index = local_basic_file[(local_basic_file.reset_index()['dt'] == pd.Timestamp(tradeDatestr)).values].query('hml_factor==1').index
    hml2_index = local_basic_file[(local_basic_file.reset_index()['dt'] == pd.Timestamp(tradeDatestr)).values].query('hml_factor==2').index

    this_date_tot_prob = pd.DataFrame()  # 触发样本模型信号汇总
    this_date_local_only_prob = pd.DataFrame()  # 本地样本模型信号汇总

    if tradeDatestr >= str_version_date_v9:
        pred_path = '/data/group/800463/wangj/model_signal/Jupiter/prod_v9/%s/%s_%s_jupiter_fac_20221220_daily_pred.csv' % (tradeDatestr, tradeDatestr, tradeDatestr)
        tmp_day_df = pd.read_csv(pred_path)
        tmp_day_df['dt'] = tmp_day_df['dt'].apply(lambda x: pd.Timestamp(x))
        tmp_day_df = tmp_day_df.set_index(['dt', 'Ticker'])[v9_model_name_pool + v9_model_name_pool_proba1]
        this_date_tot_prob = pd.concat([this_date_tot_prob, tmp_day_df.reindex(this_date_sample_index)], axis=1)
        this_date_local_only_prob = pd.concat([this_date_local_only_prob, tmp_day_df.reindex(this_date_sample_index)], axis=1)

    if tradeDatestr >= str_version_date_v10:
        pred_path = '/data/group/800463/wangj/model_signal/Jupiter/prod_v10/%s/%s_%s_jupiterN_fac_20240911_daily_pred.csv' % (tradeDatestr, tradeDatestr, tradeDatestr)
        tmp_day_df = pd.read_csv(pred_path)
        tmp_day_df['dt'] = tmp_day_df['dt'].apply(lambda x: pd.Timestamp(x))
        tmp_day_df = tmp_day_df.set_index(['dt', 'Ticker'])[v10_model_name_pool + v10_model_name_pool_proba1]
        this_date_tot_prob = pd.concat([this_date_tot_prob, tmp_day_df.reindex(this_date_sample_index)], axis=1)
        this_date_local_only_prob = pd.concat([this_date_local_only_prob, tmp_day_df.reindex(this_date_sample_index)], axis=1)
            
    tot_local_prob = pd.concat([tot_local_prob, this_date_tot_prob])
    tot_local_only_prob = pd.concat([tot_local_only_prob, this_date_local_only_prob])

tot_local_prob.fillna(0, inplace=True)
tot_local_only_prob.fillna(0, inplace=True)
for column in tot_local_prob.columns:
    tot_local_prob[column] = tot_local_prob[column].astype(float)
for column in tot_local_only_prob.columns:
    tot_local_only_prob[column] = tot_local_only_prob[column].astype(float)

# 已经拼好了，直接代入Tool类
# strategy_name, begindate, enddate, savepath, basic_df, sel_models, all_models):
jup_signal = pd.concat([tot_local_prob, local_basic_file], axis=1, join_axes=[tot_local_prob.index]).loc[Basic_samples_non_zt_need.index].sort_index()
jup_model_track_v10 = modeltrack_Tool('jupiter', version_date_v10, end_date_h, savepath, jup_signal, v10_model_name_all, v10_model_name_pool, 4)

tot_local_returnv10, tot_local_predict_summaryv10 = jup_model_track_v10.cal_modeltrack_data(type='vote') # 计算投票信息 第一个sheet
tot_local_returnv10_pool, tot_local_predict_summaryv10_pool = jup_model_track_v10.cal_modeltrack_data(type='all')  # 计算子模型信息 第二个sheet

# old 与 new 一起跑，谁的更好
jup_model_track_v9comp = modeltrack_Tool('jupiter', version_date_v10, end_date_h, savepath, jup_signal, v9_model_name_all, v9_model_name_all, 5)    # 最后一个参数是阈值，需要改
tot_local_returnv9comp, tot_local_predict_summaryv9comp = jup_model_track_v9comp.cal_modeltrack_data(type='vote')
tot_local_returnv9comp_pool, tot_local_predict_summaryv9comp_pool = jup_model_track_v9comp.cal_modeltrack_data(type='all')

# 旧的实盘期间的表现
# jup_model_track_v9 = modeltrack_Tool('jupiter', year_start_date_h, '2022-12-30', savepath, jup_signal, v9_model_name_all, v9_model_name_all,7)
jup_model_track_v9 = modeltrack_Tool('jupiter', year_start_date_h, end_date_h, savepath, jup_signal, v9_model_name_all, v9_model_name_all, 5)
tot_local_returnv9, tot_local_predict_summaryv9 = jup_model_track_v9.cal_modeltrack_data(type='vote')
tot_local_returnv9_pool, tot_local_predict_summaryv9_pool = jup_model_track_v9.cal_modeltrack_data(type='all')

# 计算各个版本各个模型本地信号的评价
jupiterN_local = pd.concat([jup_model_track_v9.rawdata.copy(), jup_model_track_v10.rawdata.copy()])
jupiterN_trigger = jupiterN_local.loc[Basic_samples_non_zt_need.index]

writer = pd.ExcelWriter('%sJupiter策略实盘与本地触发对比_%s_%s.xlsx' % (savepath, year_start_date, end_date_lw))
jupiterN_trigger.reset_index().to_excel(writer, sheet_name='jupiterN实盘触发明细')    # 复盘用到
jupiterN_local.reset_index().to_excel(writer, sheet_name='jupiterN本地触发明细')
writer.save()

# 写入excel
workbook = xlsxwriter.Workbook('%s%s模型跟踪v4_%s_%s.xlsx' % (savepath, jup_model_track_v9.strategy, year_start_date, end_date_lw))

generate_sheet(workbook, savepath, jup_model_track_v9.strategy, tot_local_predict_summaryv9, tot_local_returnv9, int(np.ceil(len(v9_model_name_all) / 2) + 2), '9')
generate_sheet(workbook, savepath, jup_model_track_v9.strategy, tot_local_predict_summaryv9_pool, tot_local_returnv9_pool, len(v9_model_name_all), '9modelpool')
generate_sheet(workbook, savepath, jup_model_track_v10.strategy, tot_local_predict_summaryv10, tot_local_returnv10,int(np.ceil(len(v10_model_name_all)/2)+2), '10')
generate_sheet(workbook, savepath, jup_model_track_v10.strategy, tot_local_predict_summaryv10_pool, tot_local_returnv10_pool, len(v10_model_name_pool), '10modelpool')
generate_sheet(workbook, savepath, jup_model_track_v9comp.strategy, tot_local_predict_summaryv9comp, tot_local_returnv9comp, int(np.ceil(len(v9_model_name_all) / 2) + 2), '9comp')
generate_sheet(workbook, savepath, jup_model_track_v9comp.strategy, tot_local_predict_summaryv9comp_pool, tot_local_returnv9comp_pool, len(v9_model_name_all), '9compmodelpool')
workbook.close()