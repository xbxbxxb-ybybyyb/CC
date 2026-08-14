# -*- coding: utf-8 -*-
import pandas as pd
from xquant.factordata import FactorData
s = FactorData()

#T-1_factor(T-1日类因子)示例
def factor_test_last_factor(start_date, end_date, IO, return_fillna_dic=False):
    factor_name='test_last_factor'

    if return_fillna_dic:
        # 返回因子为nan时的填充值，Todo: T-1_factor类因子需要包括数据源缩写（其列表在因子规范数据源检测一节）
        return {factor_name: 0, 'data':['MD']}
    # 计算全部股票在全部时间区间上的因子值，之后会在run_factor_demo函数中进行向后平移一天和样本的筛选
    # 返回dt, Ticker格式multiindex的DataFrame, 一列，列名为因子名称
    # -------------------------------------------------------------------------------------------------------------------
    start_date_ = int(s.tradingday(str(start_date), -30)[0])  #向前取的天数至少大于要用到的数据日期数+1天
    md_data = IO.read_data([start_date_,end_date],columns = ['pct_chg']
                           ,alt = '/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
    md_data.loc[md_data['pct_chg'] > 10, 'pct_chg'] = 10  # 截断
    md_data.loc[md_data['pct_chg'] < -10, 'pct_chg'] = -10  # 截断
    factor_df = pd.DataFrame()
    factor_df[factor_name] = md_data['pct_chg'].unstack().rolling(20,min_periods=3).std().stack()
    # -------------------------------------------------------------------------------------------------------------------
    return factor_df

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的fDataFrame中列名也为因子名称;
    # 以上的四个因子名称应该统一。

if __name__ == '__main__':
    import IO
    start_date, end_date=20180101,20180130
    factor_df=factor_test_last_factor(start_date,end_date,IO)
    print(factor_df.describe())
