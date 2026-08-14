# @Time : 2022/6/13 8:20
# @Author : Zhichen Lu
# @File : summary.py
import pandas as pd
from dataApi.sendInfo import send_message,send_file

mession = {}
mession['每日训练日期更新']={
    '说明':'更新历史训练、测试日期',
    '代码文件':'ensemblemonitor-strategy-python/daily_update/period_info_update.py',
    '时间':'6:00',
    '内存':'5G',
    'CPU':'1核'
}
mession['早盘生成组合文件、拷贝调仓参数']={
    '说明':'',
    '代码文件':'ensemblemonitor-strategy-python/NonFixWindow/daily_generate_paramCondition/stk_list_list_update_nonfix.py',
    '时间':'7:45',
    '内存':'5G',
    'CPU':'1核'
}

mession['拷贝python实盘策略到实盘环境']={
    '说明':'线下先模拟运行确认无误后再上传',
    '代码文件':'ensemblemonitor-strategy-python/OnlineTool/Copy2XtraderTesNonFix.py',
    '时间':'8:05',
    '内存':'15G',
    'CPU':'1核'
}
mession['每天更新矩阵处理因子']={
    '说明':'用前一日行业矩阵处理前一日fix因子后存储',
    '代码文件':'MillenniumFalcon/run_aimr_MatrixFactor.py \n MillenniumFalcon/getMatrixNoReadingShift.py',
    '时间':'8:35',
    '内存':'1G',
    'CPU':'1核'
}
mession['NonFix_XGBMatrix_每日更新']={
    '说明':'矩阵训练模型更新XGB 日常同步线下预测、模型更新日晚上740手动运行',
    '代码文件':'ensemblemonitor-strategy-python/NonFixWindow/DailyTracingFilterProbFactorTheta/XGBMonthlyCrossFixSameSWMeanOnlyEarlySignalContain1DayFutureFilterFactorOnline.py',
    '时间':'9:00',
    '内存':'80G',
    'CPU':'2核'
}

mession['更新XGB']={
    '说明':'更新XGB、模型更新日晚上740手动运行',
    '代码文件':'ensemblemonitor-strategy-python/NonFixWindow/DailyTracingFilterProbFactorTheta/XGBMonthlyEarlySignalContain1DayFuture8Bar_keep5OriginFactorFilterFactorOnline.py',
    '时间':'9:00',
    '内存':'80G',
    'CPU':'2核'
}

mession['每天生成问题因子列表']={
    '说明':'每天剔除最近一段时间线上线下相关性差异较大的因子',
    '代码文件':'ensemblemonitor-strategy-python/data_analysis/FactorComparing.py',
    '时间':'9:30',
    '内存':'80G',
    'CPU':'10核'
}


mession['每日线上线下比对']={
    '说明':'对比截止至T-1日线上线下回测结果',
    '代码文件':'ensemblemonitor-strategy-python/NonFixWindow/daily_generate_paramCondition/run_backtest_nonfixwindow_8barOnlineTracing8modelThetaCondition.py',
    '时间':'9:40',
    '内存':'50G',
    'CPU':'8核'
}

mession['股票池更新']={
    '说明':'回测过程中读取股票池至T日',
    '代码文件':'ensemblemonitor-strategy-python/daily_update/daily_stock_pool_update.py',
    '时间':'17:53',
    '内存':'40G',
    'CPU':'1核'
}


mession['成交价更新']={
    '说明':'更新用于回测的成交价至T日',
    '代码文件':'StrongStockModel/backtest/StrategyBackTest/load_basic_file/prepare_deal_price.py',
    '时间':'1900',
    '内存':'100G',
    'CPU':'2核'
}

mession['复权成交量更新']={
    '说明':'更新用于回测的线下复权成交量至T日',
    '代码文件':'StrongStockModel/backtest/StrategyBackTest/load_basic_file/load_vol_calc_adj.py',
    '时间':'1900',
    '内存':'120G',
    'CPU':'4核'
}


mession['每天生成NonFix标签']={
    '说明':'每天更新用于训练的30min~240min标签，更新至T-1日的标签',
    '代码文件':'StrongStockModel/NonFixWindow/LableGeneration/run_aimr_label_generation.py \n StrongStockModel/NonFixWindow/LableGeneration/IntradayLabel_Bar8.py',
    '时间':'19:33',
    '内存':'1G',
    'CPU':'1核'
}

mession['实盘_每天生成关系矩阵']={
    '说明':'生成次日用于实盘的关系矩阵',
    '代码文件':'ensemblemonitor-strategy-python/NonFixWindow/daily_generate_paramCondition/IndustryMatrixDailyUpdateNonFix.py',
    '时间':'20::00',
    '内存':'10G',
    'CPU':'1核'
}


mession['NonFix_930成交量和ratio生成']={
    '说明':'生成持仓重合部分930和FIX策略所占比例',
    '代码文件':'ensemblemonitor-strategy-python/NonFixWindow/daily_generate_paramCondition/daily_update_pre_night930ratio.py',
    '时间':'20::00',
    '内存':'20G',
    'CPU':'1核'
}


mession['每日生成实盘条件终止条件']={
    '说明':'生成用于次日实盘的盘中终止条件',
    '代码文件':'ensemblemonitor-strategy-python/NonFixWindow/daily_generate_paramCondition/daily_prepareConditionForNonFix2.py',
    '时间':'20:00',
    '内存':'20G',
    'CPU':'2核'
}

mession['每天更新次日减半行业股票列表及近5日成交量均值']={
    '说明':'',
    '代码文件':'ensemblemonitor-strategy-python/NonFixWindow/daily_generate_paramCondition/AmtClipNonFix.py',
    '时间':'20:00',
    '内存':'16G',
    'CPU':'4核'
}
mession['更新盘前因子均值标准差']={
    '说明':'',
    '代码文件':'ensemblemonitor-strategy-python/NonFixWindow/daily_generate_paramCondition/offline_daily_update_nonfix.py',
    '时间':'06:40',
    '内存':'40G',
    'CPU':'10核'
}


online_codes = {}

online_codes['当前线上版本实盘代码(非固定窗口+日内条件)']= 'ensemblemonitor-strategy-python/ApplicationNonFixCondition.py'
online_codes['930时点代码']= 'ensemblemonitor-strategy-python/Application930ForMixNonFix.py'
online_codes['线下模拟回放']= 'ensemblemonitor-strategy-python/NonFixWindow/main_online_NonFixCondition.py'
online_codes['实盘每天线下统计']= 'ensemblemonitor-strategy-python/NonFixWindow/daily_generate_paramCondition/OnlineStatWith930_20220422NonFix.py'
online_codes['实盘每天线下统计']= 'ensemblemonitor-strategy-python/NonFixWindow/daily_generate_paramCondition/OnlineStatWith930_20220422NonFix.py'


offline_code = {}
offline_code['非固定时点回测框架+日内终止条件V4执行文件'] = 'StrongStockModel/NonFixWindow/backtest/run_backtest_by_api_signa/run_backtest_nonfixwindow_8barExtraContidionAIMRPctV4_2_1.py'
offline_code['非固定窗口框架'] = 'StrongStockModel/backtest/StrategyBackTest/DerivativeStrategy/StartWithLimitCashVolConsiderNonFixSignal8BarExtraContition.py'
offline_code['XGB 矩阵处理非固定窗口历史训练'] = 'StrongStockModel/NonFixWindow/OnlineModelReTrain/FilterProblemFactor/XGBMonthlyCrossFixSameSWMeanOnlyEarlySignalContain1DayFutureFilterFactor.py'
offline_code['XGB非固定窗口历史训练'] = 'StrongStockModel/NonFixWindow/OnlineModelReTrain/FilterProblemFactor/XGBMonthlyEarlySignalContain1DayFuture8Bar_keep5OriginFactorFilterFactor.py'
offline_code['择时新版本框架回测'] = 'R2D2/ChangingCash/StartWithLimitCashVolConsiderNonFixSignal8BarExtraContitionChangingCashByRatioLimitShortLongV1.py'
offline_code['择时新版本框架回测_执行文件(不含日内条件)'] = 'R2D2/ChangingCash/DifferentFrameCompare/run_backtest_nonfixwindow_8barExtraContidionChangableCashByRatioLimitShortLongValMannualSignal.py'
offline_code['择时新版本框架回测(含日内条件)'] = 'R2D2/ChangingCash/StartWithLimitCashVolConsiderNonFixSignal8BarExtraContitionChangingCashByRatioLimitShortLongV1.py'
offline_code['择时新版本框架回测_执行文件(含日内条件)'] = 'R2D2/ChangingCash/DifferentFrameCompare/run_backtest_nonfixwindow_8barExtraContidionChangableCashByRatioLimitShortLongValMannualSignalCondition.py'

offline_code = pd.Series(offline_code)
offline_code.index = pd.MultiIndex.from_tuples([('实盘相关',x) for x in offline_code.index])
online_codes = pd.Series(online_codes)
online_codes.index = pd.MultiIndex.from_tuples([('线下回测训练',x) for x in online_codes.index])

mession = pd.DataFrame(mession).T
file_name = './交接清单.xlsx'
with pd.ExcelWriter(file_name) as writer:
    mession.to_excel(writer,sheet_name='定时任务')
    pd.concat([online_codes,offline_code]).to_excel(writer,sheet_name='线下研究')
send_file(['015664'],file_name)


#
# mession['']={
#     '说明':'',
#     '代码文件':'',
#     '时间':'',
#     '内存':'G',
#     'CPU':'核'
# }
# mession['']={
#     '说明':'',
#     '代码文件':'',
#     '时间':'',
#     '内存':'G',
#     'CPU':'核'
# }







