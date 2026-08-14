# 使用实际的量计算实际买入的股票的模拟第一版收益
"""
Saturn 930 别称 项目二
"""
import numpy as np
import pandas as pd
from xquant.factordata import FactorData
from xquant.marketdata import MarketData
mdp = MarketData()
s = FactorData()

# ------------------------------------更新触发文件，计算模拟收益-------------------------------------------------
import time
import os
import datetime as dt
import sys
sys.path.append("../../")
sys.path.append("/../..")

if __name__ == "__main__":
    t1 = time.time()
    if len(sys.argv) > 1:
        date = sys.argv[1]
    else:
        date = s.tradingday(dt.datetime.now().strftime('%Y%m%d'), -1)[0]  # 判断当前的日期
        # date = '20240226' # 若未在当个交易日晚上运行程序，需要在次日早上修改date
    print('pj2更新实盘触发标签文件，current date = %s' % date)

    Adate = date[0:4] + '-' + date[4:6] + '-' + date[6:8]
    lastdate = s.tradingday(date, -2)[0]
    Alastdate = lastdate[0:4] + '-' + lastdate[4:6] + '-' + lastdate[6:8]
    IO_mother_dir = '/data/group/800080/warehouse_event'
    MD_data_prod_dir = IO_mother_dir + '/prod/LOCAL_DATA/FLAG/%s/' % date

    # while not os.path.exists(MD_data_prod_dir + '%s_MD.success' % date):
    #     print('等待MD或RDF或RISK或5分钟数据中')
    #     time.sleep(60)
    while True:
        md_data = s.get_factor_value('WIND_AShareEODPrices',
                                     factors=['S_INFO_WINDCODE', 'S_DQ_PCTCHANGE', 'S_DQ_PRECLOSE', 'S_DQ_OPEN', 'S_DQ_HIGH', 'S_DQ_LOW', 'S_DQ_CLOSE', 'S_DQ_AVGPRICE', 'S_DQ_ADJFACTOR'],
                                     TRADE_DT=date).rename(columns={'S_INFO_WINDCODE': 'Ticker', 'S_DQ_PCTCHANGE': 'pct_chg', 'S_DQ_PRECLOSE': 'pre_close', 'S_DQ_OPEN': 'open',
                                                                    'S_DQ_HIGH': 'high', 'S_DQ_LOW': 'low', 'S_DQ_CLOSE': 'close', 'S_DQ_AVGPRICE': 'vwap', 'S_DQ_ADJFACTOR': 'adjfactor'})
        if len(md_data) > 0:  # 当日有数据
            md_data['dt'] = pd.to_datetime(date)
            md_data = md_data.set_index(['dt', 'Ticker']).sort_index()
            break
        else:
            print(f'{date}_WIND数据未完备')
            time.sleep(60)

    # ----------------------------更新项目二触发文件，添加形态和v2o10信息-------------------------------
    need_columns_tot = ['dt', 'Ticker', '前日形态', 'TN_v2o10', 'p2shouldBuySignal', '买入时点', 'T_c2o10', 'close_zt', 'high_zt', 'T_o2pre']
    need_columns = ['dt', 'Ticker', '前日形态', 'TN_v2o10', 'p2shouldBuySignal', '买入时点']

    # 获取昨天的标签汇总、今天的因子耗时和模型差异
    if lastdate <= '20210326':
        Labels_prod_summary_old = pd.DataFrame()
    else:
        Labels_prod_summary_old = pd.read_excel('/data/group/800463/日内强势股/log_parse/因子耗时/实盘触发项目二标签汇总_%s.xlsx' % Alastdate)

    if 'twap2o10' not in Labels_prod_summary_old.columns:
        Labels_prod_summary_old['twap2o10'] = np.nan

    raw_last_date_factor_time_cost_pj2 = pd.read_excel('/data/group/800463/日内强势股/log_parse/因子耗时/因子耗时_%s_prod.xlsx' % Alastdate, sheet_name='项目二930样本')

    raw_last_date_model_compare_pj2_931 = pd.read_excel(
        '/data/group/800463/日内强势股/log_parse/模型差异/%s/模型差异_%s_prod_pj2_931.xlsx' % (lastdate, lastdate)
        , sheet_name='本地投票结果').rename(columns={'Ticker': 'Unnamed: 0'}).set_index(['Unnamed: 0'])
    raw_last_date_model_compare_pj2 = pd.DataFrame(index=raw_last_date_model_compare_pj2_931.index,
                                                   columns=['本地投票结果',
                                                            'prod_signal',
                                                            'is_sample_930'])
    raw_last_date_model_compare_pj2 = raw_last_date_model_compare_pj2.reset_index()
    raw_last_date_model_compare_pj2['本地投票结果'] = 0
    raw_last_date_model_compare_pj2['prod_signal'] = False
    raw_last_date_model_compare_pj2['is_sample_930'] = False
    # raw_last_date_model_compare_pj2['p2shouldBuySignal'] = False
    # 当前项目二买入时点为930
    raw_last_date_model_compare_pj2['买入时点'] = 930
    # 获取模型的预测结果
    # 如果昨天有模型没有给出预测（比如没有前日涨停样本、或者没有前高样本等分场景），则在模型差异中的投票结果中新建一个空的列
    raw_last_date_model_compare_pj2 = raw_last_date_model_compare_pj2[['Unnamed: 0'] + ['买入时点']].rename(columns={'Unnamed: 0': 'Ticker'}) * 1
    raw_last_date_model_compare_pj2['dt'] = pd.Timestamp(Alastdate)
    # 计算买入时形态
    for index, row in raw_last_date_factor_time_cost_pj2.iterrows():
        stock_code, pre_date = row['Unnamed: 0'], lastdate
        saturn_basic_info = pd.read_hdf('/data/group/800463/project/project2_prod/daily_data/Basic/Basic_closed_hf_finish.h5')
        raw_last_date_factor_time_cost_pj2.loc[index, '前日形态'] = saturn_basic_info.loc[lastdate, stock_code]['lzt_label_pattern']

    # 将耗时、模型预测拼入标签汇总
    raw_last_date_factor_time_cost_pj2['dt'] = pd.Timestamp(lastdate)
    raw_last_date_factor_time_cost_pj2['TN_v2o10'] = np.nan
    raw_last_date_factor_time_cost_pj2['p2shouldBuySignal'] = False
    raw_last_date_factor_time_cost_pj2 = raw_last_date_factor_time_cost_pj2.rename(columns={'Unnamed: 0': 'Ticker'})
    Labels_prod_summary_new = pd.concat([Labels_prod_summary_old,
                                         raw_last_date_factor_time_cost_pj2.set_index(['dt', 'Ticker']).join(
                                             raw_last_date_model_compare_pj2.set_index(['dt', 'Ticker'])).reset_index()[
                                             need_columns]]).reset_index()[need_columns_tot + ['twap2o10']]

    # 对于v2o10还未算出的样本进行计算
    v2o10_nan_samples = Labels_prod_summary_new[
        (Labels_prod_summary_new['TN_v2o10'].isnull()) | (Labels_prod_summary_new['T_c2o10'].isnull())]
    date_ini = v2o10_nan_samples['dt'].apply(lambda x: x.strftime('%Y%m%d')).min()
    end_date = v2o10_nan_samples['dt'].apply(lambda x: x.strftime('%Y%m%d')).max()
    # 20240227 by fengc 优化时间
    md_data = s.get_factor_value('WIND_AShareEODPrices',
                                 factors=['S_INFO_WINDCODE', 'TRADE_DT', 'S_DQ_PCTCHANGE', 'S_DQ_PRECLOSE', 'S_DQ_OPEN', 'S_DQ_HIGH', 'S_DQ_LOW', 'S_DQ_CLOSE', 'S_DQ_AVGPRICE', 'S_DQ_ADJFACTOR'],
                                 TRADE_DT=s.tradingday(date_ini, date)).rename(
        columns={'S_INFO_WINDCODE': 'Ticker', 'TRADE_DT': 'dt', 'S_DQ_PCTCHANGE': 'pct_chg', 'S_DQ_PRECLOSE': 'pre_close', 'S_DQ_OPEN': 'open',
                 'S_DQ_HIGH': 'high', 'S_DQ_LOW': 'low', 'S_DQ_CLOSE': 'close', 'S_DQ_AVGPRICE': 'vwap', 'S_DQ_ADJFACTOR': 'adjfactor'})
    md_data['dt'] = md_data['dt'].apply(lambda x: pd.to_datetime(x))
    md_data = md_data.set_index(['dt', 'Ticker']).sort_values(['dt', 'Ticker'])
    # end_date_ = int(s.tradingday(end_date, 30)[-1])
    # md_data = IO.read_data([date_ini, end_date_],
    #                        columns=['pre_close', 'open', 'high', 'low', 'close', 'vwap', 'adjfactor'],
    #                        alt=IO_mother_dir + '/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
    md_data['vwap'] = md_data['vwap'] * md_data['adjfactor']
    md_data['ul_price'] = np.floor(md_data['pre_close'] * 100 * 1.1 + 0.5) / 100
    md_data['new_300'] = ((md_data.reset_index()['Ticker'].apply(lambda x: x[0] == '3') & (md_data.reset_index()['dt'] >= '20200824')) | \
                          (md_data.reset_index()['Ticker'].apply(lambda x: x[:2] == '68') & (md_data.reset_index()['dt'] >= '20100824'))).values
    md_data.loc[md_data['new_300'], 'ul_price'] = np.floor(md_data.loc[md_data['new_300'], 'pre_close'] * 100 * 1.2 + 0.5) / 100
    md_data['vwap'], md_data['pre_close'] = md_data['vwap'] * md_data['adjfactor'], md_data['pre_close'] * md_data['adjfactor']
    md_data['high'], md_data['low'] = md_data['high'] * md_data['adjfactor'], md_data['low'] * md_data['adjfactor']
    md_data['ul_price'] = md_data['ul_price'] * md_data['adjfactor']
    md_data.loc[md_data['high'] == md_data['low'], 'vwap'] = np.nan
    md_data['next_vwap'] = md_data['vwap'].unstack().shift(-1).stack()
    md_data['next_vwap'] = md_data['next_vwap'].unstack().fillna(method='bfill', axis=0).stack()

    Labels_prod_summary_new_copy = Labels_prod_summary_new.copy()
    for i in v2o10_nan_samples.index:
        buy_date = Labels_prod_summary_new.loc[i]['dt'].strftime('%Y%m%d')
        stock = Labels_prod_summary_new.loc[i]['Ticker']
        saturn_basic_hf_info = pd.read_hdf('/data/group/800463/project/project2_prod/daily_data/Basic/Basic_closed_hf_finish.h5')
        T_day_930_10_twap_before_ZT = saturn_basic_hf_info['T_day_930_10_twap_before_ZT'].loc[buy_date, stock]
        this_buy_price = md_data['adjfactor'].loc[buy_date, stock] * T_day_930_10_twap_before_ZT
        this_v2o10 = (md_data['next_vwap'].loc[buy_date, stock] / this_buy_price - 1) * 100
        T_c2o10 = (md_data['vwap'].loc[buy_date, stock] / this_buy_price - 1) * 100
        if T_day_930_10_twap_before_ZT == -1:
            this_v2o10, T_c2o10 = -1, -1
        if T_day_930_10_twap_before_ZT == -3:
            this_v2o10, T_c2o10 = -3, -3
        Labels_prod_summary_new.loc[i, 'TN_v2o10'] = this_v2o10
        Labels_prod_summary_new.loc[i, 'T_c2o10'] = T_c2o10

    param = {'buy_vol_pct':0.2, 'sell_vol_pct': 0.1, 'max_amt': 500 * 10000, 'cover_amt':1500, 'p2_type':'930'}
    # -----计算卖出收益-----
    if 'twap2o10' not in Labels_prod_summary_new.columns:
        Labels_prod_summary_new['twap2o10'] = np.nan
    if 'close_zt' not in Labels_prod_summary_new.columns:
        Labels_prod_summary_new['close_zt'] = np.nan
    if 'high_zt' not in Labels_prod_summary_new.columns:
        Labels_prod_summary_new['high_zt'] = np.nan
    if 'T_o2pre' not in Labels_prod_summary_new.columns:
        Labels_prod_summary_new['T_o2pre'] = np.nan

    close_high_zt_nan_samples = Labels_prod_summary_new[Labels_prod_summary_new['close_zt'].isnull()|Labels_prod_summary_new['high_zt'].isnull()]
    if len(close_high_zt_nan_samples) != 0:
        date_ini = close_high_zt_nan_samples['dt'].apply(lambda x: x.strftime('%Y%m%d')).min()
        end_date = close_high_zt_nan_samples['dt'].apply(lambda x: x.strftime('%Y%m%d')).max()
        # 20240227 by fengc 优化时间
        MD_data = s.get_factor_value('WIND_AShareEODPrices',
                                     factors=['S_INFO_WINDCODE', 'TRADE_DT', 'S_DQ_PCTCHANGE', 'S_DQ_PRECLOSE', 'S_DQ_OPEN', 'S_DQ_HIGH', 'S_DQ_LOW', 'S_DQ_CLOSE', 'S_DQ_AVGPRICE', 'S_DQ_ADJFACTOR'],
                                     TRADE_DT=s.tradingday(date_ini, date)).rename(
            columns={'S_INFO_WINDCODE': 'Ticker', 'TRADE_DT': 'dt', 'S_DQ_PCTCHANGE': 'pct_chg', 'S_DQ_PRECLOSE': 'pre_close', 'S_DQ_OPEN': 'open',
                     'S_DQ_HIGH': 'high', 'S_DQ_LOW': 'low', 'S_DQ_CLOSE': 'close', 'S_DQ_AVGPRICE': 'vwap', 'S_DQ_ADJFACTOR': 'adjfactor'})
        MD_data['dt'] = MD_data['dt'].apply(lambda x: pd.to_datetime(x))
        MD_data = MD_data.set_index(['dt', 'Ticker']).sort_values(['dt', 'Ticker'])
        # MD_data = IO.read_data([date_ini, end_date], columns=['pre_close', 'high','close','open'],
        #                             alt=IO_mother_dir+'/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
        MD_data['ul_price'] = np.floor(MD_data['pre_close'] * 100 * 1.1 + 0.5) / 100
        MD_data['new_300'] = ((MD_data.reset_index()['Ticker'].apply(lambda x: x[0] == '3') & (MD_data.reset_index()['dt'] >= '20200824')) | \
                          (MD_data.reset_index()['Ticker'].apply(lambda x: x[:2] == '68') & (MD_data.reset_index()['dt'] >= '20100824'))).values
        MD_data.loc[MD_data['new_300'],'ul_price'] = np.floor(MD_data.loc[MD_data['new_300'], 'pre_close'] * 100 * 1.2 + 0.5) / 100
        for i in close_high_zt_nan_samples.index:
            buy_date = Labels_prod_summary_new.loc[i]['dt'].strftime('%Y%m%d')
            stock = Labels_prod_summary_new.loc[i]['Ticker']
            Labels_prod_summary_new.loc[i, 'high_zt'] = (MD_data['ul_price'] == MD_data['high']).loc[buy_date,stock]
            Labels_prod_summary_new.loc[i, 'close_zt'] = (MD_data['ul_price'] == MD_data['close']).loc[buy_date,stock]
            Labels_prod_summary_new.loc[i, 'T_o2pre'] = 100*((MD_data['open'] / MD_data['pre_close'])-1).loc[buy_date,stock]

    Labels_prod_summary_new.to_excel('/data/group/800463/日内强势股/log_parse/因子耗时/实盘触发项目二标签汇总_%s.xlsx'%Adate,index=False)
    print('create file %s!!!!!!!!!!!!'%'/data/group/800463/日内强势股/log_parse/因子耗时/实盘触发项目二标签汇总_%s.xlsx'%Adate)
    print(f'2-1.label_summary_pj2耗时{round(time.time() - t1, 6)}秒')