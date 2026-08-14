import numpy as np
import pandas as pd
import decimal

def get_time_delta(itime):
    mls = int(str(int(itime))[-3:])
    s = int(str(int(itime))[-5:-3])
    m = int(str(int(itime))[-7:-5])
    h = int(str(int(itime))[:-7])
    time_mls = h * 3600 * 1000 + m * 60 * 1000 + s * 1000 + mls
    time_mls_900 = 9 * 3600 * 1000
    if int(itime) > 120000000:
        time_delta = time_mls - time_mls_900 - 5400000
    else:
        time_delta = time_mls - time_mls_900
    return time_delta
def round_(x, n=0):
    x = x + 1e-10
    if n > 0:
        res = float(decimal.Decimal(str(x)).quantize(decimal.Decimal('0.%s1' % ('0' * (n - 1))),
                                                     rounding=decimal.ROUND_HALF_UP))
    else:
        res = int(decimal.Decimal(str(x)).quantize(decimal.Decimal('1'), rounding=decimal.ROUND_HALF_UP))
    return res

dic_pro_column = {
    'monetarycap': ['MONETARY_CAP'],
    'acctrcv': ['ACCT_RCV'],
    'prepay': ['PREPAY'],
    'othrcv': ['OTH_RCV'],
    'inventories': ['INVENTORIES'],
    'totcurassets': ['TOT_CUR_ASSETS'],
    'longtermeqyinvest': ['LONG_TERM_EQY_INVEST'],
    'fixassets': ['FIX_ASSETS'],
    'intangassets': ['INTANG_ASSETS'],
    'deferredtaxassets': ['DEFERRED_TAX_ASSETS'],
    'totnoncurassets': ['TOT_NON_CUR_ASSETS'],
    'totassets': ['TOT_ASSETS'],
    'stborrow': ['ST_BORROW'],
    'acctpayable': ['ACCT_PAYABLE'],
    'emplbenpayable': ['EMPL_BEN_PAYABLE'],
    'taxessurchargespayable': ['TAXES_SURCHARGES_PAYABLE'],
    'totcurliab': ['TOT_CUR_LIAB'],
    'totnoncurliab': ['TOT_NON_CUR_LIAB'],
    'totliab': ['TOT_LIAB'],
    'caprsrv': ['CAP_RSRV'],
    'surplusrsrv': ['SURPLUS_RSRV'],
    'undistributedprofit': ['UNDISTRIBUTED_PROFIT'],
    'totshrhldreqyexclminint': ['TOT_SHRHLDR_EQY_EXCL_MIN_INT'],
    'totshrhldreqyinclminint': ['TOT_SHRHLDR_EQY_INCL_MIN_INT'],
    'totliabshrhldreqy': ['TOT_LIAB_SHRHLDR_EQY'],
    'accountsreceivablebill': ['ACCOUNTS_RECEIVABLE_BILL'],
    'accountspayable': ['ACCOUNTS_PAYABLE'],
    'othrcvtot': ['OTH_RCV_TOT'],
    'stmbstot': ['STM_BS_TOT'],
    'othpayabletot': ['OTH_PAYABLE_TOT'],
    # 组合类
    'ldbl': ['TOT_CUR_ASSETS', 'TOT_CUR_LIAB'], # 流动比率
    'sdbl': ['INVENTORIES', 'TOT_CUR_ASSETS', 'TOT_CUR_LIAB'],
    'fzqybl': ['TOT_LIAB', 'TOT_SHRHLDR_EQY_INCL_MIN_INT'],
    'zcggl': ['TOT_ASSETS', 'TOT_SHRHLDR_EQY_INCL_MIN_INT'],
    'gdqybl': ['TOT_SHRHLDR_EQY_INCL_MIN_INT', 'TOT_ASSETS'],
    'gdzcbl': ['FIX_ASSETS', 'TOT_ASSETS'],
    'wxzcbl': ['INTANG_ASSETS', 'TOT_ASSETS'],
    'zbgjbl': ['CAP_RSRV', 'TOT_SHRHLDR_EQY_INCL_MIN_INT'],
    'lcsybl': ['UNDISTRIBUTED_PROFIT', 'TOT_SHRHLDR_EQY_INCL_MIN_INT'],
}


# 因子属性函数
def f_pro_monetarycap(fin_df):
    fin_df['factor'] = fin_df['MONETARY_CAP']
    return fin_df
def f_pro_acctrcv(fin_df):
    fin_df['factor'] = fin_df['ACCT_RCV']
    return fin_df
def f_pro_othrcv(fin_df):
    fin_df['factor'] = fin_df['OTH_RCV']
    return fin_df
def f_pro_prepay(fin_df):
    fin_df['factor'] = fin_df['PREPAY']
    return fin_df
def f_pro_inventories(fin_df):
    fin_df['factor'] = fin_df['INVENTORIES']
    return fin_df
def f_pro_totcurassets(fin_df):
    fin_df['factor'] = fin_df['TOT_CUR_ASSETS']
    return fin_df
def f_pro_longtermeqyinvest(fin_df):
    fin_df['factor'] = fin_df['LONG_TERM_EQY_INVEST']
    return fin_df
def f_pro_fixassets(fin_df):
    fin_df['factor'] = fin_df['FIX_ASSETS']
    return fin_df
def f_pro_intangassets(fin_df):
    fin_df['factor'] = fin_df['INTANG_ASSETS']
    return fin_df
def f_pro_deferredtaxassets(fin_df):
    fin_df['factor'] = fin_df['DEFERRED_TAX_ASSETS']
    return fin_df
def f_pro_totnoncurassets(fin_df):
    fin_df['factor'] = fin_df['TOT_NON_CUR_ASSETS']
    return fin_df
def f_pro_totassets(fin_df):
    fin_df['factor'] = fin_df['TOT_ASSETS']
    return fin_df
def f_pro_stborrow(fin_df):
    fin_df['factor'] = fin_df['ST_BORROW']
    return fin_df
def f_pro_acctpayable(fin_df):
    fin_df['factor'] = fin_df['ACCT_PAYABLE']
    return fin_df
def f_pro_emplbenpayable(fin_df):
    fin_df['factor'] = fin_df['EMPL_BEN_PAYABLE']
    return fin_df
def f_pro_taxessurchargespayable(fin_df):
    fin_df['factor'] = fin_df['TAXES_SURCHARGES_PAYABLE']
    return fin_df
def f_pro_totcurliab(fin_df):
    fin_df['factor'] = fin_df['TOT_CUR_LIAB']
    return fin_df
def f_pro_totnoncurliab(fin_df):
    fin_df['factor'] = fin_df['TOT_NON_CUR_LIAB']
    return fin_df
def f_pro_totliab(fin_df):
    fin_df['factor'] = fin_df['TOT_LIAB']
    return fin_df
def f_pro_caprsrv(fin_df):
    fin_df['factor'] = fin_df['CAP_RSRV']
    return fin_df
def f_pro_surplusrsrv(fin_df):
    fin_df['factor'] = fin_df['SURPLUS_RSRV']
    return fin_df
def f_pro_undistributedprofit(fin_df):
    fin_df['factor'] = fin_df['UNDISTRIBUTED_PROFIT']
    return fin_df
def f_pro_totshrhldreqyexclminint(fin_df):
    fin_df['factor'] = fin_df['TOT_SHRHLDR_EQY_EXCL_MIN_INT']
    return fin_df
def f_pro_totshrhldreqyinclminint(fin_df):
    fin_df['factor'] = fin_df['TOT_SHRHLDR_EQY_INCL_MIN_INT']
    return fin_df
def f_pro_totliabshrhldreqy(fin_df):
    fin_df['factor'] = fin_df['TOT_LIAB_SHRHLDR_EQY']
    return fin_df
def f_pro_accountsreceivablebill(fin_df):
    fin_df['factor'] = fin_df['ACCOUNTS_RECEIVABLE_BILL']
    return fin_df
def f_pro_accountspayable(fin_df):
    fin_df['factor'] = fin_df['ACCOUNTS_PAYABLE']
    return fin_df
def f_pro_othrcvtot(fin_df):
    fin_df['factor'] = fin_df['OTH_RCV_TOT']
    return fin_df
def f_pro_stmbstot(fin_df):
    fin_df['factor'] = fin_df['STM_BS_TOT']
    return fin_df
def f_pro_othpayabletot(fin_df):
    fin_df['factor'] = fin_df['OTH_PAYABLE_TOT']
    return fin_df
## 组合类指标
def f_pro_ldbl(fin_df): # 流动比率 = 流动资产 / 流动负债
    fin_df['factor'] = fin_df['TOT_CUR_ASSETS'].fillna(0) / fin_df['TOT_CUR_LIAB'].replace(0,np.nan)
    return fin_df
def f_pro_sdbl(fin_df): # 速动比率 = (流动资产 - 存货) / 流动负债
    fin_df['factor'] = (fin_df['TOT_CUR_ASSETS'].fillna(0) - fin_df['INVENTORIES'].fillna(0)) / fin_df['TOT_CUR_LIAB'].replace(0,np.nan)
    return fin_df
def f_pro_fzqybl(fin_df): # 负债权益比率 = 总负债 / 股东权益（包含少数股东）
    fin_df['factor'] = fin_df['TOT_LIAB'].fillna(0) / fin_df['TOT_SHRHLDR_EQY_INCL_MIN_INT'].replace(0,np.nan)
    return fin_df
def f_pro_zcggl(fin_df): # 资产杠杆率 = 资产总额 / 股东权益
    fin_df['factor'] = fin_df['TOT_ASSETS'].fillna(0) / fin_df['TOT_SHRHLDR_EQY_INCL_MIN_INT'].replace(0,np.nan)
    return fin_df
def f_pro_gdqybl(fin_df): # 股东权益比率 = 股东权益 / 资产总额
    fin_df['factor'] = fin_df['TOT_SHRHLDR_EQY_INCL_MIN_INT'].fillna(0) / fin_df['TOT_ASSETS'].replace(0,np.nan)
    return fin_df
def f_pro_gdzcbl(fin_df): # 固定资产比例 = 固定资产 / 资产总额
    fin_df['factor'] = fin_df['FIX_ASSETS'].fillna(0) / fin_df['TOT_ASSETS'].replace(0,np.nan)
    return fin_df
def f_pro_wxzcbl(fin_df): # 无形资产比例 = 无形资产 / 资产总额
    fin_df['factor'] = fin_df['INTANG_ASSETS'].fillna(0) / fin_df['TOT_ASSETS'].replace(0,np.nan)
    return fin_df
def f_pro_zbgjbl(fin_df): # 资本公积比例 = 资本公积 / 股东权益
    fin_df['factor'] = fin_df['CAP_RSRV'].fillna(0) / fin_df['TOT_SHRHLDR_EQY_INCL_MIN_INT'].replace(0,np.nan)
    return fin_df
def f_pro_lcsybl(fin_df): # 留存收益比例 = 留存收益（WIND写为未分配利润） / 股东权益
    fin_df['factor'] = fin_df['UNDISTRIBUTED_PROFIT'].fillna(0) / fin_df['TOT_SHRHLDR_EQY_INCL_MIN_INT'].replace(0,np.nan)
    return fin_df
# 季度筛选函数，返回df
def f_t_kind_cum(fin_df):
    return fin_df
def f_t_kind_single(fin_df, need_column):
    basic_columns = ['ANN_DT','STATEMENT_TYPE','report_period','MDDate']
    columns = need_column
    columns = [x for x in columns if x not in basic_columns]
    for col in columns:
        fin_df[f'{col}_diff'] = fin_df.groupby(['dt', 'Ticker'])[col].diff()
        fin_df.loc[fin_df['report_period'] == 1, f'{col}_diff'] = fin_df.loc[
            fin_df['report_period'] == 1, col]
    columns_diff = [f'{x}_diff' for x in columns]
    res = fin_df[columns_diff + basic_columns]
    res.columns = [x.replace('_diff','') for x in res.columns]
    return res
def f_t_kind_single1(fin_df, need_column): # 不需要额外处理period=1
    basic_columns = ['ANN_DT','STATEMENT_TYPE','report_period','MDDate']
    columns = need_column
    columns = [x for x in columns if x not in basic_columns]
    for col in columns:
        fin_df[f'{col}_diff'] = fin_df.groupby(['dt', 'Ticker'])[col].diff()
        # fin_df.loc[fin_df['report_period'] == 1, f'{col}_diff'] = fin_df.loc[
        #     fin_df['report_period'] == 1, col]
    columns_diff = [f'{x}_diff' for x in columns]
    res = fin_df[columns_diff + basic_columns]
    res.columns = [x.replace('_diff','') for x in res.columns]
    return res
def f_t_kind_ratiocum(fin_df, need_column):
    basic_columns = ['ANN_DT','STATEMENT_TYPE','report_period','MDDate']
    columns = need_column
    columns = [x for x in columns if x not in basic_columns]
    for col in columns:
        fin_df[f'{col}_diff'] = fin_df.groupby(['dt', 'Ticker'])[col].shift(4)
        fin_df[f'{col}_diff'] = (fin_df[f'{col}'] - fin_df[f'{col}_diff']) / fin_df[f'{col}_diff'].replace(0,np.nan)
    columns_diff = [f'{x}_diff' for x in columns]
    res = fin_df[columns_diff + basic_columns]
    res.columns = [x.replace('_diff','') for x in res.columns]
    return res
def f_t_kind_ratiosingle(fin_df, need_column):
    basic_columns = ['ANN_DT','STATEMENT_TYPE','report_period','MDDate']
    columns = need_column
    columns = [x for x in columns if x not in basic_columns]
    for col in columns:
        fin_df[f'{col}_diff'] = fin_df.groupby(['dt', 'Ticker'])[col].diff()
        fin_df.loc[fin_df['report_period'] == 1, f'{col}_diff'] = fin_df.loc[
            fin_df['report_period'] == 1, col]
    columns_diff = [f'{x}_diff' for x in columns]
    res = fin_df[columns_diff + basic_columns]
    res.columns = [x.replace('_diff','') for x in res.columns]
    fin_df = res.copy()
    for col in columns:
        fin_df[f'{col}_diff'] = fin_df.groupby(['dt', 'Ticker'])[col].shift(4)
        fin_df[f'{col}_diff'] = (fin_df[f'{col}'] - fin_df[f'{col}_diff']) / fin_df[f'{col}_diff'].replace(0,np.nan)
    columns_diff = [f'{x}_diff' for x in columns]
    res = fin_df[columns_diff + basic_columns]
    res.columns = [x.replace('_diff','') for x in res.columns]
    return res
# 标准化处理,计算序列值
def f_calc_max(fin_series):
    if fin_series.empty:
        return np.nan
    else:
        return fin_series.max()
def f_calc_min(fin_series):
    if fin_series.empty:
        return np.nan
    else:
        return fin_series.min()
def f_calc_avg(fin_series):
    if fin_series.empty:
        return np.nan
    else:
        return fin_series.mean()
def f_calc_med(fin_series):
    if fin_series.empty:
        return np.nan
    else:
        return fin_series.median()
def f_calc_cv(fin_series):
    if fin_series.empty:
        return np.nan
    else:
        if  abs(fin_series.mean()) > 0.0001:
            return fin_series.std() / fin_series.mean()
        else:
            return np.nan
def f_calc_sum(fin_series):
    if fin_series.empty:
        return np.nan
    else:
        return fin_series.sum()
def f_calc_cct(fin_series):
    if abs(fin_series.sum()) > 0.001:
        return (fin_series**2).sum() / (fin_series.sum())**2
    else:
        return np.nan
def f_calc_skew(fin_series):
    if fin_series.empty:
        return np.nan
    else:
        return fin_series.skew()
def f_calc_kurt(fin_series):
    if fin_series.empty:
        return np.nan
    else:
        return fin_series.kurt()
def f_calc_change(fin_series):
    if fin_series.empty:
        return np.nan
    else:
        return fin_series.head(1).mean() - fin_series.tail(1).mean()
def f_calc_tail(fin_series):
    if fin_series.empty:
        return np.nan
    else:
        return fin_series.tail(1).mean()
def f_calc_m2m(fin_series):
    if fin_series.empty:
        return np.nan
    else:
        fin_series = fin_series + fin_series.min()
        return fin_series.max() / fin_series.mean() if fin_series.mean()>0 else np.nan
def f_calc_std(fin_series):
    if fin_series.empty:
        return np.nan
    else:
        return fin_series.std()