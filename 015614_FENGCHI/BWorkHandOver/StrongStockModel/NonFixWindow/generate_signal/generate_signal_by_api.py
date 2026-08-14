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

base_model_param = {
    'XGB_DTC_Matrix_Light_Cat': {
        x: [
                f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelectedMDDImproveV8BarWith1DayLabel_20220216_keep5OriginFactor/SWMeanFuture_{x}_bar/XGB_SWMean_ic_d_train200_test10_factor_num400/XGB_SWMean_ic_d_train200_test10_factor_num400/',
                f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelectedMDDImproveV8BarWith1DayLabel_20220216_keep5OriginFactor/SWMeanFuture_{x}_bar/XGB_SWMean_ic_t_train200_test10_factor_num400/XGB_SWMean_ic_t_train200_test10_factor_num400/',
                f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelectedMDDImproveV8BarWith1DayLabel_20220216_keep5OriginFactor/SWMeanFuture_{x}_bar/XGB_SWMean_ic_c_train200_test10_factor_num400/XGB_SWMean_ic_c_train200_test10_factor_num400/',
                f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelectedMDDImproveV8BarWith1DayLabel_20220216_keep5OriginFactor/Future_{x}_bar/XGBV4ReversalResReselect_ic_d_train200_test10_factor_num400/XGBV4ReversalResReselect_ic_d_train200_test10_factor_num400/',
                f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelectedMDDImproveV8BarWith1DayLabel_20220216_keep5OriginFactor/Future_{x}_bar/XGBV4ReversalResReselect_ic_t_train200_test10_factor_num400/XGBV4ReversalResReselect_ic_t_train200_test10_factor_num400/',
                f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelectedMDDImproveV8BarWith1DayLabel_20220216_keep5OriginFactor/Future_{x}_bar/XGBV4ReversalResReselect_ic_c_train200_test10_factor_num400/XGBV4ReversalResReselect_ic_c_train200_test10_factor_num400/',
                f'/data/group/800442/800319/wyl/model_record/nonfix/future_{x}_bar/lightgbm_in_sample_ic_all_t/',
                f'/data/group/800442/800319/wyl/model_record/nonfix/future_{x}_bar/catboost_in_sample_ic_all_t/'
        ] for x in range(1, 9)
    },
    f'XGB_DTC': {x:
        [
            f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelectedMDDImproveV8BarWith1DayLabel_20220216_keep5OriginFactor/Future_{x}_bar/XGBV4ReversalResReselect_ic_d_train200_test10_factor_num400/XGBV4ReversalResReselect_ic_d_train200_test10_factor_num400/',
            f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelectedMDDImproveV8BarWith1DayLabel_20220216_keep5OriginFactor/Future_{x}_bar/XGBV4ReversalResReselect_ic_t_train200_test10_factor_num400/XGBV4ReversalResReselect_ic_t_train200_test10_factor_num400/',
            f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelectedMDDImproveV8BarWith1DayLabel_20220216_keep5OriginFactor/Future_{x}_bar/XGBV4ReversalResReselect_ic_c_train200_test10_factor_num400/XGBV4ReversalResReselect_ic_c_train200_test10_factor_num400/',
        ] for x in range(1, 9)
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
        ] for x in range(2, 8)
    },

}
signal_path = '/data/user/015664/AFuckingTrigger/限制买入和持仓/NonFix信号存储/'

if __name__ == '__main__':
    # tag = 'XGB_Min5_DTC'
    # tag = 'XGB_DTC'
    tag = 'XGB_DTC_Matrix_Light_Cat'
    start, end = 20161026, 20211130
    from xquant.compute.aimr import AIMR
    long_threshold = eval(AIMR.getParam())
    generate_long_signal(long_threshold, base_model_param[tag],start,end, f'{signal_path}/{tag}/long/')
    # generate_short_signal(0, base_model_param[tag],start,end, f'{signal_path}/{tag}/short/')
