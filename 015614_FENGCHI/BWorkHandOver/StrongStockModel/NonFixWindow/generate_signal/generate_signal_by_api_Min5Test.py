# @Time : 2022/3/24 9:42
# @Author : Zhichen Lu
# @File : generate_signal_by_api.py
import sys;

print('Python %s on %s' % (sys.version, sys.platform))
sys.path.extend(
    [
    '/data/user/015664/TriggeredTrading', '/data/user/015664/TriggeredTrading/FeatureEngineering', '/data/user/015664/TriggeredTrading/ensemblemonitor-strategy-python',
     '/data/user/015664/TriggeredTrading/StrongStockModel',
     '/data/user/015664/TriggeredTrading/Deep-Reinforcement-Learning-for-Automated-Stock-Trading-Ensemble-Strategy-ICAIF-2020-master',
     '/data/user/015664/TriggeredTrading/FactorAlpha', '/data/user/015664/TriggeredTrading/CrossFT', '/data/user/015664/TriggeredTrading/CrossFT/basic',
     '/data/user/015664/TriggeredTrading/ensemblemonitor-strategy-python/FactorCalculator_', '/data/user/015664/TriggeredTrading/Temporal_Relational_Stock_Ranking-master/training',
     '/data/user/015664/TriggeredTrading/Temporal_Relational_Stock_Ranking-master/preprocess', '/data/user/015664/TriggeredTrading'

     ])

from StrongStockModel.model.ModelResultLoadingTool import generate_short_signal, generate_long_signal
from dataApi.tradeDate import  get_pre_trade_date
import pandas as pd
import os

def get_nonfix_signal_with_930(long_pct,short_pct,start,end,fix_tag,tag_930,max_future=8):

    long_signal = {}
    short_signal = {}
    final_tag = f'Fix_{fix_tag}_930_{tag_930}'
    for future_window in range(1,max_future+1):
        short_path = f'{signal_path}/{final_tag}/short/signal_short_{future_window}_pct_{short_pct}.pkl'
        long_path = f'{signal_path}/{final_tag}/signal_long_{future_window}_pct_{long_pct}.pkl'
        if not os.path.exists(long_path):
            if not os.path.exists(os.path.split(long_path)[0]):
                os.makedirs(os.path.split(long_path)[0])
            if future_window>8:
                long_fix = {future_window:pd.DataFrame()}
            else:
                long_fix = generate_long_signal(long_pct, {future_window: base_model_param[fix_tag][future_window]},
                                            start, end, f'{signal_path}/{fix_tag}/long/')
            long_930 = generate_long_signal(long_pct, {future_window:base_model_param[tag_930][future_window]},
                                            start, end, f'{signal_path}/{tag_930}/long/')
            long_930 = long_930[future_window].swaplevel(0, 1).loc[1455]
            long_930.index = pd.MultiIndex.from_tuples([(get_pre_trade_date(x, -1), 930) for x in long_930.index])
            date_fix = set([x[0] for x in long_fix[future_window].index])
            date_930 = set([x[0] for x in long_930.index])
            inter_date_list = sorted(list(date_fix.intersection(date_930)))
            long_signal[future_window] = pd.concat([long_fix[future_window],
                                long_930]).sort_index().loc[inter_date_list[0]:inter_date_list[-1]]
            print(inter_date_list[0],inter_date_list[-1])

            # long_signal = {x:long_signal[x].loc[inter_date_list[0]:inter_date_list[-1]] for x in long_signal}
            pd.to_pickle(long_signal[future_window], long_path)
        else:
            print(long_path,'exists')
            long_signal[future_window] = pd.read_pickle(long_path)
        if future_window>8:
            continue
        if not os.path.exists(short_path):
            if not os.path.exists(os.path.split(short_path)[0]):
                os.makedirs(os.path.split(short_path)[0])
            short_fix = generate_short_signal(short_pct, {future_window: base_model_param[fix_tag][future_window]},
                                              start, end, f'{signal_path}/{fix_tag}/short/')
            short_930 = generate_short_signal(short_pct, {future_window: base_model_param[tag_930][future_window]},
                                              start, end, f'{signal_path}/{tag_930}/short/')
            short_930 = short_930[future_window].swaplevel(0, 1).loc[1455]
            short_930.index = pd.MultiIndex.from_tuples([(get_pre_trade_date(x, -1), 930) for x in short_930.index])

            date_fix = set([x[0] for x in short_fix[future_window].index])
            date_930 = set([x[0] for x in short_930.index])
            inter_date_list = sorted(list(date_fix.intersection(date_930)))

            short_signal[future_window] = pd.concat([short_fix[future_window], short_930]).sort_index().loc[inter_date_list[0]:inter_date_list[-1]]
            print(inter_date_list[0],inter_date_list[-1])
            pd.to_pickle(short_signal[future_window], short_path)
        else:
            print(short_path, 'exist')
            short_signal[future_window] = pd.read_pickle(short_path)

    return long_signal,short_signal,final_tag

base_model_param = {
    'XGB_DTC_Matrix_Light_Cat': {
        x: [
                f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelectedMDDImproveV8BarWith1DayLabel_20220216_keep5OriginFactor/SWMeanFuture_{x}_bar/XGB_SWMean_ic_d_train200_test10_factor_num400/XGB_SWMean_ic_d_train200_test10_factor_num400/',
                f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelectedMDDImproveV8BarWith1DayLabel_20220216_keep5OriginFactor/SWMeanFuture_{x}_bar/XGB_SWMean_ic_t_train200_test10_factor_num400/XGB_SWMean_ic_t_train200_test10_factor_num400/',
                f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelectedMDDImproveV8BarWith1DayLabel_20220216_keep5OriginFactor/SWMeanFuture_{x}_bar/XGB_SWMean_ic_c_train200_test10_factor_num400/XGB_SWMean_ic_c_train200_test10_factor_num400/',
                f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelectedMDDImproveV8BarWith1DayLabel_20220216_keep5OriginFactor/Future_{x}_bar/XGBV4ReversalResReselect_ic_d_train200_test10_factor_num400/XGBV4ReversalResReselect_ic_d_train200_test10_factor_num400/',
                f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelectedMDDImproveV8BarWith1DayLabel_20220216_keep5OriginFactor/Future_{x}_bar/XGBV4ReversalResReselect_ic_t_train200_test10_factor_num400/XGBV4ReversalResReselect_ic_t_train200_test10_factor_num400/',
                f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelectedMDDImproveV8BarWith1DayLabel_20220216_keep5OriginFactor/Future_{x}_bar/XGBV4ReversalResReselect_ic_c_train200_test10_factor_num400/XGBV4ReversalResReselect_ic_c_train200_test10_factor_num400/',
                f'/data/group/800442/800319/wyl/model_record/nonfix/future_{x}_bar/lightgbm_all_sample_ic_all_t/',
                f'/data/group/800442/800319/wyl/model_record/nonfix/future_{x}_bar/catboost_all_sample_ic_all_t/'
        ] for x in range(1, 9)[::-1]
    },

'XGB_DTC_Matrix_Light_Cat_XGBClipDiff': {
        x: [
                f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelectedMDDImproveV8BarWith1DayLabel_20220216_keep5OriginFactor/SWMeanFuture_{x}_bar/XGB_SWMean_ic_d_train200_test10_factor_num400/XGB_SWMean_ic_d_train200_test10_factor_num400/',
                f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelectedMDDImproveV8BarWith1DayLabel_20220216_keep5OriginFactor/SWMeanFuture_{x}_bar/XGB_SWMean_ic_t_train200_test10_factor_num400/XGB_SWMean_ic_t_train200_test10_factor_num400/',
                f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelectedMDDImproveV8BarWith1DayLabel_20220216_keep5OriginFactor/SWMeanFuture_{x}_bar/XGB_SWMean_ic_c_train200_test10_factor_num400/XGB_SWMean_ic_c_train200_test10_factor_num400/',
                f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelectedMDDImproveV8BarWith1DayLabel_20220216_keep5OriginFactor/Future_{x}_bar/XGBV4ReversalResReselect_ic_d_train200_test10_factor_num400/XGBV4ReversalResReselect_ic_d_train200_test10_factor_num400/',
                f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelectedMDDImproveV8BarWith1DayLabel_20220216_keep5OriginFactor/Future_{x}_bar/XGBV4ReversalResReselect_ic_t_train200_test10_factor_num400/XGBV4ReversalResReselect_ic_t_train200_test10_factor_num400/',
                f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelectedMDDImproveV8BarWith1DayLabel_20220216_keep5OriginFactor/Future_{x}_bar/XGBV4ReversalResReselect_ic_c_train200_test10_factor_num400/XGBV4ReversalResReselect_ic_c_train200_test10_factor_num400/',
                f'/data/group/800442/800319/wyl/model_record/nonfix/future_{x}_bar/lightgbm_all_sample_ic_all_t/',
                f'/data/group/800442/800319/wyl/model_record/nonfix/future_{x}_bar/catboost_all_sample_ic_all_t/',
            f'/data/group/800442/800319/Faamonitor/PL/FeatureEngineering/DiffExtraClip/Future_{x}_bar/XGBV4ReversalResReselect_ic_d_train200_test10_factor_num400/XGBV4ReversalResReselect_ic_d_train200_test10_factor_num400/',
            f'/data/group/800442/800319/Faamonitor/PL/FeatureEngineering/DiffExtraClip/Future_{x}_bar/XGBV4ReversalResReselect_ic_t_train200_test10_factor_num400/XGBV4ReversalResReselect_ic_t_train200_test10_factor_num400/',
            f'/data/group/800442/800319/Faamonitor/PL/FeatureEngineering/DiffExtraClip/Future_{x}_bar/XGBV4ReversalResReselect_ic_c_train200_test10_factor_num400/XGBV4ReversalResReselect_ic_c_train200_test10_factor_num400/',

        ] for x in range(8, 9)
    },

    f'XGB_DTC': {x:
        [
            f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelectedMDDImproveV8BarWith1DayLabel_20220216_keep5OriginFactor/Future_{x}_bar/XGBV4ReversalResReselect_ic_d_train200_test10_factor_num400/XGBV4ReversalResReselect_ic_d_train200_test10_factor_num400/',
            f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelectedMDDImproveV8BarWith1DayLabel_20220216_keep5OriginFactor/Future_{x}_bar/XGBV4ReversalResReselect_ic_t_train200_test10_factor_num400/XGBV4ReversalResReselect_ic_t_train200_test10_factor_num400/',
            f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelectedMDDImproveV8BarWith1DayLabel_20220216_keep5OriginFactor/Future_{x}_bar/XGBV4ReversalResReselect_ic_c_train200_test10_factor_num400/XGBV4ReversalResReselect_ic_c_train200_test10_factor_num400/',
        ] for x in range(1, 9)
    },

f'XGB_DTC_DiffClip': {x:
        [
            f'/data/group/800442/800319/Faamonitor/PL/FeatureEngineering/DiffExtraClip/Future_{x}_bar/XGBV4ReversalResReselect_ic_d_train200_test10_factor_num400/XGBV4ReversalResReselect_ic_d_train200_test10_factor_num400/',
            f'/data/group/800442/800319/Faamonitor/PL/FeatureEngineering/DiffExtraClip/Future_{x}_bar/XGBV4ReversalResReselect_ic_t_train200_test10_factor_num400/XGBV4ReversalResReselect_ic_t_train200_test10_factor_num400/',
            f'/data/group/800442/800319/Faamonitor/PL/FeatureEngineering/DiffExtraClip/Future_{x}_bar/XGBV4ReversalResReselect_ic_c_train200_test10_factor_num400/XGBV4ReversalResReselect_ic_c_train200_test10_factor_num400/',
        ] for x in range(8, 9)
    },

    'XGBReversalRes_DTC': {x: [
        f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelectedMDDImprove8BarReversalRes/Future_{x}_bar/XGBV4ReversalResReselect_ic_d_train200_test10_factor_num400/XGBV4ReversalResReselect_ic_d_train200_test10_factor_num400/',
        f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelectedMDDImprove8BarReversalRes/Future_{x}_bar/XGBV4ReversalResReselect_ic_t_train200_test10_factor_num400/XGBV4ReversalResReselect_ic_t_train200_test10_factor_num400/',
        f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelectedMDDImprove8BarReversalRes/Future_{x}_bar/XGBV4ReversalResReselect_ic_c_train200_test10_factor_num400/XGBV4ReversalResReselect_ic_c_train200_test10_factor_num400/',
    ] for x in range(1, 9)},

    'XGB_Min5_DTC': {
        x: [
            f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/NonFix8BarWith930Use5Mins/Future_{x}_bar/XGB_5mins_ic_d_train200_test10_factor_num400/XGB_5mins_ic_d_train200_test10_factor_num400/',
            f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/NonFix8BarWith930Use5Mins/Future_{x}_bar/XGB_5mins_ic_t_train200_test10_factor_num400/XGB_5mins_ic_t_train200_test10_factor_num400/',
            f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/NonFix8BarWith930Use5Mins/Future_{x}_bar/XGB_5mins_ic_c_train200_test10_factor_num400/XGB_5mins_ic_c_train200_test10_factor_num400/',
        ] for x in range(1, 9)
    },

'XGB_Min5_DTC707': {
        x: [
            f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/NonFix8BarWith930Use5Mins_707/Future_{x}_bar/XGB_5mins_ic_d_train200_test10_factor_num400/XGB_5mins_ic_d_train200_test10_factor_num400/',
            f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/NonFix8BarWith930Use5Mins_707/Future_{x}_bar/XGB_5mins_ic_t_train200_test10_factor_num400/XGB_5mins_ic_t_train200_test10_factor_num400/',
            f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/NonFix8BarWith930Use5Mins_707/Future_{x}_bar/XGB_5mins_ic_c_train200_test10_factor_num400/XGB_5mins_ic_c_train200_test10_factor_num400/',
        ] for x in range(1, 9)
    },

'XGB_Min5_DTC707V20220330': {
        x: [
            f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/NonFix8BarWith930Use5Mins_707V20220330/Future_{x}_bar/XGB_5mins_ic_d_train200_test10_factor_num400/XGB_5mins_ic_d_train200_test10_factor_num400/',
            f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/NonFix8BarWith930Use5Mins_707V20220330/Future_{x}_bar/XGB_5mins_ic_t_train200_test10_factor_num400/XGB_5mins_ic_t_train200_test10_factor_num400/',
            f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/NonFix8BarWith930Use5Mins_707V20220330/Future_{x}_bar/XGB_5mins_ic_c_train200_test10_factor_num400/XGB_5mins_ic_c_train200_test10_factor_num400/',
        ] for x in range(1, 10)
    },
    'XGB_D_TTCOVER_DROP':{
        8:[
f'/data/group/800442/800319/IntraExp/MDDPeriodFactorInfluence/DropByFIRetrain_total_cover_roll/Future_8_bar/XGB_ic_d_train200_test10_factor_num400_drop0/XGB_ic_d_train200_test10_factor_num400_drop0/'
        ]
    }



}



signal_path = '/data/user/015664/AFuckingTrigger/限制买入和持仓/NonFix信号存储/'

if __name__ == '__main__':
    # tag = 'XGB_Min5_DTC707'
    tag = 'XGB_Min5_DTC707V20220330'
    # tag = 'XGB_Min5_DTC'
    # tag = 'XGB_DTC'
    # tag = 'XGB_DTC_Matrix_Light_Cat'
    start, end = 20161026, 20211130
    # from xquant.compute.aimr import AIMR
    long_threshold = 0.05#eval(AIMR.getParam())
    generate_long_signal(long_threshold, base_model_param[tag],start,end, f'{signal_path}/{tag}/long/')
    # generate_short_signal(0, base_model_param[tag],start,end, f'{signal_path}/{tag}/short/')



