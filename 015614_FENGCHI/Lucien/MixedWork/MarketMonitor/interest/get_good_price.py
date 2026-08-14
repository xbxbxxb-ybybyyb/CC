# coding: utf-8
# Author：fengchi863
# Date ：2025/4/8 17:58

from xquant.factordata import FactorData
from dataApi.tradeDate import get_date_range, get_pre_trade_date
from MixedWork.GreyStockGenerator.tools import trans_any2code
from LucienUtil.StockUtil import StockUtil
import pandas as pd
from LucienUtil import IO
import decimal
import datetime as dt

fd = FactorData()

class GoodStock:
    def __init__(self, now_date):
        self.now_date = now_date
        self.now_year = now_date[:4]

    def get_financial_indicator(self, stock_code, N=11):
        """中国A股财务指标"""
        report_list = [int(self.now_year) - x for x in range(N)][::-1]
        start_year = report_list[0]
        end_year = report_list[-1]
        res_df = fd.get_factor_value('WIND_AShareFinancialIndicator',
                                     S_INFO_WINDCODE=[stock_code],
                                     REPORT_PERIOD=['>=' + f'{start_year}1231', '<=' + f'{end_year}1231'],
                                     factors=['S_FA_EBITPS', 'S_FA_UNDISTRIBUTEDPS', 'REPORT_PERIOD', 'S_FA_ROE_YEARLY']
                                     )
        # 保留年报，也就是报告期为1231结尾
        res_df = res_df.loc[res_df['REPORT_PERIOD'].apply(lambda x: str(x).endswith('1231'))]
        rename_dict = {
            'REPORT_PERIOD': '报告期',
            'S_FA_EBITPS': '每股息税前利润',
            'S_FA_UNDISTRIBUTEDPS': '每股未分配利润',
            'S_FA_ROE_YEARLY': '年化净资产收益率'
        }

        res_df = res_df.rename(rename_dict, axis=1)
        res_df = res_df.sort_values('报告期').reset_index(drop=True)
        return res_df


    def get_history_profit(self, stock_code, N=11):
        """中国A股利润表"""
        report_list = [int(self.now_year) - x for x in range(N)][::-1]
        start_year = report_list[0]
        end_year = report_list[-1]
        res_df = fd.get_factor_value('WIND_AShareIncome',
                            S_INFO_WINDCODE=[stock_code],
                            REPORT_PERIOD=['>=' + f'{start_year}1231', '<=' + f'{end_year}1231'],
                            factors=['STATEMENT_TYPE', 'NET_PROFIT_EXCL_MIN_INT_INC', 'NET_PROFIT_AFTER_DED_NR_LP', 'TOT_OPER_REV', 'REPORT_PERIOD', 'NET_PROFIT_INCL_MIN_INT_INC']
                            )
        # 40800100 合并报表
        res_df = res_df.query('STATEMENT_TYPE == "408001000"')
        # 保留年报，也就是报告期为1231结尾
        res_df = res_df.loc[res_df['REPORT_PERIOD'].apply(lambda x: str(x).endswith('1231'))]
        res_df = res_df.sort_values('REPORT_PERIOD')
        rename_dict = {
            'NET_PROFIT_AFTER_DED_NR_LP': '扣非净利润',
            'NET_PROFIT_EXCL_MIN_INT_INC': '净利润',   # 税后利润中不包含少数股东损益的部分
            'TOT_OPER_REV': '营业收入',
            'REPORT_PERIOD': '报告期'
        }
        res_df = res_df.rename(rename_dict, axis=1)
        res_df = res_df[['报告期', '营业收入', '扣非净利润', '净利润']]
        res_df['营业收入'] = res_df['营业收入'] / 1e8
        res_df['扣非净利润'] = res_df['扣非净利润'] / 1e8
        res_df['净利润'] = res_df['净利润'] / 1e8
        return res_df

    def get_history_share(self, stock_code, N=11):
        """中国A股分红"""
        """
        1、有些年份的分红，是在下一年的5-8月发布上一年的，这里就需要知道最新一年的是否已经公布了分红
        """
        report_list = [int(self.now_year) - x for x in range(N)][::-1]
        start_year = report_list[0]
        end_year = report_list[-1]
        res_df = fd.get_factor_value('WIND_AShareDividend',
                                     S_INFO_WINDCODE=[stock_code],
                                     REPORT_PERIOD=['>=' + f'{start_year}1231', '<=' + f'{end_year}1231'],
                                     factors=['S_DIV_PROGRESS', 'TOT_CASH_DVD', 'REPORT_PERIOD', 'CASH_DVD_PER_SH_AFTER_TAX', 'ANN_DT']
                                     )
        res_df = res_df.sort_values('REPORT_PERIOD')
        # res_df.to_excel('/data/user/015614/junkData/11.xlsx')
        # 筛选"实施"的分红
        res_df = res_df.query('S_DIV_PROGRESS >= "2"')
        res_df['年度'] = res_df['REPORT_PERIOD'].map(lambda x: x[:4])
        # 由于是根据TOT_CASH_DVD算的分红率，所以这里使用这个指标
        res_df['当年是否已经全部分红'] = res_df[['TOT_CASH_DVD', 'REPORT_PERIOD']].apply(lambda x: x['REPORT_PERIOD'].endswith('1231') and x['TOT_CASH_DVD'] > 0, axis=1).map(int)
        res_df = res_df.groupby('年度').agg({'TOT_CASH_DVD': 'sum',
                                           'CASH_DVD_PER_SH_AFTER_TAX': 'sum',
                                           '当年是否已经全部分红': 'max'})
        rename_dict = {
            'TOT_CASH_DVD': '分红总额',
            'CASH_DVD_PER_SH_AFTER_TAX': '每股股利',
        }
        res_df = res_df.rename(rename_dict, axis=1)
        res_df = res_df[['分红总额', '每股股利', '当年是否已经全部分红']]
        res_df['分红总额'] = res_df['分红总额'] / 1e8
        res_df = res_df.sort_index()
        return res_df

    def get_basic_info(self, stock_code, N=11):
        """提供每年最后一个工作日的股本、市值等信息"""
        report_list = [int(self.now_year) - x for x in range(N)][::-1]
        start_year = report_list[0]
        end_year = report_list[-1]
        date_list = get_date_range(start_year*10000 + 101, end_year * 10000 + 1231)
        date_list_str = list(map(lambda x: str(x), date_list))
        high_df = fd.get_factor_value('Basic_factor', factor_names=['high'], stock=[stock_code], mddate=date_list_str).reset_index()
        low_df = fd.get_factor_value('Basic_factor', factor_names=['low'], stock=[stock_code], mddate=date_list_str).reset_index()
        high_df['年度'] = high_df['mddate'].map(lambda x: x[:4])
        low_df['年度'] = low_df['mddate'].map(lambda x: x[:4])
        yearly_high = high_df.groupby('年度').max()
        yearly_low = low_df.groupby('年度').min()
        yearly_high_low = pd.merge(yearly_high['high'], yearly_low['low'], on='年度')

        year_end_list = get_date_range(start_year*10000 + 101, end_year * 10000 + 1231, period='Y')
        year_end_list[-1] = get_pre_trade_date(int(dt.date.today().strftime('%Y%m%d')), 2)
        year_end_list_str = list(map(lambda x: str(x), year_end_list))

        df = fd.get_factor_value('Basic_factor', factor_names=['a_mkt_cap', 'pe_ttm', 'total_shares'], stock=[stock_code], mddate=year_end_list_str)
        df = df.rename({'a_mkt_cap': '总市值',
                        'pe_ttm': '市盈率TTM',
                        'total_shares': '总股本'}, axis=1)
        df['年度'] = df.index.get_level_values(0).map(lambda x: x[:4])
        df = df.set_index('年度', drop=True)

        return yearly_high_low, df

    @staticmethod
    def guess_future_profit(profit_df, profit_grow_rate, N=20):
        latest_profit = profit_df['扣非净利润'].iloc[-1]
        latest_year = profit_df['年度'].iloc[-1]
        future_profit_list = [latest_profit * ((1 + profit_grow_rate) ** i) for i in range(N)]
        future_year_list = [int(latest_year) + 1 + x for x in range(N)]
        res = pd.Series(future_profit_list, index=future_year_list)
        return res

    @staticmethod
    def round_(x, n=0):
        x = x + 1e-10
        if n > 0:
            res = float(decimal.Decimal(str(x)).quantize(decimal.Decimal('0.%s1' % ('0' * (n - 1))),
                                                         rounding=decimal.ROUND_HALF_UP))
        else:
            res = int(decimal.Decimal(str(x)).quantize(decimal.Decimal('1'), rounding=decimal.ROUND_HALF_UP))
        return res

def get_good_price(stock_code, now_date):
    stock_code = trans_any2code(stock_code)
    """
    计算净利润增长率使用扣非净利润
    计算分红率，使用分红总额/净利润
    """
    gs = GoodStock(now_date=now_date)

    profit_df = gs.get_history_profit(stock_code, 11)
    finance_df = gs.get_financial_indicator(stock_code, 11)
    profit_grow_rate = profit_df['扣非净利润'].pct_change().mean()
    profit_grow_rate = gs.round_(profit_grow_rate, 2)

    share_df = gs.get_history_share(stock_code, 11)

    # 按年度计算，注意：最后一个年度可能分红还没有结束，所以使用倒数第二个年度的分红比例进行参考
    profit_df['年度'] = profit_df['报告期'].map(lambda x: x[:4])
    finance_df['年度'] = finance_df['报告期'].map(lambda x: x[:4])

    # 剔除报告期，尾号都是1231结尾的，不需要使用
    profit_df = profit_df.drop('报告期', axis=1)
    finance_df = finance_df.drop('报告期', axis=1)

    merge_df = pd.merge(profit_df, share_df, on='年度', how='outer')
    merge_df = pd.merge(merge_df, finance_df, on='年度', how='outer')
    merge_df = merge_df.set_index('年度')
    merge_df = merge_df.sort_index()

    # merge_df['分红率'] = merge_df['每股股利'] / merge_df['每股息税前利润']  #这个计算会比 分红总额/净利润 低一点
    merge_df['分红率'] = merge_df['分红总额'] / merge_df['净利润']
    merge_df['净利润同比'] = merge_df['净利润'].pct_change()
    merge_df['净利润同比2'] = merge_df['扣非净利润'].pct_change()

    yearly_high_low, df = gs.get_basic_info(stock_code, N=11)
    merge_df = pd.merge(merge_df, yearly_high_low, on='年度', how='outer')
    merge_df = pd.merge(merge_df, df, on='年度', how='outer')

    # 这里应对万得落地库对于每股股利的计算不及时的情况，总股本单位是万，分红总额单位也是亿
    merge_df.loc['2024', '每股股利'] = merge_df.loc['2024', '分红总额'] / merge_df.loc['2024', '总股本'] * 1e4

    if merge_df.loc['2024', '当年是否已经全部分红']:
        merge_df.loc['2025', '每股股利'] = merge_df.loc['2024', '每股股利']
    else:
        merge_df.loc['2025', '每股股利'] = merge_df.loc['2023', '每股股利']
    merge_df['最低股息率'] = merge_df['每股股利'] / merge_df['high']
    merge_df['最高股息率'] = merge_df['每股股利'] / merge_df['low']

    stock_name = StockUtil.get_1stock_name(stock_code)
    merge_df['证券代码'] = stock_code
    merge_df['证券名称'] = stock_name

    merge_df.to_excel(f'/data/user/015614/junkData/分红养老/{stock_name}_{stock_code}.xlsx')

    # future_profit = gs.guess_future_profit(
    #     profit_df=profit_df,
    #     profit_grow_rate=profit_grow_rate,
    #     N=20
    # )

if __name__ == '__main__':
    now_date = dt.datetime.today().strftime('%Y%m%d')
    f_data = IO.read_data(['20250601', now_date], columns=['close', 'adjfactor'],
                          alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
    stock_code_list = list(f_data['close'].unstack().columns)

    stock_code_list = list(filter(lambda x: not (x.startswith('688') or x.endswith('BJ')), stock_code_list))
    get_good_price('601088.SH', now_date)
    # for stock_code in stock_code_list[::-1]:
    #     try:
    #         get_good_price(stock_code, now_date)
    #         print(f'success: {stock_code}')
    #     except:
    #         pd.DataFrame().to_excel(f'/data/user/015614/junkData/分红养老/error/{stock_code}.xlsx')
    #         print(f'error: {stock_code}')