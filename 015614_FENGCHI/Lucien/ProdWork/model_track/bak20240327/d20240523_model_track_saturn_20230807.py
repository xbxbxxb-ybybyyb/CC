# coding: utf-8
# Author：fengchi863
# Date ：2023/8/7 11:18
from xquant.factordata import FactorData

s = FactorData()
import matplotlib.pyplot as plt
import xlsxwriter
from ProdWork.model_track.modeltrack_Tool_v2 import *
from ProdWork.model_track.config import *

#####################################-----------3、生成saturn-----------#####################################
# saturn_triggered = pd.read_excel('/data/group/800463/日内强势股/log_parse/因子耗时/实盘触发项目二标签汇总_%s.xlsx' % end_date_h)
version_sat_date = '2021-06-21'
sat_local_basic_file = pd.read_hdf('/data/group/800463/project/project2_prod/daily_data/Basic/Basic_closed_hf_finish.h5').sort_index().loc[pd.Timestamp(year_start_date_h):pd.Timestamp(end_date_lw), slice(None)]  # 一定要sortindex

# v5版本的Saturn
DJ_model_name_all = ['openPctHighDjClaModel', 'openPctLowDjClaModel', 'totalDjClaModel',
                     'saturn931OpenPctHighDjModel', 'saturn931OpenPctLowDjModel', \
                     'saturn931Pat3DjModel', 'saturn931Pat4DjModel', 'saturn931Ret2oHighDjModel',
                     'saturn931Ret2oLowDjModel', 'saturn931TotalDjModel']
WJ_model_name_all = ['openPctHighWjClaModel', 'openPctLowWjClaModel', 'totalWjClaModel',
                     'saturn931OpenPctHighWjModel', 'saturn931OpenPctLowWjModel', \
                     'saturn931Pct5HighWjModel', 'saturn931Pct5LowWjModel', 'saturn931TotalWjModel']
XLY_model_name_all = ['Pat34XgbModel', 'saturn931Pat34XlyModel', 'saturn931Ret2OXlyModel']

saturn_model_rename_dict = {'openPctHighWjClaModel': 'highopenClaModel',
                            'openPctLowWjClaModel': 'lowopenClaModel',
                            'totalWjClaModel': 'allClaModel',
                            'openPctHighDjClaModel': '930_openpct_high_v2',
                            'openPctLowDjClaModel': '930_openpct_low_v2',
                            'totalDjClaModel': '930_cla_v2',
                            'Pat34XgbModel': 'Saturn930Pat34XgbModel',
                            'saturn931OpenPctHighWjModel': 'highopenregModel',
                            'saturn931OpenPctLowWjModel': 'lowopenregModel',
                            'saturn931Pct5HighWjModel': 'highpct5regModel',
                            'saturn931Pct5LowWjModel': 'lowpct5regModel',
                            'saturn931TotalWjModel': 'allregwjModel',
                            'saturn931OpenPctHighDjModel': '931_openpct_high_v2',
                            'saturn931OpenPctLowDjModel': '931_openpct_low_v2',
                            'saturn931Pat3DjModel': '931_pat_23_v2',
                            'saturn931Pat4DjModel': '931_pat_14_v2',
                            'saturn931Ret2oHighDjModel': '931_ret2o_high_v2',
                            'saturn931Ret2oLowDjModel': '931_ret2o_low_v2',
                            'saturn931TotalDjModel': '931_reg_v2',
                            'Saturn931Pat34XgbModel': 'Saturn931Pat34XgbModel',
                            'Saturn931Ret2OPMMLModel': 'Saturn931Ret2OPMMLModel',
                            }

wj_prob = pd.DataFrame()
dj_prob = pd.DataFrame()
xly_prob = pd.DataFrame()
v6_prob = pd.DataFrame()
v5_pj2_start_date = '20220303'
v6_pj2_start_date = '20230626'

v6_model_name_all = ['totalRegFSV8NnXbcModel',
                      'totalRegNnXbcModel',
                      'totalRegFSV11XgbXlyModel',
                      'totalRegFSV11LgbWjModel',
                      'totalRegFSRSXgbSkkModel',
                      'totalRegFSRSXgbFcModel']

saturn_model_name_all = ['openPctDjClaModel', 'openPctWjClaModel', 'totalDjClaModel', 'totalWjClaModel',
                         'Pat34XgbModel', 'saturn931OpenPctDjModel', 'saturn931OpenPctWjModel',
                         'saturn931Pat34DjModel', 'saturn931Pat34XlyModel', 'saturn931Ret2oDjModel',
                         'saturn931Ret2OXlyModel', 'saturn931Pct5WjModel', 'saturn931TotalDjModel',
                         'saturn931TotalWjModel',
                         ]

v6_model_name_proba1 = [x.split('Model')[0] + '_proba1' for x in v6_model_name_all]
v6_model_name_pool = v6_model_name_all + ['totalRegFSRSXgbXbcModel', 'totalRegXgbSkkModel', 'totalRegFSV8XgbWjModel', 'totalRegXgbFcModel', 'totalRegFSV10Dnn2ZwhModel']
v6_model_pool_proba1 = [x.split('Model')[0] + '_proba1' for x in v6_model_name_pool]
v6_rename_modeldict = dict(zip(v6_model_name_all,['saturn931v6'+x for x in v6_model_name_all]))
v6_rename_probadict = dict(zip(v6_model_name_proba1,['saturn931v6'+x for x in v6_model_name_proba1]))
v6_rename_modelpooldict = dict(zip(v6_model_name_pool, ['saturn931v6' + x for x in v6_model_name_pool]))
v6_rename_probapooldict = dict(zip(v6_model_pool_proba1, ['saturn931v6' + x for x in v6_model_pool_proba1]))

v6_model_name_all, v6_model_name_proba1 = list(v6_rename_modeldict.values()), list(v6_rename_probadict.values())
v6_model_name_pool, v6_model_pool_proba1 = list(v6_rename_modelpooldict.values()), list(v6_rename_probapooldict.values())

for tradeDatestr in s.tradingday(year_start_date, end_date_lw):
    print('saturn: %s' % tradeDatestr)
    this_date_sat_sample_index = sat_local_basic_file[(sat_local_basic_file.reset_index()['dt'] == pd.Timestamp(tradeDatestr)).values].index
    this_date_wj_prob = pd.DataFrame()
    this_date_dj_prob = pd.DataFrame()
    this_date_xly_prob = pd.DataFrame()
    this_date_v6_prob = pd.DataFrame()
    if tradeDatestr >= '20210615':
        for WJ_model_name in WJ_model_name_all:
            print(WJ_model_name)
            if tradeDatestr >= v5_pj2_start_date and WJ_model_name.find('931') < 0:
                print(tradeDatestr, WJ_model_name, 'has no prediction file!!!!!!!!!!')
                WJ_model_local_prob = pd.DataFrame(index=this_date_sat_sample_index,
                                                   columns=['prediction', 'pred_Reg', 'probability']).fillna(0).reset_index()
            else:
                # if tradeDatestr == '20240228' and WJ_model_name.find('931Pct5') > 0:
                #     print(1)
                if WJ_model_name.find('931') > 0:
                    wj_new_models_path = '/data/group/800463/wangj/model_signal/Saturn/S1/%s/%s' % (saturn_model_rename_dict[WJ_model_name], tradeDatestr)
                else:
                    wj_new_models_path = '/data/group/800463/wangj/model_signal/Saturn/S0/%s/%s' % (saturn_model_rename_dict[WJ_model_name], tradeDatestr)
                # 核对模型的预测数据

                if os.path.exists(wj_new_models_path + '/预测数据/'):
                    Predict_file_csvs = os.listdir(wj_new_models_path + '/预测数据/')
                    csv_name = np.array(Predict_file_csvs)[np.array(
                        list(map(lambda x: '%s~%s' % (tradeDatestr, tradeDatestr) in x, Predict_file_csvs)))][0]
                    try:
                        WJ_model_local_prob = pd.read_csv(wj_new_models_path + '/预测数据/' + csv_name)
                    except:
                        WJ_model_local_prob = pd.read_csv(wj_new_models_path + '/预测数据/' + csv_name, encoding='GBK')
                else:
                    print(tradeDatestr, WJ_model_name, 'has no prediction file!!!!!!!!!!')
                    if WJ_model_name.find('931Pct5') > 0:
                        WJ_model_local_prob = pd.DataFrame(index=this_date_sat_sample_index,
                                                           columns=['prediction', 'pred_Reg', 'probability']).reset_index()
                    else:
                        WJ_model_local_prob = pd.DataFrame(index=this_date_sat_sample_index,
                                                           columns=['prediction', 'pred_Reg', 'probability']).fillna(0).reset_index()

            WJ_model_local_prob['dt'] = [pd.Timestamp(str(x)) for x in WJ_model_local_prob.dt.tolist()]
            WJ_model_local_label = \
            WJ_model_local_prob.set_index(['dt', 'Ticker']).rename(columns={'prediction': WJ_model_name,'pred_Reg':WJ_model_name.split('Model')[0]+'_proba1'})[
                [WJ_model_name,WJ_model_name.split('Model')[0]+'_proba1']]
            this_date_wj_prob = pd.concat([this_date_wj_prob, WJ_model_local_label], axis=1).reindex(this_date_sat_sample_index)

        for DJ_model_name in DJ_model_name_all:
            print(DJ_model_name)

            dj_model_path = '/data/group/800463/dongj/model_signal/saturn/model_output_everyday/%s_%s/pred_label.h5' % (
            tradeDatestr, saturn_model_rename_dict[DJ_model_name])
            dj_prob_path = '/data/group/800463/dongj/model_signal/saturn/model_output_everyday/%s_%s/pred_prob.h5' % (
                tradeDatestr, saturn_model_rename_dict[DJ_model_name])
            if tradeDatestr >= v5_pj2_start_date and DJ_model_name.find('931') < 0:
                print(tradeDatestr, DJ_model_name, ' has no prediction!')
                DJ_model_local_prob = pd.DataFrame(index=this_date_sat_sample_index,
                                                   columns=[DJ_model_name,DJ_model_name.split('Model')[0]+'_proba1']).fillna(0)
            else:
                print(tradeDatestr, DJ_model_name)
                DJ_model_local_prob = pd.read_hdf(dj_model_path)
                DJ_model_local_label = DJ_model_local_prob.rename(
                    columns={'pred_label': DJ_model_name})
                DJ_model_local_prob = pd.read_hdf(dj_prob_path) \
                    .rename(columns={'pred_prob': DJ_model_name.split('Model')[0] + '_proba1'})
                DJ_model_local_prob = pd.concat([DJ_model_local_label, DJ_model_local_prob], axis=1)
            this_date_dj_prob = pd.concat([this_date_dj_prob, DJ_model_local_prob], axis=1).reindex(this_date_sat_sample_index)

        for XLY_model_name in XLY_model_name_all:
            print(XLY_model_name)
            if XLY_model_name.find('931') > 0:
                if tradeDatestr >= '20210906':
                    xly_new_models_path = '/data/group/800463/xiely/model_signal/%s_saturn_931/model_predict.pkl' % tradeDatestr
                else:
                    xly_new_models_path = '/data/user/013551/xly_dailyModelPredict_v2/%s_saturn_931/model_predict.pkl' % tradeDatestr
                xly_model_local_prob = pd.read_pickle(xly_new_models_path)
                if tradeDatestr >= v5_pj2_start_date:
                    xly_model_local_prob.rename(columns={'S1Pat34XlyModel_pred': 'saturn931Pat34XlyModel_pred',
                                                         'S1Ret2OXlyModel_pred': 'saturn931Ret2OXlyModel_pred'},
                                                inplace=True)
                else:
                    xly_model_local_prob.rename(
                        columns={'Saturn931Pat34XgbModel_pred': 'saturn931Pat34XlyModel_pred',
                                 'Saturn931Ret2OPMMLModel_pred': 'saturn931Ret2OXlyModel_pred'},
                        inplace=True)
                addcols = list(filter(lambda x: x.find(XLY_model_name[9:12])>=0 and x.find('proba')>=0,xly_model_local_prob.columns.tolist()))
                xly_model_local_prob = \
                xly_model_local_prob.rename(columns={XLY_model_name + '_pred': XLY_model_name})[[XLY_model_name]+addcols]
            else:
                if tradeDatestr >= '20210906':
                    xly_new_models_path = '/data/group/800463/xiely/model_signal/%s_saturn_930/model_predict.pkl' % tradeDatestr
                else:
                    xly_new_models_path = '/data/user/013551/xly_dailyModelPredict_v2/%s_saturn_930/model_predict.pkl' % tradeDatestr
                if tradeDatestr >= v5_pj2_start_date:
                    print(tradeDatestr, XLY_model_name, ' has no prediction!')
                    xly_model_local_prob = pd.DataFrame(index=this_date_sat_sample_index, columns=[XLY_model_name]).fillna(0)
                else:
                    xly_model_local_prob = pd.read_pickle(xly_new_models_path).rename(columns={'Saturn930' + XLY_model_name + '_pred': XLY_model_name})[[XLY_model_name]]
            this_date_xly_prob = pd.concat([this_date_xly_prob, xly_model_local_prob], axis=1).reindex(this_date_sat_sample_index)

        # v6部分
        if tradeDatestr >= v6_pj2_start_date:
            pred_path = '/data/group/800463/wangj/model_signal/Saturn/S1_v6/%s/%s_%s_saturn_fac_v6_daily_pred.csv' % (
                tradeDatestr, tradeDatestr, tradeDatestr)
            tmp_day_df = pd.read_csv(pred_path)
            tmp_day_df.rename(columns=v6_rename_modeldict, inplace=True)
            tmp_day_df.rename(columns=v6_rename_probadict, inplace=True)
            tmp_day_df.rename(columns=v6_rename_modelpooldict, inplace=True)
            tmp_day_df.rename(columns=v6_rename_probapooldict, inplace=True)
            tmp_day_df['dt'] = tmp_day_df['dt'].apply(lambda x: pd.Timestamp(x))
            tmp_day_df = tmp_day_df.set_index(['dt', 'Ticker'])[v6_model_name_pool + v6_model_pool_proba1]
            this_date_v6_prob = pd.concat([this_date_v6_prob, tmp_day_df.reindex(this_date_sat_sample_index)], axis=1)

    wj_prob = pd.concat([wj_prob, this_date_wj_prob])
    dj_prob = pd.concat([dj_prob, this_date_dj_prob])
    xly_prob = pd.concat([xly_prob, this_date_xly_prob])
    v6_prob = pd.concat([v6_prob, this_date_v6_prob])

saturn_tot_local_prob = pd.concat([wj_prob, dj_prob, xly_prob, v6_prob], axis=1, join_axes=[wj_prob.index])

# 分场景部分结合
s1_vote_thres = 5
v6s1_vote_thres = 3
saturn_tot_local_prob['openPctWjClaModel'] = saturn_tot_local_prob['openPctHighWjClaModel'].fillna(0) + saturn_tot_local_prob['openPctLowWjClaModel'].fillna(0)
saturn_tot_local_prob['openPctDjClaModel'] = saturn_tot_local_prob['openPctHighDjClaModel'].fillna(0) + saturn_tot_local_prob['openPctLowDjClaModel'].fillna(0)
saturn_tot_local_prob['saturn931OpenPctWjModel'] = saturn_tot_local_prob['saturn931OpenPctHighWjModel'].fillna(0) + saturn_tot_local_prob['saturn931OpenPctLowWjModel'].fillna(0)
saturn_tot_local_prob['saturn931OpenPctDjModel'] = saturn_tot_local_prob['saturn931OpenPctHighDjModel'].fillna(0) + saturn_tot_local_prob['saturn931OpenPctLowDjModel'].fillna(0)
saturn_tot_local_prob['saturn931Pct5WjModel'] = saturn_tot_local_prob['saturn931Pct5HighWjModel'].fillna(0) + saturn_tot_local_prob['saturn931Pct5LowWjModel'].fillna(0)

saturn_tot_local_prob['saturn931Pat34DjModel'] = saturn_tot_local_prob['saturn931Pat3DjModel'].fillna(0) + saturn_tot_local_prob['saturn931Pat4DjModel'].fillna(0)
saturn_tot_local_prob['saturn931Ret2oDjModel'] = saturn_tot_local_prob['saturn931Ret2oHighDjModel'].fillna(0) + saturn_tot_local_prob['saturn931Ret2oLowDjModel'].fillna(0)
saturn_tot_local_prob['saturn931OpenPctWj_proba1'] = pd.concat([saturn_tot_local_prob['saturn931OpenPctHighWj_proba1'].dropna(),saturn_tot_local_prob['saturn931OpenPctLowWj_proba1'].dropna()]).reindex(saturn_tot_local_prob.index).fillna(0)
saturn_tot_local_prob['saturn931Pct5Wj_proba1'] = pd.concat([saturn_tot_local_prob['saturn931Pct5HighWj_proba1'].dropna(),saturn_tot_local_prob['saturn931Pct5LowWj_proba1'].dropna()]).reindex(saturn_tot_local_prob.index).fillna(0)
saturn_tot_local_prob['saturn931OpenPctDj_proba1'] = pd.concat([saturn_tot_local_prob['saturn931OpenPctHighDj_proba1'].dropna(), saturn_tot_local_prob['saturn931OpenPctLowDj_proba1'].dropna()]).reindex(saturn_tot_local_prob.index).fillna(0)
saturn_tot_local_prob['saturn931Pat34Dj_proba1'] = saturn_tot_local_prob['saturn931Pat3Dj_proba1'].fillna(0) + saturn_tot_local_prob['saturn931Pat4Dj_proba1'].fillna(0)
saturn_tot_local_prob['saturn931Ret2oDj_proba1'] = saturn_tot_local_prob['saturn931Ret2oHighDj_proba1'].fillna(0) + saturn_tot_local_prob['saturn931Ret2oLowDj_proba1'].fillna(0)
saturn_tot_local_prob['saturn931Pat34Xly_proba1'] = saturn_tot_local_prob['S1Pat3PMMLModel_proba'].fillna(0) + saturn_tot_local_prob['S1Pat4PMMLModel_proba'].fillna(0)
saturn_tot_local_prob['saturn931Ret2OXly_proba1'] = saturn_tot_local_prob['S1Ret2oHighXgbModel_proba'].fillna(0) + saturn_tot_local_prob['S1Ret2oLowPMMLModel_proba'].fillna(0)
s1_cols = list(filter(lambda x: x.find('931') >= 0, saturn_model_name_all))
s1_proba1 = [x.split('Model')[0] + '_proba1' for x in s1_cols]
v5_saturn_tot_local_prob = saturn_tot_local_prob[s1_cols + s1_proba1]
v6_saturn_tot_local_prob = saturn_tot_local_prob[v6_model_name_pool + v6_model_pool_proba1]

v5_saturn_tot_local_prob['s1_vote_sum'] = v5_saturn_tot_local_prob[s1_cols].sum(axis=1)
v6_saturn_tot_local_prob['s1_vote_sum'] = v6_saturn_tot_local_prob[v6_model_name_all].sum(axis=1)

v5_saturn_tot_local_s1 = pd.concat([sat_local_basic_file, v5_saturn_tot_local_prob], axis=1, join_axes=[v5_saturn_tot_local_prob.index])
v6_saturn_tot_local_s1 = pd.concat([sat_local_basic_file, v6_saturn_tot_local_prob], axis=1, join_axes=[v6_saturn_tot_local_prob.index])
v5_saturn_tot_local_s1['shouldBuySignal'] = v5_saturn_tot_local_s1['s1_vote_sum'].apply(lambda x: 1 if x >= s1_vote_thres else 0)
v6_saturn_tot_local_s1['shouldBuySignal'] = v6_saturn_tot_local_s1['s1_vote_sum'].apply(lambda x: 1 if x >= 3 else 0)

writer = pd.ExcelWriter(savepath + '策略实盘与本地触发对比_%s_%s.xlsx' % (year_start_date, end_date_lw))
v5_saturn_tot_local_s1.reset_index().to_excel(writer, sheet_name='s1_v5')
v6_saturn_tot_local_s1.reset_index().to_excel(writer, sheet_name='s1_v6')
writer.save()

# 计算各个版本各个模型本地信号的评价
sat_model_track_v5 = modeltrack_Tool('s1', year_start_date_h, end_date_lw, savepath, v5_saturn_tot_local_s1, s1_cols, s1_cols, 5)
tot_local_returnv5, tot_local_predict_summaryv5 = sat_model_track_v5.cal_modeltrack_data(type='vote')
tot_local_returnv5_pool, tot_local_predict_summaryv5_pool = sat_model_track_v5.cal_modeltrack_data(type='all')

sat_model_track_v5comp = modeltrack_Tool('s1', v6_pj2_start_date, end_date_h, savepath, v5_saturn_tot_local_s1, s1_cols, s1_cols, 5)
tot_local_returnv5comp, tot_local_predict_summaryv5comp = sat_model_track_v5comp.cal_modeltrack_data(type='vote')
tot_local_returnv5comp_pool, tot_local_predict_summaryv5comp_pool = sat_model_track_v5comp.cal_modeltrack_data(type='all')

sat_model_track_v6 = modeltrack_Tool('s1', v6_pj2_start_date, end_date_h, savepath, v6_saturn_tot_local_s1, v6_model_name_all, v6_model_name_pool, 3)
tot_local_returnv6, tot_local_predict_summaryv6 = sat_model_track_v6.cal_modeltrack_data(type='vote')
tot_local_returnv6_pool, tot_local_predict_summaryv6_pool = sat_model_track_v6.cal_modeltrack_data(type='all')

# 写入excel
workbook = xlsxwriter.Workbook('%s%s模型跟踪v6_%s_%s.xlsx' % (savepath, sat_model_track_v5.strategy, year_start_date, end_date_lw))
generate_sheet(workbook, savepath, sat_model_track_v5.strategy, tot_local_predict_summaryv5, tot_local_returnv5, int(np.ceil(len(s1_cols) / 2) + 2), '5')
generate_sheet(workbook, savepath, sat_model_track_v5.strategy, tot_local_predict_summaryv5_pool, tot_local_returnv5_pool, len(s1_cols), '5modelpool')
generate_sheet(workbook, savepath, sat_model_track_v5.strategy, tot_local_predict_summaryv5comp, tot_local_returnv5comp, int(np.ceil(len(s1_cols) / 2) + 2), '5comp')
generate_sheet(workbook, savepath, sat_model_track_v5.strategy, tot_local_predict_summaryv5comp_pool, tot_local_returnv5comp_pool, len(s1_cols), '5compmodelpool')
generate_sheet(workbook, savepath, sat_model_track_v6.strategy, tot_local_predict_summaryv6, tot_local_returnv6, int(np.ceil(len(v6_model_name_all) / 2) + 2), '6')
generate_sheet(workbook, savepath, sat_model_track_v6.strategy, tot_local_predict_summaryv6_pool, tot_local_returnv6_pool, len(v6_model_name_pool), '6modelpool')

workbook.close()