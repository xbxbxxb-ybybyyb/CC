# coding: utf-8
# Author：fengchi863
# Date ：2023/5/22 17:31
from xquant.factordata import FactorData

s = FactorData()
import matplotlib.pyplot as plt
import xlsxwriter
from ProdWork.model_track.modeltrack_Tool_v2 import *
from ProdWork.model_track.config import *

# -----------合并ceress1的模型------------
from ProdWork.Param_config_data import latest_version_pj3

cer_local_basic_file = pd.DataFrame()
ver3_cerbegin = '20220617'
last_version_indicator = '2'
now_version_pj3 = latest_version_pj3
for date in s.tradingday(year_start_date, end_date_lw):
    if date < now_version_pj3:
        this_date_basic = pd.read_pickle(
            '/data/group/800463/project/project3_prod/daily_data/%s/ceres_factor_v0902_%s.pkl' % (
            str(date), str(date)))
    elif date < ver3_cerbegin:
        this_date_basic = pd.read_pickle(
            '/data/group/800463/project/project3_prod/daily_data/%s_v2/ceres_factor_v0120_%s.pkl' % (
            str(date), str(date)))
    else:
        this_date_basic = pd.read_pickle(
            '/data/group/800463/project/project3_prod/daily_data/' + str(date) + '_v3/ceres_factor_v3_' + str(
                date) + '.pkl')
    cer_local_basic_file = pd.concat([cer_local_basic_file, this_date_basic])
# cers1_model_track = modeltrack_Tool('ceress1', year_start_date_h, end_date_h, savepath, cer_local_basic_file)
# local_basic_file_cers1_need = cers1_model_track.rawdata.copy()

DJ_cermodel_name_all = ['ceres931cbMoreDjModel', 'ceres931cbOneDjModel', \
                        'ceres931Pct5HighDjModel', 'ceres931Pct5LowDjModel', 'ceres931TotalDjModel',
                        'ceres931totalOpenDjModel'] + ['ceres931Pct5HighClaDjModel', 'ceres931Pct5LowClaDjModel',
                                                       'ceres931O2ulHighClaDjModel', 'ceres931O2ulLowClaDjModel']
DJ_cermodel_name_all = DJ_cermodel_name_all + ['ceres931cbMoreDjModel_v2', 'ceres931cbOneDjModel_v2', \
                                               'ceres931Pct5HighDjModel_v2', 'ceres931Pct5LowDjModel_v2',
                                               'ceres931TotalDjModel_v2',
                                               'ceres931totalOpenDjModel_v2']
WJ_cermodel_name_all = ['ceres931OpenPctMedWjModel', 'ceres931OpenPctOthWjModel', \
                        'ceres931Pct5HighWjModel', 'ceres931Pct5LowWjModel', 'ceres931TotalWjModel'] + [
                           'ceres931Pct5HighClaWjModel', 'ceres931Pct5LowClaWjModel']
WJ_cermodel_name_all = WJ_cermodel_name_all + ['ceres931OpenPctMedWjModel_v%s' % last_version_indicator,
                                               'ceres931OpenPctOthWjModel_v%s' % last_version_indicator, \
                                               'ceres931Pct5HighWjModel_v%s' % last_version_indicator,
                                               'ceres931Pct5LowWjModel_v%s' % last_version_indicator]  # 添加上一版本模型且用版本号进行区分标注
XLY_cermodel_name_all_v1 = ['ceres931TimeXlyModel', 'ceres931t1PctXlyModel', 'ceres931UlXlyModel',
                            'ceres931TotalXlyModel']
XLY_cermodel_name_all_v2 = ['ceres931t1PctXlyModel', 'ceres931UlXlyModel', 'ceres931TotalXlyModel']
XLY_cermodel_name_all_v3 = ['ceres931t1PctXlyModel'] + [x + '_v%s' % last_version_indicator for x in
                                                        XLY_cermodel_name_all_v2]
ceres_model_rename_dict = {'ceres931cbMoreDjModel': 'SP2_931_cbmore_reg_v1',
                           'ceres931cbOneDjModel': 'SP2_931_cbone_reg_v1',
                           'ceres931Pct5HighDjModel': 'SP2_931_open5high_reg_v1',
                           'ceres931Pct5LowDjModel': 'SP2_931_open5low_reg_v1',
                           'ceres931TotalDjModel': 'SP2_931_reg_v1',
                           'ceres931totalOpenDjModel': 'SP2_931_reg_o_v1',
                           'ceres931cbMoreDjModel_v2': 'SP2_931_cbmore_reg_v1',
                           'ceres931cbOneDjModel_v2': 'SP2_931_cbone_reg_v1',
                           'ceres931Pct5HighDjModel_v2': 'SP2_931_open5high_reg_v1',
                           'ceres931Pct5LowDjModel_v2': 'SP2_931_open5low_reg_v1',
                           'ceres931TotalDjModel_v2': 'SP2_931_reg_v1',
                           'ceres931totalOpenDjModel_v2': 'SP2_931_reg_o_v1',

                           'ceres931Pct5HighClaDjModel': 'SP2_931_open5high_cla',
                           'ceres931Pct5LowClaDjModel': 'SP2_931_open5low_cla',
                           'ceres931O2ulHighClaDjModel': 'SP2_931_o2ulhigh_cla',
                           'ceres931O2ulLowClaDjModel': 'SP2_931_o2ullow_cla',

                           'ceres931OpenPctMedWjModel': 'MedopenwjModel',
                           'ceres931OpenPctOthWjModel': 'OthopenwjModel',
                           'ceres931Pct5HighWjModel': 'Highpct5wjModel',
                           'ceres931Pct5LowWjModel': 'Lowpct5wjModel',
                           'ceres931OpenPctMedWjModel_v2': 'MedopenwjModel',
                           'ceres931OpenPctOthWjModel_v2': 'OthopenwjModel',
                           'ceres931Pct5HighWjModel_v2': 'Highpct5wjModel',
                           'ceres931Pct5LowWjModel_v2': 'Lowpct5wjModel',

                           'ceres931Pct5HighClaWjModel': 'Highpct5ClawjModel',
                           'ceres931Pct5LowClaWjModel': 'Lowpct5ClawjModel',
                           'ceres931TotalWjModel': 'allregwjModel',
                           'ceres931TimeXlyModel': 'CeresS1TimeXlyModel',
                           'ceres931t1PctXlyModel': 'CeresS1t1PctXlyModel',
                           'ceres931UlXlyModel': 'CeresS1UlXlyModel',
                           'ceres931TotalXlyModel': 'CeresS1TotalXlyModel',

                           'ceres931t1PctXlyModel_v2': 'CeresS1t1PctXlyModel',
                           'ceres931UlXlyModel_v2': 'CeresS1UlXlyModel',
                           'ceres931TotalXlyModel_v2': 'CeresS1TotalXlyModel',
                           }
wj_prob = pd.DataFrame()
dj_prob = pd.DataFrame()
xly_prob = pd.DataFrame()

for tradeDatestr in s.tradingday(year_start_date, end_date_lw):
    print('ceres:%s' % tradeDatestr)
    this_date_wj_prob = pd.DataFrame()
    this_date_dj_prob = pd.DataFrame()
    this_date_xly_prob = pd.DataFrame()
    this_date_cer_index = cer_local_basic_file[(
                cer_local_basic_file.reset_index()['dt'] == pd.Timestamp(
            tradeDatestr)).values].index  # local_basic_file_cers1_need.loc[pd.Timestamp(tradeDatestr):pd.Timestamp(tradeDatestr)].index
    if tradeDatestr >= '20211129':
        for WJ_model_name in WJ_cermodel_name_all:
            print(WJ_model_name)
            if WJ_model_name.find('931') > 0 and WJ_model_name.find('_v%s' % last_version_indicator) < 0:
                wj_new_models_path = '/data/group/800463/wangj/model_signal/Ceres/S1/%s/%s' % (
                ceres_model_rename_dict[WJ_model_name], tradeDatestr)
            elif WJ_model_name.find('931') > 0 and WJ_model_name.find('_v%s' % last_version_indicator) >= 0:
                print(WJ_model_name)
                wj_new_models_path = '/data/group/800463/wangj/model_signal/Ceres/S1/%s/%s' % (
                ceres_model_rename_dict[WJ_model_name], tradeDatestr)
            else:
                wj_new_models_path = '/data/group/800463/wangj/model_signal/Ceres/S0/%s/%s' % (
                ceres_model_rename_dict[WJ_model_name], tradeDatestr)

            # 核对模型的预测数据
            if os.path.exists(wj_new_models_path + '/预测数据/'):
                Predict_file_csvs = os.listdir(wj_new_models_path + '/预测数据/')
                csv_name = np.array(Predict_file_csvs)[
                    np.array(list(map(lambda x: '%s~%s' % (tradeDatestr, tradeDatestr) in x, Predict_file_csvs)))][
                    0]
                try:
                    WJ_model_local_prob = pd.read_csv(wj_new_models_path + '/预测数据/' + csv_name)
                except:
                    WJ_model_local_prob = pd.read_csv(wj_new_models_path + '/预测数据/' + csv_name, encoding='GBK')
            else:
                print(tradeDatestr, WJ_model_name, 'has no prediction file!!!!!!!!!!')
                WJ_model_local_prob = pd.DataFrame(index=this_date_cer_index,
                                                   columns=['prediction', 'pred_Reg', 'probability']).fillna(
                    0).reset_index()
            WJ_model_local_prob['dt'] = [pd.Timestamp(str(x)) for x in WJ_model_local_prob.dt.tolist()]
            WJ_model_local_label = \
                WJ_model_local_prob.set_index(['dt', 'Ticker']).rename(columns={'prediction': WJ_model_name,'probability':WJ_model_name.split('Model')[0]+'_proba1','pred_Reg':WJ_model_name.split('Model')[0]+'_proba1'})[
                    [WJ_model_name,WJ_model_name.split('Model')[0]+'_proba1']]
            if tradeDatestr >= now_version_pj3 and WJ_model_name == 'ceres931TotalWjModel':
                print(tradeDatestr, WJ_model_name)
                WJ_model_local_prob = pd.DataFrame(index=this_date_cer_index,
                                                   columns=[WJ_model_name,WJ_model_name.split('Model')[0]+'_proba1']).fillna(0)
            this_date_wj_prob = pd.concat([this_date_wj_prob, WJ_model_local_label], axis=1).reindex(this_date_cer_index)
        for DJ_model_name in DJ_cermodel_name_all:
            print(DJ_model_name)
            this_date_dj_path = '/data/group/800463/dongj/model_signal/ceres/model_output_everyday/%s_%s/pred_label.h5' % (
            tradeDatestr, ceres_model_rename_dict[DJ_model_name])
            this_date_djprob_path = '/data/group/800463/dongj/model_signal/ceres/model_output_everyday/%s_%s/pred_prob.h5' % (
                tradeDatestr, ceres_model_rename_dict[DJ_model_name])
            if tradeDatestr >= ver3_cerbegin and DJ_model_name.find('_v%s' % last_version_indicator) < 0:
                this_date_dj_path = '/data/group/800463/dongj/model_signal/ceres/v3/model_output_everyday/%s_%s/pred_label.h5' % (
                tradeDatestr, ceres_model_rename_dict[DJ_model_name])
                this_date_djprob_path = '/data/group/800463/dongj/model_signal/ceres/v3/model_output_everyday/%s_%s/pred_prob.h5' % (
                    tradeDatestr, ceres_model_rename_dict[DJ_model_name])

            if os.path.exists(this_date_dj_path):
                DJ_model_local_label = pd.read_hdf(this_date_dj_path)
                DJ_model_local_prob = pd.read_hdf(this_date_djprob_path)
                DJ_model_local_prob = pd.concat([DJ_model_local_label,DJ_model_local_prob],axis=1)
            else:
                print(tradeDatestr, DJ_model_name, 'has no prediction file!!!!!!!!!!')
                DJ_model_local_prob = pd.DataFrame(index=this_date_cer_index,
                                                   columns=['pred_label','pred_prob']).fillna(0)  # .reset_index()
            DJ_model_local_prob = DJ_model_local_prob.rename(columns={'pred_label': DJ_model_name,'pred_prob': DJ_model_name.split('Model')[0]+'_proba1'})
            this_date_dj_prob = pd.concat([this_date_dj_prob, DJ_model_local_prob], axis=1).reindex(this_date_cer_index)
        XLY_cermodel_name_all = XLY_cermodel_name_all_v1
        if tradeDatestr >= now_version_pj3 and tradeDatestr < ver3_cerbegin:
            XLY_cermodel_name_all = XLY_cermodel_name_all_v1
        else:
            XLY_cermodel_name_all = XLY_cermodel_name_all_v3
        for XLY_model_name in list(
                set(XLY_cermodel_name_all_v1 + XLY_cermodel_name_all_v2 + XLY_cermodel_name_all_v3)):
            print(XLY_model_name)
            if XLY_model_name.find('931') > 0:
                xly_new_models_path = '/data/group/800463/xiely/model_signal/%s_ceres_931/model_predict.pkl' % tradeDatestr
                if tradeDatestr >= ver3_cerbegin and XLY_model_name == 'ceres931t1PctXlyModel':
                    xly_new_models_path = '/data/group/800463/xiely/model_signal/%s_ceres_931_v3/model_predict.pkl' % tradeDatestr

                xly_model_local_proball = pd.read_pickle(xly_new_models_path)
                xly_model_local_proball.rename(columns={'t1PctXlyModel_pred': 'CeresS1t1PctXlyModel_pred',
                                                        'ulXlyModel_pred': 'CeresS1UlXlyModel_pred',
                                                        'totalXlyModel_pred': 'CeresS1TotalXlyModel_pred'},
                                               inplace=True)
                if ceres_model_rename_dict[
                    XLY_model_name] + '_pred' not in xly_model_local_proball.columns.tolist():
                    print('%s has no prediction' % XLY_model_name)
                    xly_model_local_proball = pd.DataFrame(index=this_date_cer_index, columns=[
                        ceres_model_rename_dict[XLY_model_name] + '_pred',ceres_model_rename_dict[XLY_model_name] + '_proba'])
                    xly_model_local_proball[ceres_model_rename_dict[XLY_model_name] + '_pred'] = 0
                addcols = list(filter(lambda x: x.find(XLY_model_name[8:16]) >= 0 and x.find('proba') >= 0,
                                      xly_model_local_proball.columns.tolist()))
                xly_model_local_prob = xly_model_local_proball.rename(
                    columns={ceres_model_rename_dict[XLY_model_name] + '_pred': XLY_model_name})[
                    [XLY_model_name]+addcols]
            else:
                xly_new_models_path = '/data/group/800463/xiely/model_signal/%s_saturn_930/model_predict.pkl' % tradeDatestr
                # 核对模型的预测数据
                xly_model_local_prob = pd.read_pickle(xly_new_models_path).rename(
                    columns={'Ceres930' + XLY_model_name + '_pred': XLY_model_name})[[XLY_model_name]]
            this_date_xly_prob = pd.concat(
                [this_date_xly_prob, xly_model_local_prob], axis=1).reindex(this_date_cer_index)#.fillna(0)
    wj_prob = pd.concat([wj_prob, this_date_wj_prob])
    dj_prob = pd.concat([dj_prob, this_date_dj_prob])
    xly_prob = pd.concat([xly_prob, this_date_xly_prob])

ceres_tot_local_prob = pd.concat([wj_prob, dj_prob, xly_prob], axis=1, join_axes=[wj_prob.index])

s0_vote_thres, s1_vote_thres, s1_vote_thres_v2, s1_vote_thres_v3 = 3, 4, 5, 3
ceres_tot_local_prob['ceres931OpenPctWjModel'] = ceres_tot_local_prob['ceres931OpenPctMedWjModel'].fillna(0) + \
                                                 ceres_tot_local_prob['ceres931OpenPctOthWjModel'].fillna(0)
ceres_tot_local_prob['ceres931Pct5WjModel'] = ceres_tot_local_prob['ceres931Pct5HighWjModel'].fillna(0) + \
                                              ceres_tot_local_prob['ceres931Pct5LowWjModel'].fillna(0)
ceres_tot_local_prob['ceres931OpenPctWjModel_v2'] = ceres_tot_local_prob['ceres931OpenPctMedWjModel_v2'].fillna(0) + \
                                                    ceres_tot_local_prob['ceres931OpenPctOthWjModel_v2'].fillna(0)
ceres_tot_local_prob['ceres931Pct5WjModel_v2'] = ceres_tot_local_prob['ceres931Pct5HighWjModel_v2'].fillna(0) + \
                                                 ceres_tot_local_prob['ceres931Pct5LowWjModel_v2'].fillna(0)
ceres_tot_local_prob['ceres931Pct5ClaWjModel'] = ceres_tot_local_prob['ceres931Pct5HighClaWjModel'].fillna(0) + \
                                                 ceres_tot_local_prob['ceres931Pct5LowClaWjModel'].fillna(0)

ceres_tot_local_prob['ceres931Pct5DjModel'] = ceres_tot_local_prob['ceres931Pct5HighDjModel'].fillna(0) + \
                                              ceres_tot_local_prob['ceres931Pct5LowDjModel'].fillna(0)
ceres_tot_local_prob['ceres931Pct5ClaDjModel'] = ceres_tot_local_prob['ceres931Pct5HighClaDjModel'].fillna(0) + \
                                                 ceres_tot_local_prob['ceres931Pct5LowClaDjModel'].fillna(0)
ceres_tot_local_prob['ceres931O2ulClaDjModel'] = ceres_tot_local_prob['ceres931O2ulHighClaDjModel'].fillna(0) + \
                                                 ceres_tot_local_prob['ceres931O2ulLowClaDjModel'].fillna(0)
ceres_tot_local_prob['ceres931cbDjModel'] = ceres_tot_local_prob['ceres931cbMoreDjModel'].fillna(0) + \
                                            ceres_tot_local_prob['ceres931cbOneDjModel'].fillna(0)
ceres_tot_local_prob['ceres931Pct5DjModel_v2'] = ceres_tot_local_prob['ceres931Pct5HighDjModel_v2'].fillna(0) + \
                                                 ceres_tot_local_prob['ceres931Pct5LowDjModel_v2'].fillna(0)
ceres_tot_local_prob['ceres931cbDjModel_v2'] = ceres_tot_local_prob['ceres931cbMoreDjModel_v2'].fillna(0) + \
                                               ceres_tot_local_prob['ceres931cbOneDjModel_v2'].fillna(0)
ceres_tot_local_prob['ceres931Pct5ClaWj_proba1'] = ceres_tot_local_prob['ceres931Pct5HighClaWj_proba1'].fillna(0) + \
                                                   ceres_tot_local_prob['ceres931Pct5LowClaWj_proba1'].fillna(0)
ceres_tot_local_prob['ceres931Pct5Dj_proba1'] = ceres_tot_local_prob['ceres931Pct5HighDj_proba1'].fillna(0) + \
                                              ceres_tot_local_prob['ceres931Pct5LowDj_proba1'].fillna(0)
ceres_tot_local_prob['ceres931Pct5ClaDj_proba1'] = ceres_tot_local_prob['ceres931Pct5HighClaDj_proba1'].fillna(0) + \
                                                 ceres_tot_local_prob['ceres931Pct5LowClaDj_proba1'].fillna(0)
ceres_tot_local_prob['ceres931O2ulClaDj_proba1'] = ceres_tot_local_prob['ceres931O2ulHighClaDj_proba1'].fillna(0) + \
                                                 ceres_tot_local_prob['ceres931O2ulLowClaDj_proba1'].fillna(0)
ceres_tot_local_prob['ceres931t1PctXly_proba1'] = ceres_tot_local_prob['t1PctXlyModel_proba'].fillna(0)


lastversion_models = list(set(ceres_tot_local_prob.filter(regex='_v%s' % last_version_indicator).columns.tolist()))
ceres_model_name_all = ['ceres931cbDjModel', 'ceres931Pct5DjModel', 'ceres931TotalDjModel',
                        'ceres931totalOpenDjModel', 'ceres931OpenPctWjModel', 'ceres931Pct5WjModel',
                        'ceres931TotalWjModel', 'ceres931Pct5ClaWjModel', 'ceres931Pct5ClaDjModel',
                        'ceres931O2ulClaDjModel'] + XLY_cermodel_name_all_v1 + lastversion_models

ceres_tot_local_prob = ceres_tot_local_prob[ceres_model_name_all]

s1_cercols = list(set(ceres_tot_local_prob.filter(regex='931').columns.tolist()) - set(
    ['ceres931OpenPctWjModel'] + ['ceres931Pct5ClaWjModel', 'ceres931Pct5ClaDjModel',
                                  'ceres931O2ulClaDjModel'] + lastversion_models))
s1_cercols_v2 = list(set(ceres_tot_local_prob.filter(regex='931').columns.tolist()) - set(
    ['ceres931TimeXlyModel', 'ceres931TotalWjModel'] + ['ceres931Pct5ClaWjModel', 'ceres931Pct5ClaDjModel',
                                                        'ceres931O2ulClaDjModel'] + lastversion_models))
s1_cercols_v2last = [x + '_v%s' % last_version_indicator for x in s1_cercols_v2]
s1_cercols_v3 = ['ceres931Pct5DjModel', 'ceres931TotalDjModel', 'ceres931Pct5ClaWjModel', 'ceres931Pct5ClaDjModel',
                 'ceres931O2ulClaDjModel',
                 'ceres931t1PctXlyModel']  # list(set(ceres_tot_local_prob.filter(regex='931').columns.tolist()) - set(['ceres931TimeXlyModel','ceres931TotalWjModel']))
s1_cercols_v3_proba1 = [x.split('Model')[0]+'_proba1' for x in s1_cercols_v3]
print('v1 models:%d, v2 models:%d, v3 models:%d' % (len(s1_cercols), len(s1_cercols_v2), len(s1_cercols_v3)))
last_ver_cerend = s.tradingday(now_version_pj3, -2)[0]
last_ver2_cerend = s.tradingday(ver3_cerbegin, -2)[0]
v1_indexsets = ceres_tot_local_prob.loc[:pd.Timestamp(last_ver_cerend)].index.tolist()
v2_indexsets = ceres_tot_local_prob.loc[pd.Timestamp(now_version_pj3):pd.Timestamp(last_ver2_cerend)].index.tolist()
v3_indexsets = ceres_tot_local_prob.loc[pd.Timestamp(ver3_cerbegin):].index.tolist()
ceres_tot_local_prob.loc[v1_indexsets, 'ceress1_vote_sum'] = ceres_tot_local_prob.loc[v1_indexsets][s1_cercols].sum(1)
ceres_tot_local_prob.loc[v2_indexsets, 'ceress1_vote_sum'] = ceres_tot_local_prob.loc[v2_indexsets][s1_cercols_v2].sum(1)
ceres_tot_local_prob.loc[v3_indexsets, 'ceress1_vote_sum'] = ceres_tot_local_prob.loc[v3_indexsets][s1_cercols_v3].sum(1)
ceres_tot_local_prob['ceress1_vote_sum_v2comp'] = 0
ceres_tot_local_prob.loc[v3_indexsets, 'ceress1_vote_sum_v2comp'] = ceres_tot_local_prob.loc[v3_indexsets][s1_cercols_v2last].sum(1)
v1_cer = ceres_tot_local_prob.loc[v1_indexsets]
v2_cer = ceres_tot_local_prob.loc[v2_indexsets]
v3_cer = ceres_tot_local_prob.loc[v3_indexsets]
if len(v1_cer) > 0:
    v1_cer['p3shouldBuySignal_local'] = v1_cer.apply(lambda x: 1 if x['ceress1_vote_sum'] >= s1_vote_thres else 0, axis=1)
    ceres_tot_local_prob.loc[v1_indexsets, 'p3shouldBuySignal_local'] = v1_cer['p3shouldBuySignal_local']
if len(v2_cer) > 0:
    v2_cer['p3shouldBuySignal_local'] = v2_cer.apply(lambda x: 1 if x['ceress1_vote_sum'] >= s1_vote_thres_v2 else 0, axis=1)
    ceres_tot_local_prob.loc[v2_indexsets, 'p3shouldBuySignal_local'] = v2_cer['p3shouldBuySignal_local']
# if len(v3_cer)>0:
v3_cer['p3shouldBuySignal_local'] = v3_cer.apply(lambda x: 1 if x['ceress1_vote_sum'] >= s1_vote_thres_v3 else 0, axis=1)
v3_cer['p3shouldBuySignal_local_v2comp'] = v3_cer.apply(lambda x: 1 if x['ceress1_vote_sum_v2comp'] >= s1_vote_thres_v2 else 0, axis=1)

ceres_tot_local_prob.loc[v3_indexsets, 'p3shouldBuySignal_local'] = v3_cer['p3shouldBuySignal_local']
ceres_tot_local_prob['p3shouldBuySignal_local_v2comp'] = 0
ceres_tot_local_prob.loc[v3_indexsets, 'p3shouldBuySignal_local_v2comp'] = v3_cer['p3shouldBuySignal_local_v2comp']
print(ceres_tot_local_prob.sum())

ceres_tot_local_s1 = pd.concat([local_basic_file_cers1_need, ceres_tot_local_prob], axis=1, join_axes=[local_basic_file_cers1_need.index])
ceres_tot_local_s1['shouldBuySignal'] = ceres_tot_local_s1['p3shouldBuySignal_local'].tolist()
ceres_tot_local_s1['shouldBuySignal_v2comp'] = ceres_tot_local_s1['p3shouldBuySignal_local_v2comp'].tolist()

writer = pd.ExcelWriter(savepath + 'Ceres本地信号明细_%s_%s.xlsx' % (year_start_date, end_date_lw))
ceres_tot_local_s1.reset_index().to_excel(writer, sheet_name='s1')
writer.save()

if last_ver_cerend > year_start_date:
    need_signal_cers1v1 = s1_cercols + ['shouldBuySignal']
    cers1_data_v1 = ceres_tot_local_s1.loc[:pd.Timestamp(last_ver_cerend)]
    tot_dt_cers1_v1 = [pd.Timestamp(x) for x in hfactor.tradingday(year_start_date, last_ver_cerend)]
    tot_local_return_cers1v1, tot_local_predict_summary_cers1v1 = cal_modeltrack_data(need_signal_cers1v1, cers1_data_v1, tot_dt_cers1_v1, cers1_model_track)

need_signal_cers1v2 = s1_cercols_v2 + ['shouldBuySignal']
if last_ver2_cerend > year_start_date:
    cers1_data_v2 = ceres_tot_local_s1.loc[pd.Timestamp(now_version_pj3):pd.Timestamp(last_ver2_cerend)]
    tot_dt_cers1_v2 = [pd.Timestamp(x) for x in hfactor.tradingday(now_version_pj3, last_ver2_cerend)]
    tot_local_return_cers1v2, tot_local_predict_summary_cers1v2 = cal_modeltrack_data(need_signal_cers1v2,  cers1_data_v2, tot_dt_cers1_v2, cers1_model_track)

need_signal_cers1v3 = s1_cercols_v3 + ['shouldBuySignal'] + ['shouldBuySignal_v2comp']
cers1_data_v3 = ceres_tot_local_s1.loc[pd.Timestamp(ver3_cerbegin):pd.Timestamp(end_date_lw)]
if ver3_cerbegin > year_start_date:
    tot_dt_cers1_v3 = [pd.Timestamp(x) for x in hfactor.tradingday(ver3_cerbegin, end_date_lw)]
else:
    tot_dt_cers1_v3 = [pd.Timestamp(x) for x in hfactor.tradingday(year_start_date, end_date_lw)]
# tot_dt_cers1_v3 = [pd.Timestamp(x) for x in hfactor.tradingday(ver3_cerbegin, end_date_lw)]
tot_local_return_cers1v3, tot_local_predict_summary_cers1v3 = cal_modeltrack_data(need_signal_cers1v3, cers1_data_v3, tot_dt_cers1_v3, cers1_model_track)

need_signal_cers1comp = s1_cercols_v2last + ['shouldBuySignal_v2comp']
# if last_ver2_cerend > year_start_date:
cers1_data_comp = ceres_tot_local_s1.loc[pd.Timestamp(ver3_cerbegin):pd.Timestamp(end_date_lw)]
if ver3_cerbegin > year_start_date:
    tot_dt_cers1_v3 = [pd.Timestamp(x) for x in hfactor.tradingday(ver3_cerbegin, end_date_lw)]
else:
    tot_dt_cers1_v3 = [pd.Timestamp(x) for x in hfactor.tradingday(year_start_date, end_date_lw)]
tot_local_return_cers1comp, tot_local_predict_summary_cers1comp = cal_modeltrack_data(need_signal_cers1comp, cers1_data_comp, tot_dt_cers1_v3, cers1_model_track)

# 写入excel
workbook = xlsxwriter.Workbook('%s%s模型跟踪_%s_%s.xlsx' % (savepath, cers1_model_track.strategy, year_start_date, end_date_lw))
if last_ver_cerend > year_start_date:
    generate_sheet(workbook, savepath, cers1_model_track.strategy, tot_local_predict_summary_cers1v1, tot_local_return_cers1v1, len(need_signal_cers1v1), '1')
if last_ver2_cerend > year_start_date:
    generate_sheet(workbook, savepath, cers1_model_track.strategy, tot_local_predict_summary_cers1v2, tot_local_return_cers1v2, len(need_signal_cers1v2), '2')
generate_sheet(workbook, savepath, cers1_model_track.strategy, tot_local_predict_summary_cers1v3, tot_local_return_cers1v3, len(need_signal_cers1v3), '3')
generate_sheet(workbook, savepath, cers1_model_track.strategy, tot_local_predict_summary_cers1comp, tot_local_return_cers1comp, len(need_signal_cers1comp), '2compare')
workbook.close()

# 存储个策略本年度集成的实盘信号
createPath('/data/group/800463/wangj/save_files/prod_signal/%s/' % end_date_lw)
jupiterN_local[['ZT_Time', 'shouldBuySignal']].to_csv('/data/group/800463/wangj/save_files/prod_signal/%s/JupiterN_本地信号_20220101_%s.csv' % (end_date_lw, end_date_lw))
eur_local[['ZT_Time', 'shouldBuySignal']].to_csv('/data/group/800463/wangj/save_files/prod_signal/%s/Europa_本地信号_20220101_%s.csv' % (end_date_lw, end_date_lw))
saturn_tot_local_s1[['shouldBuySignal']].to_csv('/data/group/800463/wangj/save_files/prod_signal/%s/S1_本地信号_20220101_%s.csv' % (end_date_lw, end_date_lw))
ceres_tot_local_s1[['shouldBuySignal']].to_csv('/data/group/800463/wangj/save_files/prod_signal/%s/Ceres_本地信号_20220101_%s.csv' % (end_date_lw, end_date_lw))