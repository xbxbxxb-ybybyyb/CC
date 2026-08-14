# coding: utf-8
# Author：fengchi863
# Date ：2021/1/15 14:20

import pandas as pd, numpy as np
from ShortTermTrading.Util.tools import get_stock_name_dict
from ShortTermTrading.dataApi.stockList import trans_int2windcode, trans_windcode2int
from ShortTermTrading.conf.path_conf import man_made_concept_data_path
from ShortTermTrading.dataApi import tradeDate, stockList
from xquant.factordata import FactorData

workmate_dict = {
    '陈慧丽': '003186',
    '冯炽': 'fengchi',
    '刘昌易': '011669',
    '张旭帆': '015630',
    '陶鑫': '015624',
    '陆威玮': '003376',
    '邵柯楠': '011670',
    '徐琪': '015628'
}

def get_minutely_df_true(df: pd.DataFrame):
    df = (df * 1.0)[df]
    df = df.groupby('date').cumsum() == 1 # 只有第一次触发
    df = df.stack()[df.stack()]
    df = df.reset_index(drop=False)
    df.columns = ['date', 'time', 'stk_id', 'True']
    return df

def get_daily_df_true(df: pd.DataFrame):
    df = df.stack()[df.stack()]
    df = df.reset_index(drop=False)
    df.columns = ['date', 'stk_id', 'True']
    return df

def check_shape(*df_list):
    if len(df_list) == 0:
        return
    for df in df_list:
        print(df.shape)
        assert df.shape == df_list[0].shape

# 必须包含stk_id这一列
def add_stock_name(df: pd.DataFrame):
    stk_code_name_dict = get_stock_name_dict()
    df['stock_name'] = df['stk_id'].apply(lambda x: stk_code_name_dict[trans_int2windcode(x)]
        if trans_int2windcode(x) in stk_code_name_dict.keys() else np.nan)
    return df

def fetch_man_made_monitor_list(kind='all'):
    # 前一天的监控表格，徐琪每天下午四点更新
    monitor_concept_df = pd.read_excel(man_made_concept_data_path)
    monitor_concept_df = monitor_concept_df[monitor_concept_df['Unnamed: 0'] != 'A20132.SH']
    monitor_concept_df['主题'] = monitor_concept_df['概念板块'] + '_' + monitor_concept_df['子主题']
    if kind == 'all':
        monitor_concept_stk_list = monitor_concept_df['Unnamed: 0'].apply(lambda x: trans_windcode2int(x))
        return monitor_concept_stk_list

def get_latest_yugao(type=None, early_year=20201231):
    fd = FactorData()
    yugao_table_name = 'AShareProfitNotice'
    raw_yugao_df = fd.get_factor_value('WIND_' + yugao_table_name,
                                       S_PROFITNOTICE_PERIOD=['>=%d' % early_year, '<=20211231'])
    col = ['S_INFO_WINDCODE', 'S_PROFITNOTICE_FIRSTANNDATE', 'S_PROFITNOTICE_DATE', 'S_PROFITNOTICE_PERIOD',
           'S_PROFITNOTICE_STYLE', 'S_PROFITNOTICE_SIGNCHANGE', 'S_PROFITNOTICE_ABSTRACT', 'S_PROFITNOTICE_CHANGEMIN',
           'S_PROFITNOTICE_CHANGEMAX', 'S_PROFITNOTICE_NET_PARENT_FIRM']
    raw_yugao_df = raw_yugao_df[col]
    if type == 'all':
        raw_yugao_df = raw_yugao_df[raw_yugao_df['S_PROFITNOTICE_PERIOD'].astype(int) % 10000 == 1231]
    elif type == 'q1':
        raw_yugao_df = raw_yugao_df[raw_yugao_df['S_PROFITNOTICE_PERIOD'].astype(int) % 10000 == 331]
    rename_dict = {'S_INFO_WINDCODE': '股票代码',
                   'S_PROFITNOTICE_FIRSTANNDATE': '预告首次公告日',
                   'S_PROFITNOTICE_DATE': '预告公告日',
                   'S_PROFITNOTICE_PERIOD': '预告报告期',
                   'S_PROFITNOTICE_STYLE': '预告类型',
                   'S_PROFITNOTICE_SIGNCHANGE': '是否变脸',
                   'S_PROFITNOTICE_ABSTRACT': '预告摘要',
                   'S_PROFITNOTICE_CHANGEMIN':'变动幅度上限',
                   'S_PROFITNOTICE_CHANGEMAX':'变动幅度下限',
                   'S_PROFITNOTICE_NETPROFITMIN': '净利润下限',
                   'S_PROFITNOTICE_NETPROFITMAX': '净利润上限',
                   'S_PROFITNOTICE_NET_PARENT_FIRM': '去年同期归母净利润'}
    raw_yugao_df = raw_yugao_df.rename(columns=rename_dict)

    yugao_kind_dict = {454001000: '不确定',
                       454002000: '略减',
                       454003000: '略增',
                       454004000: '扭亏',
                       454005000: '其他',
                       454006000: '首亏',
                       454007000: '续亏',
                       454008000: '续盈',
                       454009000: '预减',
                       454010000: '预增',
                       }
    raw_yugao_df['预告类型'] = raw_yugao_df['预告类型'].apply(lambda x: yugao_kind_dict[x])
    raw_yugao_df['变动幅度'] = raw_yugao_df['变动幅度上限'].astype(str) + '%至' + raw_yugao_df['变动幅度下限'].astype(str) + '%'

    date_list = tradeDate.get_date_range(20140101, 20211231)
    raw_yugao_df['年份'] = raw_yugao_df['预告报告期'].astype(int) // 10000

    if type == 'all':
        raw_yugao_df['预告首次公告日'] = raw_yugao_df[['预告首次公告日', '预告公告日', '年份']].apply(
            lambda x: _get_true_yugao_report_date(x['预告首次公告日'], x['预告公告日'], x['年份']), axis=1
        )
        raw_yugao_df = raw_yugao_df[raw_yugao_df['预告首次公告日'] != False]

    # 添加交易日
    raw_yugao_df['预告首次交易日'] = raw_yugao_df['预告首次公告日'].apply(lambda x: min([y for y in date_list if y >= int(x)]))
    # 添加股票名
    stk_code_name_dict = get_stock_name_dict()
    raw_yugao_df['股票名称'] = raw_yugao_df['股票代码'].apply(lambda x: stk_code_name_dict[stockList.trans_int2windcode(x)]
        if stockList.trans_int2windcode(x) in stk_code_name_dict.keys() else x)

    raw_yugao_df = raw_yugao_df.sort_values(['预告首次公告日'])
    return raw_yugao_df

def get_latest_nianbao(type=None, early_year=20201231):
    if type == 'all':
        report_date = 1231
    elif type == 'q1':
        report_date = 331
    # TODO
    fd = FactorData()
    date_predict_table_name = 'AShareIssuingDatePredict'
    raw_date_predict = fd.get_factor_value('WIND_' + date_predict_table_name,
                                           report_period=['>=%d' % early_year, '<=20211231'])
    col = ['S_INFO_WINDCODE', 'REPORT_PERIOD', 'S_STM_PREDICT_ISSUINGDATE', 'S_STM_ACTUAL_ISSUINGDATE']
    raw_date_predict = raw_date_predict[col]
    raw_date_predict = raw_date_predict[raw_date_predict['REPORT_PERIOD'].astype(int) % 10000 == report_date]
    rename_dict = {'S_INFO_WINDCODE': '股票代码',
                   'REPORT_PERIOD': '报告期',
                   'S_STM_PREDICT_ISSUINGDATE': '年报预计披露日',
                   'S_STM_ACTUAL_ISSUINGDATE': '年报实际披露日'
                   }
    raw_date_predict = raw_date_predict.rename(columns=rename_dict)

    # # 添加股票名
    # stk_code_name_dict = get_stock_name_dict()
    # raw_date_predict['股票名称'] = raw_date_predict['股票代码'].apply(lambda x: stk_code_name_dict[stockList.trans_int2windcode(x)]
    #             if stockList.trans_int2windcode(x) in stk_code_name_dict.keys() else x)

    date_list = tradeDate.get_date_range(20140101, 20211231)
    # 添加交易日
    raw_date_predict['年报实际披露日首次交易日'] = raw_date_predict['年报实际披露日'].apply(lambda x: min(
        [y for y in date_list if y >= int(x)]) if x == x else np.nan)
    raw_date_predict['年份'] = raw_date_predict['报告期'].astype(int) // 10000

    return raw_date_predict

def get_latest_kuaibao(early_year=20201231):
    fd = FactorData()
    kuaibao_table_name = 'AShareProfitExpress'
    raw_kuaibao_df = fd.get_factor_value('WIND_' + kuaibao_table_name,
                                         report_period=['>=%d' % early_year, '<=20211231'])
    col = ['S_INFO_WINDCODE', 'REPORT_PERIOD', 'ANN_DT', 'OPER_PROFIT', 'S_FA_YOYSALES', 'S_FA_YOYNETPROFIT_DEDUCTED',
           'BRIEF_PERFORMANCE']
    raw_kuaibao_df = raw_kuaibao_df[col]
    raw_kuaibao_df = raw_kuaibao_df[raw_kuaibao_df['REPORT_PERIOD'].astype(int) % 10000 == 1231]
    rename_dict = {'S_INFO_WINDCODE': '股票代码',
                   'REPORT_PERIOD': '报告期',
                   'ANN_DT': '快报公告日',
                   'S_FA_YOYSALES': '快报营业收入同比',
                   'S_FA_YOYNETPROFIT_DEDUCTED': '快报归母利润同比',
                   'BRIEF_PERFORMANCE': '快报摘要'
                   }
    raw_kuaibao_df = raw_kuaibao_df.rename(columns=rename_dict)
    raw_kuaibao_df['年份'] = raw_kuaibao_df['报告期'].astype(int) // 10000
    date_list = tradeDate.get_date_range(20140101, 20211231)
    # 添加交易日
    raw_kuaibao_df['快报公告首次交易日'] = raw_kuaibao_df['快报公告日'].apply(lambda x: min([y for y in date_list if y >= int(x)]))
    return raw_kuaibao_df

def _get_true_yugao_report_date(a1, a2, a3):
    if type(a1) == str:
        a1 = int(a1)
    if type(a2) == str:
        a2 = int(a2)
    early_report_date = a3 * 10000 + 1201
    late_report_date = (a3 + 1) * 10000 + 131
    if late_report_date >= a1 >= early_report_date:
        return a1
    elif (a1 < early_report_date) and (early_report_date <= a2 <= late_report_date):
        return a2
    else:
        return False

# 增加朝阳永续一致预期数据
def get_cfs_c4_data(date):
    s = FactorData()
    trading_day = s.tradingday(20201101, date)
    cfs = s.get_factor_value('Basic_factor', mddate=trading_day, factor_names=['cfs_c4', 'cfs_c4_type'])
    cfs = cfs[cfs['rpt_date']==2020]
    cfs = cfs.reset_index()
    cfs['stock'] = cfs['stock'].map(int)
    cfs['cfs_c4'] = cfs['cfs_c4'] / 10000
    cfs = cfs.set_index(['stock', 'rpt_date', 'mddate'])
    return cfs

def get_eod_data(date):
    fd = FactorData()
    profit_table = 'AShareEODDerivativeIndicator'
    profit_df = fd.get_factor_value('WIND_' + profit_table,
                                     TRADE_DT=[str(date)])
    col = ['S_INFO_WINDCODE', 'TRADE_DT', 'NET_PROFIT_PARENT_COMP_LYR', 'NET_PROFIT_PARENT_COMP_TTM', 'S_VAL_MV']
    profit_df = profit_df[col]
    rename_dict = {'S_INFO_WINDCODE': '股票代码',
                   'TRADE_DT': '交易日期',
                   'NET_PROFIT_PARENT_COMP_LYR': '去年归母净利润',
                   'NET_PROFIT_PARENT_COMP_TTM': '年报归母净利润',
                   'S_VAL_MV': '总市值'
                   }
    profit_df = profit_df.rename(columns=rename_dict)
    profit_df['去年归母净利润'] = profit_df['去年归母净利润'].astype(int) / 1e8
    profit_df['年报归母净利润'] = profit_df['年报归母净利润'].astype(int) / 1e8
    profit_df['总市值'] = profit_df['总市值'].apply(lambda x: int(x) / 1e4 if not np.isnan(x) else np.nan)
    profit_df = profit_df.set_index('股票代码')
    return profit_df