# coding: utf-8
# Author：fengchi863
# Date ：2023/5/22 17:20
from xquant.factordata import FactorData

s = FactorData()
import matplotlib.pyplot as plt
import xlsxwriter
from ProdWork.model_track.modeltrack_Tool_v2 import *
from ProdWork.model_track.config import *

#################--------Europa---------#############
# 先进行本地的Basic拼接和筛选
version_date_v1 = '2022-05-18'
version_date_v2 = '2023-02-13'
version_date_v3 = '2023-05-09'
str_version_date_v1 = version_date_v1[:4] + version_date_v1[5:7] + version_date_v1[-2:]
str_version_date_v2 = version_date_v2[:4] + version_date_v2[5:7] + version_date_v2[-2:]
str_version_date_v3 = version_date_v3[:4] + version_date_v3[5:7] + version_date_v3[-2:]
local_basic_eur = pd.DataFrame()

if str_version_date_v1 < year_start_date:
    eur_date = year_start_date
else:
    eur_date = str_version_date_v1
for date in s.tradingday(eur_date, end_date):
    this_date_basic = pd.read_hdf('/data/group/800463/project/project1_prod/generalStrong_v3/daily_data/%s/Basic_zt_001_%s_%s.h5' % (date, date, date))
    local_basic_eur = pd.concat([local_basic_eur, this_date_basic])

Basic_samples = pd.read_excel('/data/group/800463/日内强势股/log_parse/因子耗时/实盘触发标签汇总New_%s.xlsx' % end_date_str)
Basic_samples = Basic_samples.sort_values(by='dt')
Basic_samples['dt'] = Basic_samples['dt'].apply(lambda x: pd.Timestamp(x))
Basic_samples_non_zt = Basic_samples[(Basic_samples['dt'] >= year_start_date_h)].set_index(['dt', 'Ticker'])
Basic_samples_eur_need = local_basic_eur.loc[Basic_samples_non_zt.loc[:pd.Timestamp(end_date_lw)].index]

# 这里重新集成。。。。。。模型对比里的不靠谱
DJ_model_name_all = ['TotalDjRegModel', 'RisePctLowDjModel', 'RisePctHighDjModel']
WJ_model_name_all = ['TotalXgbRegWjModel', 'Hml0WjModel', 'Hml1WjModel', 'Hml2WjModel']
XLY_model_name_all = ['HighHMLXgbModel', 'LowHMLXgbModel', 'MedianHMLXgbModel', 'TotalXgbModel']
v1_model_name_all = ['TotalDjRegModel', 'RisePctDjModel', 'TotalXgbRegWjModel', 'HmlWjModel', 'TotalXgbModel', 'HMLXgbModel']
v1_model_name_proba1 = [x.split('Model')[0] + '_proba1' for x in v1_model_name_all]
v2_model_name_all = ['hmlRegFSV8LrXlyModel', 'hmlRegFSV8XgbXbcModel', 'totalRegO2ulFSV8XgbXbcModel',
                     'totalRegFSV8XgbWjModel', 'totalRegFSV8LgbWjModel', 'hmlRegFSV8XgbWjModel']
v2_model_name_proba1 = [x.split('Model')[0] + '_proba1' for x in v2_model_name_all]
v2_model_name_pool = v2_model_name_all+['hmlRegFSV8XgbXlyModel','totalRegFSRSXgbXlyModel','totalRegXgbSkkModel','totalRegXgbXbcModel']
v2_model_pool_proba1 = [x.split('Model')[0] + '_proba1' for x in v2_model_name_pool]

v3_model_name_all =['totalRegO2ulFSV8XgbXbcModel','totalRegXgbFSV8WjModel','hmlRegFSV8LrXbcModel','hmlRegFSV8XgbWjModel',
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

xly_total_prediction001 = pd.DataFrame()
for date in s.tradingday(eur_date, end_date_lw):
    xly_new_models_path = '/data/group/800463/xiely/model_signal/%s_jptnew/model_predict.pkl' % date
    this_date_xly_prob = pd.read_pickle(xly_new_models_path)
    this_date_xly_prob.rename(
        columns={'Hml0XgbModel_proba': 'LowHMLXgbModel_proba', 'Hml1XgbModel_proba': 'MedianHMLXgbModel_proba',
                 'Hml2PMMLModel_proba': 'HighHMLXgbModel_proba'}, inplace=True)
    xly_total_prediction001 = pd.concat([xly_total_prediction001, this_date_xly_prob])
tot_local_prob = pd.DataFrame()
tot_local_only_prob = pd.DataFrame()

for tradeDatestr in s.tradingday(eur_date, end_date_lw):
    print('Europra:%s' % tradeDatestr)
    this_date_local_sample_index = local_basic_eur[(local_basic_eur.reset_index()['dt'] == pd.Timestamp(tradeDatestr)).values].index
    hml0_index = local_basic_eur[(local_basic_eur.reset_index()['dt'] == pd.Timestamp(tradeDatestr)).values].query('hml_factor==0').index
    hml1_index = local_basic_eur[(local_basic_eur.reset_index()['dt'] == pd.Timestamp(tradeDatestr)).values].query('hml_factor==1').index
    hml2_index = local_basic_eur[(local_basic_eur.reset_index()['dt'] == pd.Timestamp(tradeDatestr)).values].query('hml_factor==2').index

    this_date_tot_prob = pd.DataFrame()
    this_date_local_only_prob = pd.DataFrame()
    # -----------------------------董坚的模型------------------------------
    this_date_dj_prob = pd.DataFrame()
    for DJ_model_name in DJ_model_name_all:
        if DJ_model_name == 'TotalDjRegModel':
            DJ_model_local_label = pd.read_hdf(
                '/data/group/800463/dongj/model_signal/jupiter001/model_output_everyday/%s_reg_v1/pred_label.h5' % tradeDatestr).rename(columns={'pred_label': DJ_model_name})
            DJ_model_local_prob = pd.read_hdf(
                '/data/group/800463/dongj/model_signal/jupiter001/model_output_everyday/%s_reg_v1/pred_prob.h5' % tradeDatestr) \
                .rename(columns={'pred_prob': DJ_model_name.split('Model')[0] + '_proba1'})
        elif DJ_model_name == 'Hml0DjModel':
            DJ_model_local_label = pd.read_hdf(
                '/data/group/800463/dongj/model_signal/jupiter001/model_output_everyday/%s_hml_low_v2/pred_label.h5' % tradeDatestr).rename(
                columns={'pred_label': DJ_model_name})
            DJ_model_local_prob = pd.read_hdf(
                '/data/group/800463/dongj/model_signal/jupiter001/model_output_everyday/%s_hml_low_v2/pred_prob.h5' % tradeDatestr) \
                .rename(columns={'pred_prob': DJ_model_name.split('Model')[0] + '_proba1'})
        elif DJ_model_name == 'Hml1DjModel':
            DJ_model_local_label = pd.read_hdf(
                '/data/group/800463/dongj/model_signal/jupiter001/model_output_everyday/%s_hml_except_v2/pred_label.h5' % tradeDatestr).rename(
                columns={'pred_label': DJ_model_name})
            DJ_model_local_prob = pd.read_hdf(
                '/data/group/800463/dongj/model_signal/jupiter001/model_output_everyday/%s_hml_except_v2/pred_prob.h5' % tradeDatestr) \
                .rename(columns={'pred_prob': DJ_model_name.split('Model')[0] + '_proba1'})
        elif DJ_model_name == 'Hml2DjModel':
            DJ_model_local_label = pd.read_hdf(
                '/data/group/800463/dongj/model_signal/jupiter001/model_output_everyday/%s_hml_high_v2/pred_label.h5' % tradeDatestr).rename(
                columns={'pred_label': DJ_model_name})
            DJ_model_local_prob = pd.read_hdf(
                '/data/group/800463/dongj/model_signal/jupiter001/model_output_everyday/%s_hml_high_v2/pred_prob.h5' % tradeDatestr) \
                .rename(columns={'pred_prob': DJ_model_name.split('Model')[0] + '_proba1'})
        elif DJ_model_name == 'RisePctHighDjModel':
            DJ_model_local_label = pd.read_hdf(
                '/data/group/800463/dongj/model_signal/jupiter001/model_output_everyday/%s_risePct_high_v1/pred_label.h5' % tradeDatestr).rename(
                columns={'pred_label': DJ_model_name})
            DJ_model_local_prob = pd.read_hdf(
                '/data/group/800463/dongj/model_signal/jupiter001/model_output_everyday/%s_risePct_high_v1/pred_prob.h5' % tradeDatestr) \
                .rename(columns={'pred_prob': DJ_model_name.split('Model')[0] + '_proba1'})
        elif DJ_model_name == 'RisePctLowDjModel':
            DJ_model_local_label = pd.read_hdf(
                '/data/group/800463/dongj/model_signal/jupiter001/model_output_everyday/%s_risePct_low_v1/pred_label.h5' % tradeDatestr).rename(
                columns={'pred_label': DJ_model_name})
            DJ_model_local_prob = pd.read_hdf(
                '/data/group/800463/dongj/model_signal/jupiter001/model_output_everyday/%s_risePct_low_v1/pred_prob.h5' % tradeDatestr) \
                .rename(columns={'pred_prob': DJ_model_name.split('Model')[0] + '_proba1'})
        DJ_model_local_label = pd.concat([DJ_model_local_label, DJ_model_local_prob], axis=1)
        this_date_dj_prob = pd.concat([this_date_dj_prob, DJ_model_local_label], axis=1)

    this_date_dj_prob['RisePctDjModel'] = this_date_dj_prob['RisePctLowDjModel'].fillna(0) + \
                                          this_date_dj_prob['RisePctHighDjModel'].fillna(0)
    this_date_dj_prob['RisePctDj_proba1'] = pd.concat([this_date_dj_prob['RisePctLowDj_proba1'].dropna(),
                                                       this_date_dj_prob['RisePctHighDj_proba1'].dropna()]).reindex(
        this_date_dj_prob.index).fillna(0)
    this_date_tot_prob = pd.concat([this_date_tot_prob, this_date_dj_prob[['TotalDjRegModel', 'RisePctDjModel','TotalDjReg_proba1', 'RisePctDj_proba1']] \
                                   .reindex(this_date_local_sample_index)], axis=1)
    this_date_local_only_prob = pd.concat(
        [this_date_local_only_prob,
         this_date_dj_prob[['TotalDjRegModel', 'RisePctDjModel','TotalDjReg_proba1', 'RisePctDj_proba1']].reindex(this_date_local_sample_index).fillna(0)],
        axis=1)
    # -----------------------------王敬的模型------------------------------
    this_date_wj_prob = pd.DataFrame()
    for WJ_model_name in WJ_model_name_all:
        # 核对模型的预测数据
        if WJ_model_name == 'TotalLgbClaWjModel':
            wj_new_models_path = '/data/group/800463/wangj/model_signal/Jupiter/allLgbClaModel/%s' % (tradeDatestr)
        elif WJ_model_name == 'Type0LgbClaWjModel':
            wj_new_models_path = '/data/group/800463/wangj/model_signal/Jupiter/type0LgbClaModel/%s' % (
                tradeDatestr)
        elif WJ_model_name == 'Type1LgbClaWjModel':
            wj_new_models_path = '/data/group/800463/wangj/model_signal/Jupiter/type1LgbClaModel/%s' % (
                tradeDatestr)
        elif WJ_model_name == 'Type2LgbClaWjModel':
            wj_new_models_path = '/data/group/800463/wangj/model_signal/Jupiter/type2LgbClaModel/%s' % (
                tradeDatestr)
        elif WJ_model_name == 'Type0LrClaWjModel':
            wj_new_models_path = '/data/group/800463/wangj/model_signal/Jupiter/type0LrClaModel/%s' % (
                tradeDatestr)
        elif WJ_model_name == 'Type1LrClaWjModel':
            wj_new_models_path = '/data/group/800463/wangj/model_signal/Jupiter/type1LrClaModel/%s' % (
                tradeDatestr)
        elif WJ_model_name == 'Type2LrClaWjModel':
            wj_new_models_path = '/data/group/800463/wangj/model_signal/Jupiter/type2LrClaModel/%s' % (
                tradeDatestr)
        elif WJ_model_name == 'TotalXgbRegWjModel':
            wj_new_models_path = '/data/group/800463/wangj/model_signal/test/Jupiter001/allregwjModel/%s' % (
                tradeDatestr)
        elif WJ_model_name == 'TotalLrClaWjModel':
            wj_new_models_path = '/data/group/800463/wangj/model_signal/Jupiter/allLrClaModel/%s' % (
                tradeDatestr)
        elif WJ_model_name == 'Type0WjModel':
            wj_new_models_path = '/data/group/800463/wangj/model_signal/Jupiter/type0regwjModel/%s' % (
                tradeDatestr)
        elif WJ_model_name == 'Type1WjModel':
            wj_new_models_path = '/data/group/800463/wangj/model_signal/Jupiter/type1regwjModel/%s' % (
                tradeDatestr)
        elif WJ_model_name == 'Type2WjModel':
            wj_new_models_path = '/data/group/800463/wangj/model_signal/Jupiter/type2regwjModel/%s' % (
                tradeDatestr)
        elif WJ_model_name == 'Hml0WjModel':
            wj_new_models_path = '/data/group/800463/wangj/model_signal/test/Jupiter001/hml0regwjModel/%s' % (
                tradeDatestr)
        elif WJ_model_name == 'Hml1WjModel':
            wj_new_models_path = '/data/group/800463/wangj/model_signal/test/Jupiter001/hml1regwjModel/%s' % (
                tradeDatestr)
        elif WJ_model_name == 'Hml2WjModel':
            wj_new_models_path = '/data/group/800463/wangj/model_signal/test/Jupiter001/hml2regwjModel/%s' % (
                tradeDatestr)
        if os.path.exists(wj_new_models_path + '/预测数据/'):
            Predict_file_csvs = os.listdir(wj_new_models_path + '/预测数据/')
            if len(Predict_file_csvs) > 0:
                csv_name = np.array(Predict_file_csvs)[
                    np.array(list(map(lambda x: '%s~%s' % (tradeDatestr, tradeDatestr) in x, Predict_file_csvs)))][0]
            else:
                csv_name = ''
            if len(csv_name) > 0:
                try:
                    WJ_model_local_prob = pd.read_csv(wj_new_models_path + '/预测数据/' + csv_name)
                except:
                    WJ_model_local_prob = pd.read_csv(wj_new_models_path + '/预测数据/' + csv_name, encoding='GBK')
            else:
                print(tradeDatestr, WJ_model_name, 'has no prediction file!!!!!!!!!!')
                WJ_model_local_prob = pd.DataFrame(index=this_date_local_sample_index,
                                                   columns=['prediction', 'pred_Reg', 'probability']).fillna(0).reset_index()
        else:
            print(tradeDatestr, WJ_model_name, 'has no prediction file!!!!!!!!!!')
            WJ_model_local_prob = pd.DataFrame(index=this_date_local_sample_index,
                                               columns=['prediction', 'pred_Reg', 'probability']).fillna(0).reset_index()

        WJ_model_local_prob['dt'] = WJ_model_local_prob['dt'].apply(lambda x: pd.Timestamp(x))
        WJ_model_local_label = \
            WJ_model_local_prob.set_index(['dt', 'Ticker']).rename(
                columns={'prediction': WJ_model_name, 'pred_Reg': WJ_model_name.split('Model')[0] + '_proba1'})[[
                WJ_model_name, WJ_model_name.split('Model')[0] + '_proba1']]
        this_date_wj_prob = pd.concat([this_date_wj_prob, WJ_model_local_label], axis=1)

    this_date_wj_prob['HmlWjModel'] = this_date_wj_prob['Hml0WjModel'].fillna(0) + \
                                      this_date_wj_prob['Hml1WjModel'].fillna(0) + \
                                      this_date_wj_prob['Hml2WjModel'].fillna(0)
    this_date_wj_prob['HmlWj_proba1'] = pd.concat([this_date_wj_prob['Hml0Wj_proba1'].fillna(0) + \
                                                   this_date_wj_prob['Hml1Wj_proba1'].fillna(0) + \
                                                   this_date_wj_prob['Hml2Wj_proba1'].fillna(0) ]).reindex(this_date_wj_prob.index).fillna(0)
    this_date_tot_prob = pd.concat([this_date_tot_prob, this_date_wj_prob[['TotalXgbRegWjModel', 'HmlWjModel','TotalXgbRegWj_proba1', 'HmlWj_proba1']] \
                                   .reindex(this_date_local_sample_index).fillna(0)], axis=1)
    this_date_local_only_prob = pd.concat(
        [this_date_local_only_prob,
         this_date_wj_prob[['TotalXgbRegWjModel', 'HmlWjModel','TotalXgbRegWj_proba1', 'HmlWj_proba1']].reindex(this_date_local_sample_index).fillna(0)],
        axis=1)
    # -----------------------------谢璐遥的模型------------------------------
    this_date_xly_prob = pd.DataFrame()

    for XLY_model_name in XLY_model_name_all:
        if 'Cla' in XLY_model_name and tradeDatestr < str_version_date_v1:
            XLY_model_local_label = (xly_total_prediction001[[XLY_model_name + '_proba']] > 0.5).rename(
                columns={XLY_model_name + '_proba': XLY_model_name})
        else:
            if tradeDatestr >= str_version_date_v1 and XLY_model_name in ['HighHBLrModel', 'HighHBXgbModel',
                                                                          'HighHMLLrModel',
                                                                          'HighPct5XgbClaModel', 'HighPct5XgbModel',
                                                                          'LowHBLrModel', 'LowHBXgbModel',
                                                                          'LowHMLLrModel',
                                                                          'LowPct5XgbClaModel', 'LowPct5XgbModel',
                                                                          'MedianHMLLrModel',
                                                                          'TotalLrModel', 'Type0XgbModel',
                                                                          'Type1XgbModel', 'Type2XgbModel']:
                XLY_model_local_label = pd.DataFrame(index=this_date_local_sample_index, columns=[XLY_model_name,XLY_model_name + '_proba']).fillna(0)  # .reset_index()
            else:
                XLY_model_local_label = (xly_total_prediction001[[XLY_model_name + '_proba']] >= 0).rename(
                    columns={XLY_model_name + '_proba': XLY_model_name}).astype(int)
                XLY_model_local_label = pd.concat(
                    [XLY_model_local_label, xly_total_prediction001[[XLY_model_name + '_proba']]], axis=1)
        XLY_model_local_label.rename(columns={XLY_model_name + '_proba': XLY_model_name.split('Model')[0] + '_proba1'}, inplace=True)
        this_date_xly_prob = pd.concat([this_date_xly_prob, XLY_model_local_label], axis=1)

    # this_date_xly_prob['HMLXgbModel'] = this_date_xly_prob['HighHMLXgbModel'].loc[hml2_index].reindex(this_date_sample_index).fillna(0) + \
    #                                     this_date_xly_prob['LowHMLXgbModel'].loc[hml0_index].reindex(this_date_sample_index).fillna(0) + \
    #                                     this_date_xly_prob['MedianHMLXgbModel'].loc[hml1_index].reindex(this_date_sample_index).fillna(0)
    this_date_xly_prob['HMLXgbModel'] = this_date_xly_prob['HighHMLXgbModel'].fillna(0) + \
                                        this_date_xly_prob['LowHMLXgbModel'].fillna(0) + \
                                        this_date_xly_prob['MedianHMLXgbModel'].fillna(0)
    this_date_xly_prob['HMLXgb_proba1'] = pd.concat([this_date_xly_prob['HighHMLXgb_proba1'].dropna(0),
                                                     this_date_xly_prob['LowHMLXgb_proba1'].dropna(0),
                                                     this_date_xly_prob['MedianHMLXgb_proba1'].dropna(0)]).reindex(this_date_xly_prob.index).fillna(0)

    this_date_tot_prob = pd.concat([this_date_tot_prob,
                                    this_date_xly_prob[['HMLXgbModel', 'TotalXgbModel','HMLXgb_proba1', 'TotalXgb_proba1']] \
                                   .reindex(this_date_local_sample_index)], axis=1)
    this_date_local_only_prob = pd.concat([this_date_local_only_prob, this_date_xly_prob[['HMLXgbModel',
                                                                                          'TotalXgbModel','HMLXgb_proba1', 'TotalXgb_proba1']].reindex(
        this_date_local_sample_index).fillna(0)], axis=1)
    if tradeDatestr >= str_version_date_v2:
        pred_path = '/data/group/800463/wangj/model_signal/Jupiter001/prod_v2/%s/%s_%s_europa_fac_20221116_new_daily_pred.csv' % (
        tradeDatestr, tradeDatestr, tradeDatestr)
        tmp_day_df = pd.read_csv(pred_path)
        tmp_day_df['dt'] = tmp_day_df['dt'].apply(lambda x: pd.Timestamp(x))
        tmp_day_df = tmp_day_df.set_index(['dt', 'Ticker'])[v2_model_name_pool+v2_model_pool_proba1]
        # this_date_v9_prob = pd.concat([this_date_v9_prob, tmp_day_df], axis=1)
        this_date_tot_prob = pd.concat([this_date_tot_prob,
                                        tmp_day_df.reindex(this_date_local_sample_index)], axis=1)
        this_date_local_only_prob = pd.concat([this_date_local_only_prob,
                                               tmp_day_df.reindex(this_date_local_sample_index)], axis=1)
    if tradeDatestr >= str_version_date_v3:
        pred_path = '/data/group/800463/wangj/model_signal/Jupiter001/prod_v3/%s/%s_%s_europa_fac_20230329_daily_pred.csv' % (
        tradeDatestr, tradeDatestr, tradeDatestr)
        tmp_day_df = pd.read_csv(pred_path)
        tmp_day_df.rename(columns = v3_rename_modeldict, inplace = True)
        tmp_day_df.rename(columns = v3_rename_probadict, inplace = True)
        tmp_day_df.rename(columns = v3_rename_modelpooldict, inplace = True)
        tmp_day_df.rename(columns = v3_rename_probapooldict, inplace = True)
        tmp_day_df['dt'] = tmp_day_df['dt'].apply(lambda x: pd.Timestamp(x))
        tmp_day_df = tmp_day_df.set_index(['dt', 'Ticker'])[v3_model_name_pool+v3_model_pool_proba1]
        # this_date_v9_prob = pd.concat([this_date_v9_prob, tmp_day_df], axis=1)
        this_date_tot_prob = pd.concat([this_date_tot_prob,
                                        tmp_day_df.reindex(this_date_local_sample_index)], axis=1)
        this_date_local_only_prob = pd.concat([this_date_local_only_prob,
                                               tmp_day_df.reindex(this_date_local_sample_index)], axis=1)

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

eur_model_track_v1comp = modeltrack_Tool('Europa', version_date_v2, '2023-05-08', savepath, eur_signal, v1_model_name_all, v1_model_name_all, 3)
tot_local_returnv1comp, tot_local_predict_summaryv1comp = eur_model_track_v1comp.cal_modeltrack_data(type='vote')
tot_local_returnv1comp_pool, tot_local_predict_summaryv1comp_pool = eur_model_track_v1comp.cal_modeltrack_data(type='all')

# eur_model_track_v1 = modeltrack_Tool('Europa', '2022-05-18', '2022-12-30', savepath, eur_signal, v1_model_name_all, v1_model_name_all,3) # year_start_date_h, '2023-02-10'
eur_model_track_v1 = modeltrack_Tool('Europa', year_start_date_h, '2023-05-07', savepath, eur_signal, v1_model_name_all, v1_model_name_all, 3)  # year_start_date_h, '2023-02-10'
tot_local_returnv1, tot_local_predict_summaryv1 = eur_model_track_v1.cal_modeltrack_data(type='vote')
tot_local_returnv1_pool, tot_local_predict_summaryv1_pool = eur_model_track_v1.cal_modeltrack_data(type='all')

eur_model_track_v3 = modeltrack_Tool('Europa', version_date_v3, end_date_h, savepath, eur_signal, v3_model_name_all, v3_model_name_pool, 4)
tot_local_returnv3, tot_local_predict_summaryv3 = eur_model_track_v3.cal_modeltrack_data(type='vote')
tot_local_returnv3_pool, tot_local_predict_summaryv3_pool = eur_model_track_v3.cal_modeltrack_data(type='all')


# 保存用于复盘的文件
eur_local = pd.concat([eur_model_track_v1.rawdata.copy(), eur_model_track_v2.rawdata.copy(), eur_model_track_v3.rawdata.copy()])
eur_trigger = eur_local.loc[Basic_samples_eur_need.index]

writer = pd.ExcelWriter('%sEuropa策略实盘与本地触发对比_%s_%s.xlsx' % (savepath, year_start_date, end_date_lw))
eur_trigger.reset_index().to_excel(writer, sheet_name='Europa实盘触发明细')
eur_local.reset_index().to_excel(writer, sheet_name='Europa本地触发明细')
writer.save()

# 写入excel
workbook = xlsxwriter.Workbook('%s%s模型跟踪v2_%s_%s.xlsx' % (savepath, eur_model_track_v1.strategy, year_start_date, end_date_lw))
generate_sheet(workbook, savepath, eur_model_track_v1.strategy, tot_local_predict_summaryv1, tot_local_returnv1, int(np.ceil(len(v1_model_name_all) / 2) + 2), '1')
generate_sheet(workbook, savepath, eur_model_track_v1.strategy, tot_local_predict_summaryv1_pool, tot_local_returnv1_pool, len(v1_model_name_all), '1modelpool')
generate_sheet(workbook, savepath, eur_model_track_v2.strategy, tot_local_predict_summaryv2, tot_local_returnv2, int(np.ceil(len(v2_model_name_all) / 2) + 2), '2')
generate_sheet(workbook, savepath, eur_model_track_v2.strategy, tot_local_predict_summaryv2_pool, tot_local_returnv2_pool, len(v2_model_name_pool), '2modelpool')
generate_sheet(workbook, savepath, eur_model_track_v1comp.strategy, tot_local_predict_summaryv1comp, tot_local_returnv1comp, int(np.ceil(len(v1_model_name_all) / 2) + 2), '1comp')
generate_sheet(workbook, savepath, eur_model_track_v1comp.strategy, tot_local_predict_summaryv1comp_pool, tot_local_returnv1comp_pool, len(v1_model_name_all), '1compmodelpool')
generate_sheet(workbook, savepath, eur_model_track_v3.strategy, tot_local_predict_summaryv3, tot_local_returnv3, int(np.ceil(len(v3_model_name_all) / 2) + 2), '3')
generate_sheet(workbook, savepath, eur_model_track_v3.strategy, tot_local_predict_summaryv3_pool, tot_local_returnv3_pool, len(v3_model_name_pool), '3modelpool')
generate_sheet(workbook, savepath, eur_model_track_v2comp.strategy, tot_local_predict_summaryv2comp, tot_local_returnv2comp, int(np.ceil(len(v2_model_name_all) / 2) + 2), '2comp')
generate_sheet(workbook, savepath, eur_model_track_v2comp.strategy, tot_local_predict_summaryv2comp_pool, tot_local_returnv2comp_pool, len(v2_model_name_pool), '2compmodelpool')

workbook.close()