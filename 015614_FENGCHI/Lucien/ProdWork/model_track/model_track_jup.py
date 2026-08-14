# coding: utf-8
# Author：fengchi863
# Date ：2023/5/22 16:57
from xquant.factordata import FactorData

s = FactorData()
import xlsxwriter
from ProdWork.model_track.config import *

version_date_v8 = '2022-02-22'  # v7-v8的时间
str_version_date_v8 = version_date_v8[:4] + version_date_v8[5:7] + version_date_v8[-2:]
str_ver8_before1 = s.tradingday(version_date_v8[:4] + version_date_v8[5:7] + version_date_v8[-2:], -2)[0]
version_date_v9 = '2023-02-13'
str_version_date_v9 = version_date_v9[:4] + version_date_v9[5:7] + version_date_v9[-2:]
str_ver9_before1 = s.tradingday(version_date_v9[:4] + version_date_v9[5:7] + version_date_v9[-2:], -2)[0]

# 先进行本地的Basic拼接和筛选
local_basic_file = pd.DataFrame()
for date in s.tradingday(year_start_date, end_date):
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
DJ_model_name_all = ['TotalDjClaModel', 'TotalDjRegModel',
                     'Hml0DjModel', 'Hml1DjModel', 'Hml2DjModel', 'RisePctLowDjModel', 'RisePctHighDjModel']
WJ_model_name_all = ['TotalLgbClaWjModel', 'Type0LgbClaWjModel', 'Type1LgbClaWjModel', 'Type2LgbClaWjModel',
                     'TotalXgbRegWjModel',
                     'TotalLrClaWjModel', 'Type0LrClaWjModel', 'Type1LrClaWjModel', 'Type2LrClaWjModel', \
                     'Type0WjModel', 'Type1WjModel', 'Type2WjModel', 'Hml0WjModel', 'Hml1WjModel', 'Hml2WjModel']
XLY_model_name_all = ['HighHBLrModel', 'HighHBXgbModel', 'HighHMLLrModel', 'HighHMLXgbModel',
                      'HighPct5XgbClaModel', 'HighPct5XgbModel', 'LowHBLrModel', 'LowHBXgbModel', 'LowHMLLrModel',
                      'LowHMLXgbModel', 'LowPct5XgbClaModel', 'LowPct5XgbModel', 'MedianHMLLrModel',
                      'MedianHMLXgbModel', 'TotalLrModel', 'TotalXgbModel', 'Type0LrModel', 'Type0XgbModel',
                      'Type1LrModel', 'Type1XgbModel', 'Type2LrModel', 'Type2XgbModel']
v8_model_name_all = ['TotalDjRegModel', 'HmlDjRegModel', 'RisePctDjModel', 'TotalXgbRegWjModel', 'HmlWjModel',
                     'TypeWjModel', 'TotalXgbModel', 'HMLXgbModel', 'TypeLrModel']
v8_model_name_proba1 = [x.split('Model')[0] + '_proba1' for x in v8_model_name_all]

v9_model_name_all = ['totalRegFSV8LrXlyModel', 'hmlRegFSV8XgbWjModel', 'hmlRegFSV8XgbXlyModel',
                     'totalRegO2ulFSV8XgbXbcModel', 'totalRegXgbXbcModel', 'totalRegFSV8XgbWjModel']
v9_model_name_pool = v9_model_name_all + ['totalRegFSRSXgbXlyModel',
                                          'totalRegXgbSkkModel',
                                          'totalRegFSV8LgbXbcModel',
                                          'totalRegFSV8LgbWjModel']
v9_model_name_proba1 = [x.split('Model')[0] + '_proba1' for x in v9_model_name_all]
v9_model_name_pool_proba1 = [x.split('Model')[0] + '_proba1' for x in v9_model_name_pool]

xly_total_prediction = pd.DataFrame()
for date in s.tradingday(year_start_date, end_date_lw):
    xly_new_models_path = '/data/group/800463/xiely/model_signal/%s/model_predict.pkl' % date
    this_date_xly_prob = pd.read_pickle(xly_new_models_path)
    this_date_xly_prob.rename(
        columns={'Hml0XgbModel_proba': 'LowHMLXgbModel_proba', 'Hml1XgbModel_proba': 'MedianHMLXgbModel_proba',
                 'Hml2XgbModel_proba': 'HighHMLXgbModel_proba', \
                 'Type0PMMLModel_proba': 'Type0LrModel_proba', 'Type1PMMLModel_proba': 'Type1LrModel_proba',
                 'Type2PMMLModel_proba': 'Type2LrModel_proba'}, inplace=True)
    xly_total_prediction = pd.concat([xly_total_prediction, this_date_xly_prob])

tot_local_prob = pd.DataFrame()
tot_local_only_prob = pd.DataFrame()

for tradeDatestr in s.tradingday(year_start_date, end_date_lw):
    print('JupiterN:%s' % tradeDatestr)
    this_date_sample_index = local_basic_file[(local_basic_file.reset_index()['dt'] == pd.Timestamp(tradeDatestr)).values].index
    hml0_index = local_basic_file[(local_basic_file.reset_index()['dt'] == pd.Timestamp(tradeDatestr)).values].query('hml_factor==0').index
    hml1_index = local_basic_file[(local_basic_file.reset_index()['dt'] == pd.Timestamp(tradeDatestr)).values].query('hml_factor==1').index
    hml2_index = local_basic_file[(local_basic_file.reset_index()['dt'] == pd.Timestamp(tradeDatestr)).values].query('hml_factor==2').index

    this_date_tot_prob = pd.DataFrame()  # 触发样本模型信号汇总
    this_date_local_only_prob = pd.DataFrame()  # 本地样本模型信号汇总
    # -----------------------------董坚的模型------------------------------
    this_date_dj_prob = pd.DataFrame()
    for DJ_model_name in DJ_model_name_all:
        # 核对模型的预测数据
        if DJ_model_name == 'TotalDjClaModel':
            if tradeDatestr <= str_ver8_before1:
                DJ_model_local_label = pd.read_hdf(
                    '/data/group/800463/dongj/model_signal/jupiter/model_output_everyday/%s_cla_v5/pred_label.h5' % tradeDatestr) \
                    .rename(columns={'pred_label': DJ_model_name})
                DJ_model_local_prob = pd.read_hdf(
                    '/data/group/800463/dongj/model_signal/jupiter/model_output_everyday/%s_cla_v5/pred_prob.h5' % tradeDatestr)\
                    .rename(columns={'pred_prob': DJ_model_name.split('Model')[0]+'_proba1'})
            else:
                DJ_model_local_label = pd.DataFrame(index=this_date_sample_index,
                                                    columns=[DJ_model_name]).fillna(0)
                DJ_model_local_prob = pd.DataFrame(index=this_date_sample_index,
                                                    columns=[DJ_model_name.split('Model')[0]+'_proba1']).fillna(0)
        elif DJ_model_name == 'TotalDjRegModel':
            DJ_model_local_label = pd.read_hdf(
                '/data/group/800463/dongj/model_signal/jupiter/model_output_everyday/%s_reg_v4/pred_label.h5' % tradeDatestr) \
                .rename(columns={'pred_label': DJ_model_name})
            DJ_model_local_prob = pd.read_hdf(
                '/data/group/800463/dongj/model_signal/jupiter/model_output_everyday/%s_reg_v4/pred_prob.h5' % tradeDatestr) \
                .rename(columns={'pred_prob': DJ_model_name.split('Model')[0] + '_proba1'})
        elif DJ_model_name == 'Hml0DjModel':
            DJ_model_local_label = pd.read_hdf(
                '/data/group/800463/dongj/model_signal/jupiter/model_output_everyday/%s_hml_low_v2/pred_label.h5' % tradeDatestr).rename(
                columns={'pred_label': DJ_model_name})
            DJ_model_local_prob = pd.read_hdf(
                '/data/group/800463/dongj/model_signal/jupiter/model_output_everyday/%s_hml_low_v2/pred_prob.h5' % tradeDatestr) \
                .rename(columns={'pred_prob': DJ_model_name.split('Model')[0] + '_proba1'})
        elif DJ_model_name == 'Hml1DjModel':
            DJ_model_local_label = pd.read_hdf(
                '/data/group/800463/dongj/model_signal/jupiter/model_output_everyday/%s_hml_except_v2/pred_label.h5' % tradeDatestr).rename(
                columns={'pred_label': DJ_model_name})
            DJ_model_local_prob = pd.read_hdf(
                '/data/group/800463/dongj/model_signal/jupiter/model_output_everyday/%s_hml_except_v2/pred_prob.h5' % tradeDatestr) \
                .rename(columns={'pred_prob': DJ_model_name.split('Model')[0] + '_proba1'})
        elif DJ_model_name == 'Hml2DjModel':
            DJ_model_local_label = pd.read_hdf(
                '/data/group/800463/dongj/model_signal/jupiter/model_output_everyday/%s_hml_high_v2/pred_label.h5' % tradeDatestr).rename(
                columns={'pred_label': DJ_model_name})
            DJ_model_local_prob = pd.read_hdf(
                '/data/group/800463/dongj/model_signal/jupiter/model_output_everyday/%s_hml_high_v2/pred_prob.h5' % tradeDatestr) \
                .rename(columns={'pred_prob': DJ_model_name.split('Model')[0] + '_proba1'})
        elif DJ_model_name == 'RisePctHighDjModel':
            DJ_model_local_label = pd.read_hdf(
                '/data/group/800463/dongj/model_signal/jupiter/model_output_everyday/%s_risePct_high_v3/pred_label.h5' % tradeDatestr).rename(
                columns={'pred_label': DJ_model_name})
            DJ_model_local_prob = pd.read_hdf(
                '/data/group/800463/dongj/model_signal/jupiter/model_output_everyday/%s_risePct_high_v3/pred_prob.h5' % tradeDatestr) \
                .rename(columns={'pred_prob': DJ_model_name.split('Model')[0] + '_proba1'})
        elif DJ_model_name == 'RisePctLowDjModel':
            DJ_model_local_label = pd.read_hdf(
                '/data/group/800463/dongj/model_signal/jupiter/model_output_everyday/%s_risePct_low_v3/pred_label.h5' % tradeDatestr).rename(
                columns={'pred_label': DJ_model_name})
            DJ_model_local_prob = pd.read_hdf(
                '/data/group/800463/dongj/model_signal/jupiter/model_output_everyday/%s_risePct_low_v3/pred_prob.h5' % tradeDatestr) \
                .rename(columns={'pred_prob': DJ_model_name.split('Model')[0] + '_proba1'})
        DJ_model_local_label = pd.concat([DJ_model_local_label, DJ_model_local_prob],axis=1)
        this_date_dj_prob = pd.concat([this_date_dj_prob, DJ_model_local_label], axis=1)

    this_date_dj_prob['HmlDjRegModel'] = this_date_dj_prob['Hml0DjModel'].fillna(0) + \
                                         this_date_dj_prob['Hml1DjModel'].fillna(0) + \
                                         this_date_dj_prob['Hml2DjModel'].fillna(0)
    this_date_dj_prob['HmlDjReg_proba1'] = pd.concat([this_date_dj_prob['Hml0Dj_proba1'].dropna(), this_date_dj_prob['Hml1Dj_proba1'].dropna(),this_date_dj_prob['Hml2Dj_proba1'].dropna()]).reindex(this_date_dj_prob.index).fillna(0)
    this_date_dj_prob['RisePctDjModel'] = this_date_dj_prob['RisePctLowDjModel'].fillna(0) + \
                                          this_date_dj_prob['RisePctHighDjModel'].fillna(0)
    this_date_dj_prob['RisePctDj_proba1'] = pd.concat([this_date_dj_prob['RisePctLowDj_proba1'].dropna(),
                                          this_date_dj_prob['RisePctHighDj_proba1'].dropna()]).reindex(this_date_dj_prob.index).fillna(0)
    this_date_tot_prob = pd.concat([this_date_tot_prob, this_date_dj_prob[
        ['TotalDjClaModel', 'TotalDjRegModel', 'HmlDjRegModel', 'RisePctDjModel','TotalDjCla_proba1', 'TotalDjReg_proba1', 'HmlDjReg_proba1', 'RisePctDj_proba1']] \
                                   .reindex(this_date_sample_index)], axis=1)
    this_date_local_only_prob = pd.concat(
        [this_date_local_only_prob,
         this_date_dj_prob[['TotalDjClaModel', 'TotalDjRegModel', 'HmlDjRegModel', 'RisePctDjModel','TotalDjCla_proba1', 'TotalDjReg_proba1', 'HmlDjReg_proba1', 'RisePctDj_proba1']].reindex(
             this_date_sample_index).fillna(0)], axis=1)

    # -----------------------------王敬的模型------------------------------
    this_date_wj_prob = pd.DataFrame()
    for WJ_model_name in WJ_model_name_all:
        # 核对模型的预测数据
        if WJ_model_name == 'TotalLgbClaWjModel':
            wj_new_models_path = '/data/group/800463/wangj/model_signal/Jupiter/allLgbClaModel/%s' % tradeDatestr
        elif WJ_model_name == 'Type0LgbClaWjModel':
            wj_new_models_path = '/data/group/800463/wangj/model_signal/Jupiter/type0LgbClaModel/%s' % tradeDatestr
        elif WJ_model_name == 'Type1LgbClaWjModel':
            wj_new_models_path = '/data/group/800463/wangj/model_signal/Jupiter/type1LgbClaModel/%s' % tradeDatestr
        elif WJ_model_name == 'Type2LgbClaWjModel':
            wj_new_models_path = '/data/group/800463/wangj/model_signal/Jupiter/type2LgbClaModel/%s' % tradeDatestr
        elif WJ_model_name == 'Type0LrClaWjModel':
            wj_new_models_path = '/data/group/800463/wangj/model_signal/Jupiter/type0LrClaModel/%s' % tradeDatestr
        elif WJ_model_name == 'Type1LrClaWjModel':
            wj_new_models_path = '/data/group/800463/wangj/model_signal/Jupiter/type1LrClaModel/%s' % tradeDatestr
        elif WJ_model_name == 'Type2LrClaWjModel':
            wj_new_models_path = '/data/group/800463/wangj/model_signal/Jupiter/type2LrClaModel/%s' % tradeDatestr
        elif WJ_model_name == 'TotalXgbRegWjModel':
            wj_new_models_path = '/data/group/800463/wangj/model_signal/Jupiter/allregwjModel/%s' % tradeDatestr
        elif WJ_model_name == 'TotalLrClaWjModel':
            wj_new_models_path = '/data/group/800463/wangj/model_signal/Jupiter/allLrClaModel/%s' % tradeDatestr
        elif WJ_model_name == 'Type0WjModel':
            wj_new_models_path = '/data/group/800463/wangj/model_signal/Jupiter/type0regwjModel/%s' % tradeDatestr
        elif WJ_model_name == 'Type1WjModel':
            wj_new_models_path = '/data/group/800463/wangj/model_signal/Jupiter/type1regwjModel/%s' % tradeDatestr
        elif WJ_model_name == 'Type2WjModel':
            wj_new_models_path = '/data/group/800463/wangj/model_signal/Jupiter/type2regwjModel/%s' % tradeDatestr
        elif WJ_model_name == 'Hml0WjModel':
            wj_new_models_path = '/data/group/800463/wangj/model_signal/Jupiter/hml0regwjModel/%s' % tradeDatestr
        elif WJ_model_name == 'Hml1WjModel':
            wj_new_models_path = '/data/group/800463/wangj/model_signal/Jupiter/hml1regwjModel/%s' % tradeDatestr
        elif WJ_model_name == 'Hml2WjModel':
            wj_new_models_path = '/data/group/800463/wangj/model_signal/Jupiter/hml2regwjModel/%s' % tradeDatestr
        if os.path.exists(wj_new_models_path + '/预测数据/'):
            Predict_file_csvs = os.listdir(wj_new_models_path + '/预测数据/')
            if len(Predict_file_csvs) > 0:
                csv_name = np.array(Predict_file_csvs)[np.array(list(map(lambda x: '%s~%s' % (tradeDatestr, tradeDatestr) in x, Predict_file_csvs)))][0]
            else:
                csv_name = ''
            if len(csv_name) > 0:
                try:
                    WJ_model_local_prob = pd.read_csv(wj_new_models_path + '/预测数据/' + csv_name)
                except:
                    WJ_model_local_prob = pd.read_csv(wj_new_models_path + '/预测数据/' + csv_name, encoding='GBK')
            else:
                print(tradeDatestr, WJ_model_name, 'has no prediction file!!!!!!!!!!')
                WJ_model_local_prob = pd.DataFrame(index=this_date_sample_index,
                                                   columns=['prediction', 'pred_Reg']).fillna(0).reset_index()#, 'probability'
        else:
            print(tradeDatestr, WJ_model_name, 'has no prediction file!!!!!!!!!!')
            WJ_model_local_prob = pd.DataFrame(index=this_date_sample_index, columns=['prediction', 'pred_Reg']).fillna(0).reset_index()#, 'probability'

        WJ_model_local_prob['dt'] = WJ_model_local_prob['dt'].apply(lambda x: pd.Timestamp(x))
        WJ_model_local_label = \
            WJ_model_local_prob.set_index(['dt', 'Ticker']).rename(columns={'prediction': WJ_model_name, 'pred_Reg': WJ_model_name.split('Model')[0]+'_proba1', 'probability': WJ_model_name.split('Model')[0]+'_proba1'})[[
                WJ_model_name,WJ_model_name.split('Model')[0]+'_proba1']]
        this_date_wj_prob = pd.concat([this_date_wj_prob, WJ_model_local_label], axis=1)
    this_date_wj_prob['TypeLgbClaWjModel'] = this_date_wj_prob['Type0LgbClaWjModel'].fillna(0) + \
                                             this_date_wj_prob['Type1LgbClaWjModel'].fillna(0) + \
                                             this_date_wj_prob['Type2LgbClaWjModel'].fillna(0)
    # this_date_wj_prob['TypeLgbClaWj_proba1'] = pd.concat([this_date_wj_prob['Type0LgbClaWj_proba1'].dropna(),
    #                                                      this_date_wj_prob['Type1LgbClaWj_proba1'].dropna(),
    #                                                      this_date_wj_prob['Type2LgbClaWj_proba1'].dropna()]).reindex(this_date_wj_prob.index).fillna(0)
    this_date_wj_prob['TypeLrClaWjModel'] = this_date_wj_prob['Type0LrClaWjModel'].fillna(0) + \
                                            this_date_wj_prob['Type1LrClaWjModel'].fillna(0) + \
                                            this_date_wj_prob['Type2LrClaWjModel'].fillna(0)
    # this_date_wj_prob['TypeLrClaWj_proba1'] = pd.concat([this_date_wj_prob['Type0LrClaWj_proba1'].dropna(),
    #                                                 this_date_wj_prob['Type1LrClaWj_proba1'].dropna(),
    #                                                 this_date_wj_prob['Type2LrClaWj_proba1'].dropna()]).reindex(
    #     this_date_wj_prob.index).fillna(0)
    this_date_wj_prob['TypeWjModel'] = this_date_wj_prob['Type0WjModel'].fillna(0) + \
                                       this_date_wj_prob['Type1WjModel'].fillna(0) + \
                                       this_date_wj_prob['Type2WjModel'].fillna(0)
    this_date_wj_prob['TypeWj_proba1'] = pd.concat([this_date_wj_prob['Type0Wj_proba1'].fillna(0) + \
                                                    this_date_wj_prob['Type1Wj_proba1'].fillna(0) + \
                                                    this_date_wj_prob['Type2Wj_proba1'].fillna(0) ]).reindex(
        this_date_wj_prob.index).fillna(0)
    # this_date_wj_prob['TypeWj_proba1'] = pd.concat([this_date_wj_prob['Type0Wj_proba1'].dropna(),
    #                                    this_date_wj_prob['Type1Wj_proba1'].dropna(),
    #                                    this_date_wj_prob['Type2Wj_proba1'].dropna()]).reindex(this_date_wj_prob.index).fillna(0)
    this_date_wj_prob['HmlWjModel'] = this_date_wj_prob['Hml0WjModel'].fillna(0) + \
                                      this_date_wj_prob['Hml1WjModel'].fillna(0) + \
                                      this_date_wj_prob['Hml2WjModel'].fillna(0)
    this_date_wj_prob['HmlWj_proba1'] =pd.concat([this_date_wj_prob['Hml0Wj_proba1'].fillna(0)+
                                                    this_date_wj_prob['Hml1Wj_proba1'].fillna(0)+
                                                    this_date_wj_prob['Hml2Wj_proba1'].fillna(0)]).reindex(this_date_wj_prob.index).fillna(0)
    # this_date_wj_prob['HmlWj_proba1'] = pd.concat([this_date_wj_prob['Hml0Wj_proba1'].dropna(),
    #                                                 this_date_wj_prob['Hml1Wj_proba1'].dropna(),
    #                                                 this_date_wj_prob['Hml2Wj_proba1'].dropna()]).reindex(this_date_wj_prob.index).fillna(0)
    this_date_tot_prob = pd.concat(
        [this_date_tot_prob, this_date_wj_prob[['TotalLgbClaWjModel', 'TotalXgbRegWjModel', 'TotalLrClaWjModel',
                                                'TypeLgbClaWjModel', 'TypeLrClaWjModel', 'TypeWjModel',
                                                'HmlWjModel','TotalXgbRegWj_proba1','TypeWj_proba1','HmlWj_proba1']] \
            .reindex(this_date_sample_index).fillna(0)], axis=1)
    this_date_local_only_prob = pd.concat(
        [this_date_local_only_prob,
         this_date_wj_prob[['TotalLgbClaWjModel', 'TotalXgbRegWjModel', 'TotalLrClaWjModel',
                            'TypeLgbClaWjModel', 'TypeLrClaWjModel', 'TypeWjModel', 'HmlWjModel','TotalXgbRegWj_proba1','TypeWj_proba1','HmlWj_proba1']].reindex(
             this_date_sample_index).fillna(0)], axis=1)
    # -----------------------------谢璐遥的模型------------------------------
    this_date_xly_prob = pd.DataFrame()

    for XLY_model_name in XLY_model_name_all:
        if 'Cla' in XLY_model_name and tradeDatestr <= str_ver8_before1:
            XLY_model_local_label = (xly_total_prediction[[XLY_model_name + '_proba']] >= 0.5).rename(
                columns={XLY_model_name + '_proba': XLY_model_name})
        else:
            if tradeDatestr > str_ver8_before1 and XLY_model_name in ['HighHBLrModel', 'HighHBXgbModel',
                                                                      'HighHMLLrModel',
                                                                      'HighPct5XgbClaModel', 'HighPct5XgbModel',
                                                                      'LowHBLrModel', 'LowHBXgbModel',
                                                                      'LowHMLLrModel',
                                                                      'LowPct5XgbClaModel', 'LowPct5XgbModel',
                                                                      'MedianHMLLrModel',
                                                                      'TotalLrModel', 'Type0XgbModel',
                                                                      'Type1XgbModel', 'Type2XgbModel']:
                XLY_model_local_label = pd.DataFrame(index=this_date_sample_index, columns=[XLY_model_name,XLY_model_name + '_proba']).fillna(0)
            else:
                XLY_model_local_label = (xly_total_prediction[[XLY_model_name + '_proba']] >= 0).rename(columns={XLY_model_name + '_proba': XLY_model_name}).astype(int)
                XLY_model_local_label = pd.concat([XLY_model_local_label,xly_total_prediction[[XLY_model_name + '_proba']]],axis=1)
        XLY_model_local_label.rename(columns={XLY_model_name + '_proba': XLY_model_name.split('Model')[0]+'_proba1'}, inplace=True)
        this_date_xly_prob = pd.concat([this_date_xly_prob, XLY_model_local_label], axis=1)
    this_date_xly_prob['HBLrModel'] = this_date_xly_prob['HighHBLrModel'].fillna(0) + \
                                      this_date_xly_prob['LowHBLrModel'].fillna(0)
    this_date_xly_prob['HBXgbModel'] = this_date_xly_prob['HighHBXgbModel'].fillna(0) + \
                                       this_date_xly_prob['LowHBXgbModel'].fillna(0)
    this_date_xly_prob['HMLLrModel'] = this_date_xly_prob['HighHMLLrModel'].fillna(0) + \
                                       this_date_xly_prob['LowHMLLrModel'].fillna(0) + \
                                       this_date_xly_prob['MedianHMLLrModel'].fillna(0)
    this_date_xly_prob['HMLXgbModel'] = this_date_xly_prob['HighHMLXgbModel'].fillna(0) + \
                                        this_date_xly_prob['LowHMLXgbModel'].fillna(0) + \
                                        this_date_xly_prob['MedianHMLXgbModel'].fillna(0)
    this_date_xly_prob['HMLXgb_proba1'] = pd.concat([this_date_xly_prob['HighHMLXgb_proba1'].dropna(0),
                                        this_date_xly_prob['LowHMLXgb_proba1'].dropna(0),
                                        this_date_xly_prob['MedianHMLXgb_proba1'].dropna(0)]).reindex(this_date_xly_prob.index).fillna(0)
    this_date_xly_prob['Pct5XgbClaModel'] = this_date_xly_prob['HighPct5XgbClaModel'].fillna(0) + \
                                            this_date_xly_prob['LowPct5XgbClaModel'].fillna(0)
    this_date_xly_prob['Pct5XgbModel'] = this_date_xly_prob['HighPct5XgbModel'].fillna(0) + \
                                         this_date_xly_prob['LowPct5XgbModel'].fillna(0)
    this_date_xly_prob['TypeLrModel'] = this_date_xly_prob['Type0LrModel'].fillna(0) + \
                                        this_date_xly_prob['Type1LrModel'].fillna(0) + \
                                        this_date_xly_prob['Type2LrModel'].fillna(0)
    this_date_xly_prob['TypeLr_proba1'] = pd.concat([this_date_xly_prob['Type0Lr_proba1'].dropna(),
                                        this_date_xly_prob['Type1Lr_proba1'].dropna(),
                                        this_date_xly_prob['Type2Lr_proba1'].dropna()]).reindex(this_date_xly_prob.index).fillna(0)
    this_date_xly_prob['TypeXgbModel'] = this_date_xly_prob['Type0XgbModel'].fillna(0) + \
                                         this_date_xly_prob['Type1XgbModel'].fillna(0) + \
                                         this_date_xly_prob['Type2XgbModel'].fillna(0)
    this_date_tot_prob = pd.concat([this_date_tot_prob,
                                    this_date_xly_prob[['HBLrModel', 'HBXgbModel', 'HMLLrModel', 'HMLXgbModel',
                                                        'Pct5XgbClaModel', 'Pct5XgbModel',
                                                        'TypeLrModel', 'TypeXgbModel', 'TotalLrModel',
                                                        'TotalXgbModel','TotalXgb_proba1','HMLXgb_proba1','TypeLr_proba1']] \
                                   .reindex(this_date_sample_index)], axis=1)
    this_date_local_only_prob = pd.concat(
        [this_date_local_only_prob, this_date_xly_prob[['HBLrModel', 'HBXgbModel', 'HMLLrModel', 'HMLXgbModel',
                                                        'Pct5XgbClaModel', 'Pct5XgbModel',
                                                        'TypeLrModel', 'TypeXgbModel', 'TotalLrModel',
                                                        'TotalXgbModel','TotalXgb_proba1','HMLXgb_proba1','TypeLr_proba1']].reindex(
            this_date_sample_index).fillna(0)], axis=1)

    # 第二种信号存储方式，以后都改为这种
    if tradeDatestr >= str_version_date_v9:
        pred_path = '/data/group/800463/wangj/model_signal/Jupiter/prod_v9/%s/%s_%s_jupiter_fac_20221220_daily_pred.csv' % (tradeDatestr, tradeDatestr, tradeDatestr)
        tmp_day_df = pd.read_csv(pred_path)
        tmp_day_df['dt'] = tmp_day_df['dt'].apply(lambda x: pd.Timestamp(x))
        tmp_day_df = tmp_day_df.set_index(['dt', 'Ticker'])[v9_model_name_pool + v9_model_name_pool_proba1]
        # this_date_v9_prob = pd.concat([this_date_v9_prob, tmp_day_df], axis=1)
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
jup_model_track_v9 = modeltrack_Tool('jupiter', version_date_v9, end_date_h, savepath, jup_signal, v9_model_name_all, v9_model_name_pool, 5)

tot_local_returnv9, tot_local_predict_summaryv9 = jup_model_track_v9.cal_modeltrack_data(type='vote') # 计算投票信息 第一个sheet
tot_local_returnv9_pool, tot_local_predict_summaryv9_pool = jup_model_track_v9.cal_modeltrack_data(type='all')  # 计算子模型信息 第二个sheet

# old 与 new 一起跑，谁的更好
jup_model_track_v8comp = modeltrack_Tool('jupiter', version_date_v9, end_date_h, savepath, jup_signal, v8_model_name_all, v8_model_name_all, 7)
tot_local_returnv8comp, tot_local_predict_summaryv8comp = jup_model_track_v8comp.cal_modeltrack_data(type='vote')
tot_local_returnv8comp_pool, tot_local_predict_summaryv8comp_pool = jup_model_track_v8comp.cal_modeltrack_data(type='all')

# 旧的实盘期间的表现
# jup_model_track_v8 = modeltrack_Tool('jupiter', year_start_date_h, '2022-12-30', savepath, jup_signal, v8_model_name_all, v8_model_name_all,7)
jup_model_track_v8 = modeltrack_Tool('jupiter', year_start_date_h, end_date_h, savepath, jup_signal, v8_model_name_all, v8_model_name_all, 7)
tot_local_returnv8, tot_local_predict_summaryv8 = jup_model_track_v8.cal_modeltrack_data(type='vote')
tot_local_returnv8_pool, tot_local_predict_summaryv8_pool = jup_model_track_v8.cal_modeltrack_data(type='all')

# 计算各个版本各个模型本地信号的评价
jupiterN_local = pd.concat([jup_model_track_v8.rawdata.copy(), jup_model_track_v9.rawdata.copy()])
jupiterN_trigger = jupiterN_local.loc[Basic_samples_non_zt_need.index]

writer = pd.ExcelWriter('%sJupiter策略实盘与本地触发对比_%s_%s.xlsx' % (savepath, year_start_date, end_date_lw))
jupiterN_trigger.reset_index().to_excel(writer, sheet_name='jupiterN实盘触发明细')    # 复盘用到
jupiterN_local.reset_index().to_excel(writer, sheet_name='jupiterN本地触发明细')
writer.save()

# 写入excel
workbook = xlsxwriter.Workbook('%s%s模型跟踪v2_%s_%s.xlsx' % (savepath, jup_model_track_v9.strategy, year_start_date, end_date_lw))

generate_sheet(workbook, savepath, jup_model_track_v8.strategy, tot_local_predict_summaryv8, tot_local_returnv8, int(np.ceil(len(v8_model_name_all) / 2) + 2), '8')
generate_sheet(workbook, savepath, jup_model_track_v8.strategy, tot_local_predict_summaryv8_pool, tot_local_returnv8_pool, len(v8_model_name_all), '8modelpool')
generate_sheet(workbook, savepath, jup_model_track_v9.strategy, tot_local_predict_summaryv9, tot_local_returnv9,int(np.ceil(len(v9_model_name_all)/2)+2), '9')
generate_sheet(workbook, savepath, jup_model_track_v9.strategy, tot_local_predict_summaryv9_pool, tot_local_returnv9_pool, len(v9_model_name_pool), '9modelpool')
generate_sheet(workbook, savepath, jup_model_track_v8comp.strategy, tot_local_predict_summaryv8comp, tot_local_returnv8comp, int(np.ceil(len(v8_model_name_all) / 2) + 2), '8comp')
generate_sheet(workbook, savepath, jup_model_track_v8comp.strategy, tot_local_predict_summaryv8comp_pool, tot_local_returnv8comp_pool, len(v8_model_name_all), '8compmodelpool')
workbook.close()