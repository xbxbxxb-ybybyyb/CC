# @Time : 2021/10/20 18:59
# @Author : Zhichen Lu
# @File : pred_distribution_analysis.py

import pandas as pd
import numpy as np
from StrongStockModel.conf.path_config import root_path
import os
from xquant.factordata import FactorData
import time
from dataApi.tradeDate import get_date_range


def return_integration(para_inf, start, end):
    res = {}
    for each in para_inf:
        res[each] = pd.read_pickle(each).loc[start:end]

    res = pd.Panel(res)
    res_sum = res.sum(axis=0)
    res_count = res.count(axis=0)

    res_integration = res_sum / res_count
    res_integration[res_count.eq(0)] = np.nan
    return res_integration.loc[start:end]


s = FactorData()
wind_a = s.get_factor_value('WIND_AIndexWindIndustriesEOD', S_INFO_WINDCODE=['881001.WI'])[['TRADE_DT', 'S_DQ_CLOSE', 'S_DQ_AMOUNT']].set_index('TRADE_DT')
wind_a = wind_a.sort_index().loc['20151231':]
kcb_szzs = s.get_factor_value('Basic_factor', ['000001.SH', '399006.SZ', '399001.SZ', '000300.SH', '000905.SH', '000016.SH', '000852.SH'], factor_names=['close'],
                              mddate=wind_a.index.tolist())
kcb_szzs = kcb_szzs.reset_index().pivot_table(index='mddate', columns='stock', values='close').sort_index()

kcb_szzs_amt = s.get_factor_value('Basic_factor', ['000001.SH', '399006.SZ', '399001.SZ', '000300.SH', '000905.SH', '000016.SH', '000852.SH'],
                                  factor_names=['amt'],
                                  mddate=wind_a.index.tolist()).pivot_table(index='mddate', columns='stock', values='amt').sort_index()

# kcb_szzs = s.get_factor_value('Basic_factor', ['000016.SH','000852.SH'], factor_names=['close'], mddate=wind_a.index.tolist())

indexes = pd.concat([wind_a, kcb_szzs], axis=1).rename(columns=
                                                       {'S_DQ_CLOSE': '万德全A', '000001.SH': '上证指数', '399006.SZ': '创业板指',
                                                        '399001.SZ': '深证成指', '000300.SH': '沪深300', '000905.SH': '中证500',
                                                        '000016.SH': '上证50', '000852.SH': '中证1000'}).sort_index()

indexes_amt = pd.concat([wind_a[['S_DQ_AMOUNT']], kcb_szzs_amt], axis=1).rename(columns=
                                                                                {'S_DQ_AMOUNT': '万德全A', '000001.SH': '上证指数', '399006.SZ': '创业板指',
                                                                                 '399001.SZ': '深证成指', '000300.SH': '沪深300', '000905.SH': '中证500',
                                                                                 '000016.SH': '上证50', '000852.SH': '中证1000'}).sort_index()

indexes.index = indexes.index.astype(int)
indexes_pct = indexes.pct_change()
from tqdm import tqdm
para = {
    'Cat': ['/data/group/800442/800319/wyl/model_record/catboostnew2_ic_all_t.pkl'],
    'Light': ['/data/group/800442/800319/wyl/model_record/lightgbmnew_ic_all_t.pkl'],
    'XGB_C': [
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_c_train200_test10_factor_num400_norm_window_40.pkl'],
    'XGB_D': [
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_d_train200_test10_factor_num400_norm_window_40.pkl'],
    'XBG_T': [
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_t_train200_test10_factor_num400_norm_window_40.pkl'],
    'all_integration':[
        '/data/group/800442/800319/wyl/model_record/catboostnew2_ic_all_t.pkl',
        '/data/group/800442/800319/wyl/model_record/lightgbmnew_ic_all_t.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_c_train200_test10_factor_num400_norm_window_40.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_d_train200_test10_factor_num400_norm_window_40.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_t_train200_test10_factor_num400_norm_window_40.pkl',
    ],

}
all_stat = {}
for p_inf in tqdm(para.keys()):
    # p_inf = 'All'
    # pred = return_integration(para[p_inf], 20210406, 20211021)
    # pd.to_pickle(pred, f'{root_path}data_analysis/XGB_Light_Cat_IntergretedPredSinceOnline.pkl')
    #
    # signal, pred_ret = pd.read_pickle('/data/user/015664/AFuckingTrigger/限制买入和持仓/信号存储/signal_XGBMonthlyV4_Cat_LightWithoutMax5_0.05.pkl')
    pred = pd.read_pickle(f'{root_path}data_analysis/XGB_Light_Cat_IntergretedPred.pkl')
    # _,pred = pd.read_pickle('/data/user/015664/AFuckingTrigger/限制买入和持仓/信号存储/实盘跟踪线下信号/signal_OutSample_XGB_Cat_Light_OnlineTest_20211021.pkl')
    # pred = pred.stack()
    stat = {}
    stat['mean'] = pred.groupby(level=0).mean()
    stat['median'] = pred.groupby(level=0).median()
    stat['std'] = pred.groupby(level=0).std()
    for qt in range(1, 10, 2):
        stat[f'percentile_{qt}'] = pred.groupby(level=0).quantile(qt * 0.1)
    stat = pd.Panel(stat)
    all_stat[p_inf] = pd.concat([stat[:, :, 'prediction'], indexes_pct], axis=1)
    all_stat['真实标签'] = pd.concat([stat[:, :, 'actual_label'], indexes_pct], axis=1)  # stat[:,:,'actual_label']
corr = all_stat['All'].corr()


with pd.ExcelWriter('./量纲统计实盘以来_逐模型统计.xlsx') as writer:
    for each in all_stat:
        all_stat[each].dropna().to_excel(writer, sheet_name=each)
    # label_stat.to_excel(writer, sheet_name='实际标签')
writer.close()
from dataApi.sendInfo import send_file

send_file(['015664'], './量纲统计实盘以来_逐模型统计.xlsx')




threshold_series = [[20161220, 0.009458912725947266], [20170104, 0.009919039796600774], [20170118, 0.011161553621201022], [20170208, 0.009315193228592067], [20170222, 0.007516027646341104],
 [20170308, 0.00772626502529136], [20170322, 0.009415791370011152], [20170407, 0.00992109817844908], [20170421, 0.007047082888549865], [20170508, 0.006242914022584526],
 [20170522, 0.004919435091373468], [20170607, 0.006151337574850466], [20170621, 0.005419420670466536], [20170705, 0.006372980793676922], [20170719, 0.007521022473378811],
 [20170802, 0.004167710452019778], [20170816, 0.006265161858718939], [20170830, 0.005399292323879556], [20170913, 0.0041508964311750525], [20170927, 0.005968506125756726],
 [20171018, 0.005149259229100616], [20171101, 0.006314400386265407], [20171115, 0.005120882934486694], [20171129, 0.008309800893719126], [20171213, 0.0062824369303856],
 [20171227, 0.006327482478435062], [20180111, 0.0042416491572214755], [20180125, 0.004403186933141088], [20180208, 0.012080076585702074], [20180301, 0.007321743614338295],
 [20180315, 0.00577929291628509], [20180329, 0.0056084631122906795], [20180416, 0.006289350959088423], [20180502, 0.004945415341377929], [20180516, 0.004332410999474129],
 [20180530, 0.005402866878305157], [20180613, 0.00646773330148829], [20180628, 0.011638428549290097], [20180712, 0.006781028904756222], [20180726, 0.007078848228622025],
 [20180809, 0.005092653059106867], [20180823, 0.0055315419901061135], [20180906, 0.004781387575756413], [20180920, 0.003786908282352556], [20181012, 0.007035324576940207],
 [20181026, 0.01099781258900796], [20181109, 0.006873346328699323], [20181123, 0.007381467640093702], [20181207, 0.009541267637167674], [20181221, 0.010933465080014635],
 [20190108, 0.0049066852409861625], [20190122, 0.0045492645986325185], [20190212, 0.006819346543376385], [20190226, 0.006780866317190673], [20190312, 0.015553054911290628],
 [20190326, 0.007814607263201401], [20190410, 0.00905274956929761], [20190424, 0.012318650227009077], [20190513, 0.019265490730643313], [20190527, 0.008922960331452168],
 [20190611, 0.006778093628741613], [20190625, 0.00829098917641028], [20190709, 0.00895603465893], [20190723, 0.010709947229944537], [20190806, 0.007178315058078642],
 [20190820, 0.011187187245561258], [20190903, 0.010092207648411126], [20190918, 0.01096305815555213], [20191009, 0.009436960740781519], [20191023, 0.00961673450677935],
 [20191106, 0.00594463294618856], [20191120, 0.007888318611261429], [20191204, 0.006213908310571749], [20191218, 0.004319395123427828], [20200102, 0.009294691954404646],
 [20200116, 0.005829251577832162], [20200207, 0.003500222770027939], [20200221, 0.010171563987668176], [20200306, 0.00732747958666227], [20200320, 0.006216059316559381],
 [20200403, 0.004673635950549083], [20200420, 0.0060884666507146695], [20200507, 0.004538973795805011], [20200521, 0.005946182266161387], [20200604, 0.0053851734158925635],
 [20200618, 0.006761918953020405], [20200706, 0.005638217037041878], [20200720, 0.00960891187949761], [20200803, 0.0072255078435831495], [20200817, 0.007662542466195026],
 [20200831, 0.006797189011021211], [20200914, 0.008155510131928926], [20200928, 0.006735315365127157], [20201020, 0.01101821279853741], [20201103, 0.007473361953076817],
 [20201117, 0.009747952311880992], [20201201, 0.0050489020621042645], [20201215, 0.008097972913167103], [20201229, 0.0068904497581845055], [20210113, 0.007181196577040231],
 [20210127, 0.00652188219182538], [20210210, 0.006227898421589631], [20210303, 0.003590664816742738], [20210317, 0.007078072136826617], [20210331, 0.0037315986105837208],
 [20210415, 0.0038503657496387175], [20210429, 0.004360349031017157], [20210518, 0.004909220711086838], [20210525, 0.003237118088558633], [20210526, 0.0036272587707012745],
 [20210527, 0.00495033564365224]]
threshold_series = pd.DataFrame(threshold_series).set_index(0)
threshold_series = threshold_series.reindex(get_date_range(threshold_series.index[0],threshold_series.index[-1])).fillna(method='pad')
threshold_series.columns = ['阈值']
threshold_series.index = threshold_series.index.astype(str)
with pd.ExcelWriter('./amt.xlsx') as writer:
    pd.concat([indexes_amt,threshold_series],axis=1).to_excel(writer, sheet_name='预测标签')
writer.close()

