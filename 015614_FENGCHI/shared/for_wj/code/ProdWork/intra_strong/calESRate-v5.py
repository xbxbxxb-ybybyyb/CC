# 使用实际的量计算实际买入的股票的模拟第一版收益
import pandas as pd
import numpy as np
from xquant.factordata import FactorData
s = FactorData()
from LucienUtil import IO
from xquant.marketdata import MarketData
import datetime as dt
mdp = MarketData()


# ------------------------------------更新触发文件，计算模拟收益-------------------------------------------------
import os
import pickle
import datetime as dt
import sys
sys.path.append("../../")
sys.path.append("/../..")
from xquant.factordata import FactorData
from xquant.xqutils.xqfile import HDFSFile
s = FactorData()
hf = HDFSFile()
import ProdWork.intra_strong.p2_profit_backtest as p2bt

if __name__ == "__main__":

    if len(sys.argv) > 1:
        date = sys.argv[1]
    else:
        date = s.tradingday(dt.datetime.now().strftime('%Y%m%d'), -1)[0]  # 判断当前的日期
        # date = '20230606'# # 若未在当个交易日晚上运行程序，需要在次日早上修改date
    print('current date = %s' % date)

    # Adate = '2021-06-23'
    # lastdate = '20210622'
    # Alastdate = '2021-06-22'
    Adate = date[0:4] + '-' + date[4:6] + '-' + date[6:8]
    lastdate = s.tradingday(date, -2)[0]
    Alastdate = lastdate[0:4] + '-' + lastdate[4:6] + '-' + lastdate[6:8]
    IO_mother_dir = '/data/group/800080/warehouse_event'
    MD_data_prod_dir = IO_mother_dir + '/prod/LOCAL_DATA/FLAG/%s/' % date
    import time
    import os

    while (os.path.exists(MD_data_prod_dir + '%s_MD.success' % date) == False):
        print('等待MD或RDF或RISK或5分钟数据中')
        time.sleep(60)


    # ----------------------------更新项目二触发文件，添加形态和v2o10信息-------------------------------



    def view_bar(num, tot, s):
        rate = (num + 1) / (tot)
        rate_num = (int(rate * 100))
        n = rate_num // 3
        r = '\r[%s>%s]%d%%-%s' % ('=' * n, '-' * (33 - n), rate_num, s)
        sys.stdout.write(r)
        sys.stdout.flush()
        if rate == 1:
            print('\n')


    need_columns_tot = ['dt', 'Ticker', '前日形态', 'TN_v2o10', 'p2shouldBuySignal', '买入时点', 'T_c2o10', 'finish_indicator',
                        'absolute_profit',
                        'close_zt', 'high_zt', 'T_o2pre']
    need_columns = ['dt', 'Ticker', '前日形态', 'TN_v2o10', 'p2shouldBuySignal', '买入时点']

    if date <= '20210621':
        model_columns = ['RollLgbClaModel_local_prob', 'highPct5LgbClaModel_local_prob',
                         'lowPct5LgbClaModel_local_prob',
                         'highopen08LgbClaModel_local_prob', 'lowopen0LgbClaModel_local_prob',
                         'pat14XgbClaModel_local_prob',
                         'pat23XgbClaModel_local_prob', 'Saturn930DjClaModel_local_prob']
    # 20210621进行930版本迭代
    if date >= '20210622':
        old_model_columns = ['RollLgbClaModel_local_prob', 'highPct5LgbClaModel_local_prob',
                             'lowPct5LgbClaModel_local_prob',
                             'highopen08LgbClaModel_local_prob', 'lowopen0LgbClaModel_local_prob',
                             'pat14XgbClaModel_local_prob',
                             'pat23XgbClaModel_local_prob', 'Saturn930DjClaModel_local_prob']
        model_columns = ['openPctHighDjClaModel_local_prob', 'openPctHighWjClaModel_local_prob',
                         'openPctLowDjClaModel_local_prob',
                         'openPctLowWjClaModel_local_prob', 'pat3XgbClaModel_local_prob', 'pat4XgbClaModel_local_prob',
                         'totalDjClaModel_local_prob', 'totalWjClaModel_local_prob']
    # 获取昨天的标签汇总、今天的因子耗时和模型差异
    if lastdate <= '20210326':
        Labels_prod_summary_old = pd.DataFrame()
    else:
        Labels_prod_summary_old = pd.read_excel(
            '/data/group/800463/日内强势股/log_parse/因子耗时/实盘触发项目二标签汇总_%s.xlsx' % Alastdate)
    if 'twap2o10' not in Labels_prod_summary_old.columns:
        Labels_prod_summary_old['twap2o10'] = np.nan
    raw_last_date_factor_time_cost_pj2 = pd.read_excel(
        '/data/group/800463/日内强势股/log_parse/因子耗时/因子耗时_%s_prod.xlsx' % Alastdate, sheet_name='项目二930样本')
    '''raw_last_date_model_compare_pj2 = pd.read_excel(
        '/data/group/800463/日内强势股/log_parse/模型差异/%s/模型差异_%s_prod_pj2_930.xlsx' % (lastdate, lastdate)
        , sheet_name='本地投票结果').rename(columns={'Ticker': 'Unnamed: 0'})'''
    raw_last_date_model_compare_pj2_931 = pd.read_excel(
        '/data/group/800463/日内强势股/log_parse/模型差异/%s/模型差异_%s_prod_pj2_931.xlsx' % (lastdate, lastdate)
        , sheet_name='本地投票结果').rename(columns={'Ticker': 'Unnamed: 0'}).set_index(['Unnamed: 0'])
    raw_last_date_model_compare_pj2 = pd.DataFrame(index = raw_last_date_model_compare_pj2_931.index,columns = [
 '本地投票结果',
 'prod_signal',
 'is_sample_930',
 'openPctHighWjClaModel_local_prob',
 'openPctLowWjClaModel_local_prob',
 'totalWjClaModel_local_prob',
 'openPctHighDjClaModel_local_prob',
 'openPctLowDjClaModel_local_prob',
 'totalDjClaModel_local_prob',
 'pat3XgbClaModel_local_prob',
 'pat4XgbClaModel_local_prob'])
    raw_last_date_model_compare_pj2 = raw_last_date_model_compare_pj2.reset_index()
    raw_last_date_model_compare_pj2['本地投票结果'] = 0
    raw_last_date_model_compare_pj2['prod_signal'] = False
    raw_last_date_model_compare_pj2['is_sample_930'] = False
    #raw_last_date_model_compare_pj2['p2shouldBuySignal'] = False
    # 当前项目二买入时点为930
    raw_last_date_model_compare_pj2['买入时点'] = 930
    # 获取模型的预测结果
    # 如果昨天有模型没有给出预测（比如没有前日涨停样本、或者没有前高样本等分场景），则在模型差异中的投票结果中新建一个空的列
    for model_name in model_columns:
        if model_name not in raw_last_date_model_compare_pj2.columns:
            raw_last_date_model_compare_pj2[model_name] = np.nan
    raw_last_date_model_compare_pj2 = raw_last_date_model_compare_pj2[['Unnamed: 0'] + model_columns + ['买入时点']].rename(
        columns={'Unnamed: 0': 'Ticker'}) * 1
    raw_last_date_model_compare_pj2['dt'] = pd.Timestamp(Alastdate)
    # 计算买入时形态
    for index, row in raw_last_date_factor_time_cost_pj2.iterrows():
        stock_code, pre_date = row['Unnamed: 0'], lastdate
        #saturn_basic_info = pd.read_hdf( '/data/group/800463/project/project2_prod/everyday_Basic_v2/%s_%s/Basic_night_finish_%s_%s.h5' % (lastdate, lastdate, lastdate, lastdate))
        saturn_basic_info = pd.read_hdf('/data/group/800463/project/project2_prod/daily_data/Basic/Basic_closed_hf_finish.h5')  #
        raw_last_date_factor_time_cost_pj2.loc[index, '前日形态'] = saturn_basic_info.loc[lastdate, stock_code][
            'lzt_label_pattern']
    # 将耗时、模型预测拼入标签汇总
    raw_last_date_factor_time_cost_pj2['dt'] = pd.Timestamp(lastdate)
    raw_last_date_factor_time_cost_pj2['TN_v2o10'] = np.nan
    raw_last_date_factor_time_cost_pj2['p2shouldBuySignal'] = False
    raw_last_date_factor_time_cost_pj2 = raw_last_date_factor_time_cost_pj2.rename(columns={'Unnamed: 0': 'Ticker'})
    Labels_prod_summary_new = pd.concat([Labels_prod_summary_old,
                                         raw_last_date_factor_time_cost_pj2.set_index(['dt', 'Ticker']).join(
                                             raw_last_date_model_compare_pj2.set_index(['dt', 'Ticker'])).reset_index()[
                                             need_columns + model_columns]]) \
        .reset_index()[need_columns_tot + model_columns + old_model_columns + ['twap2o10']]
    # 对于v2o10还未算出的样本进行计算
    v2o10_nan_samples = Labels_prod_summary_new[
        (Labels_prod_summary_new['TN_v2o10'].isnull()) | (Labels_prod_summary_new['T_c2o10'].isnull())]
    date_ini = v2o10_nan_samples['dt'].apply(lambda x: x.strftime('%Y%m%d')).min()
    end_date = v2o10_nan_samples['dt'].apply(lambda x: x.strftime('%Y%m%d')).max()
    end_date_ = int(s.tradingday(end_date, 30)[-1])
    vwap_data = IO.read_data([date_ini, end_date_], columns=['vwap', 'adjfactor'],
                             alt=IO_mother_dir + '/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
    vwap_data['vwap'] = vwap_data['vwap'] * vwap_data['adjfactor']
    md_data = IO.read_data([date_ini, end_date_],
                           columns=['pre_close', 'open', 'high', 'low', 'close', 'vwap', 'adjfactor'],
                           alt=IO_mother_dir + '/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
    md_data['ul_price'] = np.floor(md_data['pre_close'] * 100 * 1.1 + 0.5) / 100
    md_data['new_300'] = (md_data.reset_index()['Ticker'].apply(lambda x: x[0] == '3') & (
                md_data.reset_index()['dt'] >= '20200824')).values
    md_data.loc[md_data['new_300'], 'ul_price'] = np.floor(
        md_data.loc[md_data['new_300'], 'pre_close'] * 100 * 1.2 + 0.5) / 100
    md_data['vwap'], md_data['pre_close'] = md_data['vwap'] * md_data['adjfactor'], md_data['pre_close'] * md_data[
        'adjfactor']
    md_data['high'], md_data['low'] = md_data['high'] * md_data['adjfactor'], md_data['low'] * md_data['adjfactor']
    md_data['ul_price'] = md_data['ul_price'] * md_data['adjfactor']
    md_data.loc[md_data['high'] == md_data['low'], 'vwap'] = np.nan
    md_data['next_vwap'] = md_data['vwap'].unstack().shift(-1).stack()
    md_data['next_vwap'] = md_data['next_vwap'].unstack().fillna(method='bfill', axis=0).stack()

    Labels_prod_summary_new_copy = Labels_prod_summary_new.copy()
    for i in v2o10_nan_samples.index:
        # i = 31
        buy_date = Labels_prod_summary_new.loc[i]['dt'].strftime('%Y%m%d')
        stock = Labels_prod_summary_new.loc[i]['Ticker']
        #saturn_basic_hf_info = pd.read_hdf('/data/group/800463/project/project2_prod/everyday_Basic_v2/%s_%s/Basic_closed_hf_finish_%s_%s.h5'% (buy_date, buy_date, buy_date, buy_date))
        saturn_basic_hf_info = pd.read_hdf('/data/group/800463/project/project2_prod/daily_data/Basic/Basic_closed_hf_finish.h5')  #
        T_day_930_10_twap_before_ZT = saturn_basic_hf_info['T_day_930_10_twap_before_ZT'].loc[buy_date, stock]
        this_buy_price = md_data['adjfactor'].loc[buy_date, stock] * T_day_930_10_twap_before_ZT
        this_v2o10 = (md_data['next_vwap'].loc[buy_date, stock] / this_buy_price - 1) * 100
        T_c2o10 = (vwap_data['vwap'].loc[buy_date, stock] / this_buy_price - 1) * 100
        if T_day_930_10_twap_before_ZT == -1:
            this_v2o10, T_c2o10 = -1, -1
        if T_day_930_10_twap_before_ZT == -3:
            this_v2o10, T_c2o10 = -3, -3
        Labels_prod_summary_new.loc[i, 'TN_v2o10'] = this_v2o10
        Labels_prod_summary_new.loc[i, 'T_c2o10'] = T_c2o10

    param = {'buy_vol_pct':0.2, 'sell_vol_pct': 0.1, 'max_amt': 500 * 10000, 'cover_amt':1500, 'p2_type':'930'}
    # -----计算卖出收益-----
    if 'finish_indicator' not in Labels_prod_summary_new.columns:
        Labels_prod_summary_new['finish_indicator'] = np.nan
    if 'absolute_profit' not in Labels_prod_summary_new.columns:
        Labels_prod_summary_new['absolute_profit'] = np.nan
    if 'twap2o10' not in Labels_prod_summary_new.columns:
        Labels_prod_summary_new['twap2o10'] = np.nan
    if 'close_zt' not in Labels_prod_summary_new.columns:
        Labels_prod_summary_new['close_zt'] = np.nan
    if 'high_zt' not in Labels_prod_summary_new.columns:
        Labels_prod_summary_new['high_zt'] = np.nan
    if 'T_o2pre' not in Labels_prod_summary_new.columns:
        Labels_prod_summary_new['T_o2pre'] = np.nan
    not_finished_old_holdings = Labels_prod_summary_new[(Labels_prod_summary_new['finish_indicator']!=1)]
    old_pct_start_date,old_pct_end_date = not_finished_old_holdings['dt'].min(),not_finished_old_holdings['dt'].max()
    old_pct_basic_file = pd.DataFrame()
    for dates in s.tradingday(old_pct_start_date.strftime('%Y%m%d'),old_pct_end_date.strftime('%Y%m%d')):
        #date_basic = pd.read_hdf('/data/group/800463/project/project2_prod/everyday_Basic_v2/%s_%s/Basic_closed_hf_finish_%s_%s.h5'%(dates,dates,dates,dates))
        date_basic = pd.read_hdf(
            '/data/group/800463/project/project2_prod/daily_data/Basic/Basic_closed_hf_finish.h5')  #
        old_pct_basic_file = pd.concat([old_pct_basic_file,
                            date_basic.loc[not_finished_old_holdings[not_finished_old_holdings['dt']==dates].set_index(['dt','Ticker']).index]])

    factor_df_twap = p2bt.factor_p2_profit_backtest(param=param, basic_file=old_pct_basic_file)

    for index, row in not_finished_old_holdings.iterrows():
        buy_date = row['dt']
        stock = row['Ticker']
        Labels_prod_summary_new.loc[index,['twap2o10','finish_indicator','absolute_profit']] = \
        factor_df_twap.rename(columns = {'pct':'twap2o10'}).loc[pd.Timestamp(buy_date),stock][['twap2o10','finish_indicator','absolute_profit']]

    close_high_zt_nan_samples = Labels_prod_summary_new[Labels_prod_summary_new['close_zt'].isnull()|Labels_prod_summary_new['high_zt'].isnull()]
    if len(close_high_zt_nan_samples) !=0:
        date_ini = close_high_zt_nan_samples['dt'].apply(lambda x: x.strftime('%Y%m%d')).min()
        end_date = close_high_zt_nan_samples['dt'].apply(lambda x: x.strftime('%Y%m%d')).max()
        MD_data = IO.read_data([date_ini, end_date], columns=['pre_close', 'high','close','open'],
                                    alt=IO_mother_dir+'/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
        MD_data['ul_price'] = np.floor(MD_data['pre_close'] * 100 * 1.1 + 0.5) / 100
        MD_data['new_300'] = (MD_data.reset_index()['Ticker'].apply(lambda x:x[0]=='3') & (MD_data.reset_index()['dt']>='20200824')).values
        MD_data.loc[MD_data['new_300'],'ul_price'] = np.floor(MD_data.loc[MD_data['new_300'],'pre_close'] * 100 * 1.2 + 0.5) / 100
        for i in close_high_zt_nan_samples.index:
            buy_date = Labels_prod_summary_new.loc[i]['dt'].strftime('%Y%m%d')
            stock = Labels_prod_summary_new.loc[i]['Ticker']
            Labels_prod_summary_new.loc[i, 'high_zt'] = (MD_data['ul_price'] == MD_data['high']).loc[buy_date,stock]
            Labels_prod_summary_new.loc[i, 'close_zt'] = (MD_data['ul_price'] == MD_data['close']).loc[buy_date,stock]
            Labels_prod_summary_new.loc[i, 'T_o2pre'] = 100*((MD_data['open'] / MD_data['pre_close'])-1).loc[buy_date,stock]


    Labels_prod_summary_new.to_excel('/data/group/800463/日内强势股/log_parse/因子耗时/实盘触发项目二标签汇总_%s.xlsx'%Adate,index=False)
    print('create file %s!!!!!!!!!!!!'%'/data/group/800463/日内强势股/log_parse/因子耗时/实盘触发项目二标签汇总_%s.xlsx'%Adate)





    #
    #
    # import os
    # for file in os.listdir('/data/group/800463/日内强势股/log_parse/日志拆分_re/'):
    #     for child_file in os.listdir('/data/group/800463/日内强势股/log_parse/日志拆分_re/%s/'%file):
    #         os.remove('/data/group/800463/日内强势股/log_parse/日志拆分_re/%s/%s'%(file,child_file))  # path是文件的路径，如果这个路径是一个文件夹，则会抛出OSError的错误，这时需用用rmdir()来删除
    #




















