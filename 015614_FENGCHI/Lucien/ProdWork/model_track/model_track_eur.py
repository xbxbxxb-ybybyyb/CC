# coding: utf-8
# Author：fengchi863
# Date ：2023/5/22 17:20
from xquant.factordata import FactorData

s = FactorData()
import xlsxwriter
from ProdWork.model_track.config import *

#################--------Europa---------#############
# 先进行本地的Basic拼接和筛选
version_date_v2 = '2023-02-13'
version_date_v3 = '2023-05-09'
str_version_date_v2 = version_date_v2[:4] + version_date_v2[5:7] + version_date_v2[-2:]
str_version_date_v3 = version_date_v3[:4] + version_date_v3[5:7] + version_date_v3[-2:]
local_basic_eur = pd.DataFrame()

eur_date = str_version_date_v2

for date in s.tradingday(year_start_date, end_date):
    this_date_basic = pd.read_hdf('/data/group/800463/project/project1_prod/left_v2212/daily_data/%s/Basic_zt_001_%s_%s.h5' % (date, date, date))
    if version_date_v2.replace('-', '') <= date < version_date_v3.replace('-', ''):
        factor = pd.DataFrame(100, columns=['last_buy_rise'], index=this_date_basic.index)
    elif date >= version_date_v3.replace('-', ''):
        factor = pd.read_pickle(f'/data/group/800463/project/project1_prod/right_v2304/daily_data/{date}_europa/all_factor_zt_merge_v2304_{date}_europa.pkl')[['last_buy_rise']]
    local_basic_eur = pd.concat([local_basic_eur, pd.concat([this_date_basic, factor], axis=1)])

Basic_samples = pd.read_excel('/data/group/800463/日内强势股/log_parse/因子耗时/实盘触发标签汇总New_%s.xlsx' % end_date_str)
Basic_samples = Basic_samples.sort_values(by='dt')
Basic_samples['dt'] = Basic_samples['dt'].apply(lambda x: pd.Timestamp(x))
Basic_samples_non_zt = Basic_samples[(Basic_samples['dt'] >= year_start_date_h)].set_index(['dt', 'Ticker'])
Basic_samples_eur_need = local_basic_eur.loc[Basic_samples_non_zt.loc[:pd.Timestamp(end_date_lw)].index]

# 这里重新集成。。。。。。模型对比里的不靠谱
v2_model_name_all = ['hmlRegFSV8LrXlyModel', 'hmlRegFSV8XgbXbcModel', 'totalRegO2ulFSV8XgbXbcModel',
                     'totalRegFSV8XgbWjModel', 'totalRegFSV8LgbWjModel', 'hmlRegFSV8XgbWjModel']
v2_model_name_proba1 = [x.split('Model')[0] + '_proba1' for x in v2_model_name_all]
v2_model_name_pool = v2_model_name_all+['hmlRegFSV8XgbXlyModel','totalRegFSRSXgbXlyModel','totalRegXgbSkkModel','totalRegXgbXbcModel']
v2_model_pool_proba1 = [x.split('Model')[0] + '_proba1' for x in v2_model_name_pool]

v3_model_name_all = ['totalRegO2ulFSV8XgbXbcModel','totalRegXgbFSV8WjModel','hmlRegFSV8LrXbcModel','hmlRegFSV8XgbWjModel',
                       'totalRegFSRSXgbSkkModel','totalRegFSV10LrXbcModel']
v3_model_name_proba1 = [x.split('Model')[0] + '_proba1' for x in v3_model_name_all]
v3_model_name_pool = v3_model_name_all + ['hmlRegFSV8LrXlyModel', 'hmlRegFSV8XgbSkkModel', 'totalRegFSV10XgbSkkModel','totalRegFSV8LrXlyModel']
v3_model_pool_proba1 = [x.split('Model')[0] + '_proba1' for x in v3_model_name_pool]
v3_rename_modeldict = dict(zip(v3_model_name_all,['v3'+x for x in v3_model_name_all]))
v3_rename_probadict = dict(zip(v3_model_name_proba1,['v3'+x for x in v3_model_name_proba1]))
v3_rename_modelpooldict = dict(zip(v3_model_name_pool, ['v3' + x for x in v3_model_name_pool]))
v3_rename_probapooldict = dict(zip(v3_model_pool_proba1, ['v3' + x for x in v3_model_pool_proba1]))

v3_model_name_all, v3_model_name_proba1 = list(v3_rename_modeldict.values()), list(v3_rename_probadict.values())
v3_model_name_pool, v3_model_pool_proba1 = list(v3_rename_modelpooldict.values()), list(v3_rename_probapooldict.values())

tot_local_prob = pd.DataFrame()
tot_local_only_prob = pd.DataFrame()

for tradeDatestr in s.tradingday(year_start_date, end_date_lw):
    print('Europra:%s' % tradeDatestr)
    this_date_local_sample_index = local_basic_eur[(local_basic_eur.reset_index()['dt'] == pd.Timestamp(tradeDatestr)).values].index

    this_date_tot_prob = pd.DataFrame()
    this_date_local_only_prob = pd.DataFrame()

    if tradeDatestr >= str_version_date_v2:
        pred_path = '/data/group/800463/wangj/model_signal/Jupiter001/prod_v2/%s/%s_%s_europa_fac_20221116_new_daily_pred.csv' % (tradeDatestr, tradeDatestr, tradeDatestr)
        tmp_day_df = pd.read_csv(pred_path)
        tmp_day_df['dt'] = tmp_day_df['dt'].apply(lambda x: pd.Timestamp(x))
        tmp_day_df = tmp_day_df.set_index(['dt', 'Ticker'])[v2_model_name_pool + v2_model_pool_proba1]

        this_date_tot_prob = pd.concat([this_date_tot_prob, tmp_day_df.reindex(this_date_local_sample_index)], axis=1)
        this_date_local_only_prob = pd.concat([this_date_local_only_prob, tmp_day_df.reindex(this_date_local_sample_index)], axis=1)

    if tradeDatestr >= str_version_date_v3:
        pred_path = '/data/group/800463/wangj/model_signal/Jupiter001/prod_v3/%s/%s_%s_europa_fac_20230329_daily_pred.csv' % (tradeDatestr, tradeDatestr, tradeDatestr)
        tmp_day_df = pd.read_csv(pred_path)
        tmp_day_df.rename(columns=v3_rename_modeldict, inplace=True)
        tmp_day_df.rename(columns=v3_rename_probadict, inplace=True)
        tmp_day_df.rename(columns=v3_rename_modelpooldict, inplace=True)
        tmp_day_df.rename(columns=v3_rename_probapooldict, inplace=True)
        tmp_day_df['dt'] = tmp_day_df['dt'].apply(lambda x: pd.Timestamp(x))
        tmp_day_df = tmp_day_df.set_index(['dt', 'Ticker'])[v3_model_name_pool + v3_model_pool_proba1]
        this_date_tot_prob = pd.concat([this_date_tot_prob, tmp_day_df.reindex(this_date_local_sample_index)], axis=1)
        this_date_local_only_prob = pd.concat([this_date_local_only_prob, tmp_day_df.reindex(this_date_local_sample_index)], axis=1)

    tot_local_prob = pd.concat([tot_local_prob, this_date_tot_prob])
    tot_local_only_prob = pd.concat([tot_local_only_prob, this_date_local_only_prob])

tot_local_prob.fillna(0, inplace=True)
tot_local_only_prob.fillna(0, inplace=True)
for column in tot_local_prob.columns:
    tot_local_prob[column] = tot_local_prob[column].astype(float)
for column in tot_local_only_prob.columns:
    tot_local_only_prob[column] = tot_local_only_prob[column].astype(float)

eur_signal = pd.concat([tot_local_prob, local_basic_eur], axis=1, join_axes=[tot_local_prob.index]).loc[Basic_samples_eur_need.index].sort_index()
eur_model_track_v2 = modeltrack_Tool('Europa', version_date_v2, end_date_h, savepath, eur_signal, v2_model_name_all, v2_model_name_pool, 3)   # 用的jupiter上线的时间
tot_local_returnv2, tot_local_predict_summaryv2 = eur_model_track_v2.cal_modeltrack_data(type='vote')
tot_local_returnv2_pool, tot_local_predict_summaryv2_pool = eur_model_track_v2.cal_modeltrack_data(type='all')

eur_model_track_v2comp = modeltrack_Tool('Europa', version_date_v3, end_date_h, savepath, eur_signal, v2_model_name_all, v2_model_name_pool, 3)
tot_local_returnv2comp, tot_local_predict_summaryv2comp = eur_model_track_v2comp.cal_modeltrack_data(type='vote')
tot_local_returnv2comp_pool, tot_local_predict_summaryv2comp_pool = eur_model_track_v2comp.cal_modeltrack_data(type='all')

eur_model_track_v3 = modeltrack_Tool('Europa', version_date_v3, end_date_h, savepath, eur_signal, v3_model_name_all, v3_model_name_pool, 4)
tot_local_returnv3, tot_local_predict_summaryv3 = eur_model_track_v3.cal_modeltrack_data(type='vote')
tot_local_returnv3_pool, tot_local_predict_summaryv3_pool = eur_model_track_v3.cal_modeltrack_data(type='all')

# 保存用于复盘的文件
eur_local = pd.concat([eur_model_track_v2.rawdata.copy(), eur_model_track_v3.rawdata.copy()])
eur_trigger = eur_local.loc[Basic_samples_eur_need.index]

writer = pd.ExcelWriter('%sEuropa策略实盘与本地触发对比_%s_%s.xlsx' % (savepath, year_start_date, end_date_lw))
eur_trigger.reset_index().to_excel(writer, sheet_name='Europa实盘触发明细')
eur_local.reset_index().to_excel(writer, sheet_name='Europa本地触发明细')
writer.save()

# 写入excel
workbook = xlsxwriter.Workbook('%s%s模型跟踪v3_%s_%s.xlsx' % (savepath, eur_model_track_v2.strategy, year_start_date, end_date_lw))
generate_sheet(workbook, savepath, eur_model_track_v2.strategy, tot_local_predict_summaryv2, tot_local_returnv2, int(np.ceil(len(v2_model_name_all) / 2) + 2), '2')
generate_sheet(workbook, savepath, eur_model_track_v2.strategy, tot_local_predict_summaryv2_pool, tot_local_returnv2_pool, len(v2_model_name_pool), '2modelpool')
generate_sheet(workbook, savepath, eur_model_track_v3.strategy, tot_local_predict_summaryv3, tot_local_returnv3, int(np.ceil(len(v3_model_name_all) / 2) + 2), '3')
generate_sheet(workbook, savepath, eur_model_track_v3.strategy, tot_local_predict_summaryv3_pool, tot_local_returnv3_pool, len(v3_model_name_pool), '3modelpool')
generate_sheet(workbook, savepath, eur_model_track_v2comp.strategy, tot_local_predict_summaryv2comp, tot_local_returnv2comp, int(np.ceil(len(v2_model_name_all) / 2) + 2), '2comp')
generate_sheet(workbook, savepath, eur_model_track_v2comp.strategy, tot_local_predict_summaryv2comp_pool, tot_local_returnv2comp_pool, len(v2_model_name_pool), '2compmodelpool')

workbook.close()