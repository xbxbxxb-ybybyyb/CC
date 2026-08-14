# coding: utf-8
# Author：fengchi863
# Date ：2023/11/1 11:21

import sys
import os
sys.path.append('/data/user/015614/Lucien')

import pandas as pd
import numpy as np
import os
import datetime as dt
import shutil
from xquant.factordata import FactorData
s = FactorData()
from xquant.marketdata import MarketData
mdp = MarketData()
import time
import warnings
from shutil import copyfile
warnings.filterwarnings('ignore')
from LucienUtil import IO
from ProdWork.CommonTools import excel_saver, cal_time_delta, inttime2str
from ProdWork.log_analyse.p4_log_parse.xdev.LogParse import LogParse

def get_TN_o2ul(start_date, end_date):
    md_data = IO.read_data([start_date, end_date], columns=['pre_close', 'open', 'high', 'low', 'close', 'vwap', 'adjfactor'],
                           alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
    md_data['ul_price'] = np.floor(md_data['pre_close'] * 100 * 1.1 + 0.5) / 100
    md_data['new_300'] = (md_data.reset_index()['Ticker'].apply(lambda x: x[0] == '3') & (md_data.reset_index()['dt'] >= '20200824')).values
    md_data.loc[md_data['new_300'], 'ul_price'] = np.floor(md_data.loc[md_data['new_300'], 'pre_close'] * 100 * 1.2 + 0.5) / 100
    md_data['open'], md_data['close'] = md_data['open'] * md_data['adjfactor'], md_data['close'] * md_data['adjfactor']
    md_data['vwap'], md_data['pre_close'] = md_data['vwap'] * md_data['adjfactor'], md_data['pre_close'] * md_data['adjfactor']
    md_data['high'], md_data['low'] = md_data['high'] * md_data['adjfactor'], md_data['low'] * md_data['adjfactor']
    md_data['ul_price'] = md_data['ul_price'] * md_data['adjfactor']
    md_data['label_T_o2ul'] = md_data['open'].unstack().shift(-1).stack() / md_data['ul_price'] - 1
    md_data.loc[md_data['high'] == md_data['low'], 'open'] = np.nan
    md_data.loc[md_data['high'] == md_data['low'], 'vwap'] = np.nan
    md_data['next_open'] = md_data['open'].unstack().shift(-1).stack()
    md_data['next_vwap'] = md_data['vwap'].unstack().shift(-1).stack()
    md_data['next_open'] = md_data['next_open'].unstack().fillna(method='bfill', axis=0).stack()
    md_data['next_vwap'] = md_data['next_vwap'].unstack().fillna(method='bfill', axis=0).stack()
    md_data['label_TN_o2ul'] = md_data['next_open'] / md_data['ul_price'] - 1
    return md_data

def cal_sell_start_time(df):
    if 'PENDING_NEW' in list(df['ordStatus']):
        sell_start_time = df[df['ordStatus'] == 'PENDING_NEW']['transactionTime'].apply(lambda x: int(x[11:13] + x[14:16] + x[17:19] + x[20:23])).values[0]
    else:
        sell_start_time = df['transactionTime'].apply(lambda x: int(x[11:13] + x[14:16] + x[17:19] + x[20:23])).values.min()
    return sell_start_time

def cal_sell_end_time(df):
    if 'FILLED' in list(df['ordStatus']):
        sell_end_time = df[df['ordStatus'] == 'FILLED']['transactionTime'].apply(lambda x: int(x[11:13] + x[14:16] + x[17:19] + x[20:23])).values.max()
    else:
        sell_end_time = df['transactionTime'].apply(lambda x: int(x[11:13] + x[14:16] + x[17:19] + x[20:23])).values.max()
    return sell_end_time


if __name__ == "__main__":
    tradeDate = dt.datetime.now().strftime('%Y-%m-%d')
    tradeDate = '2024-10-08'    # 当天即可
    nowdate = tradeDate[:4] + tradeDate[5:7] + tradeDate[8:]
    begindate, enddate = nowdate, nowdate
    # begindate, enddate = '20230821', '20230908'

    for date in s.tradingday(begindate, enddate):
        tradeDate = f'{date[:4]}-{date[4:6]}-{date[6:]}'
        tradeDatestr = tradeDate[:4] + tradeDate[5:7] + tradeDate[-2:]
        lastdate = s.tradingday(tradeDatestr, -2)[0]
        lastdate_h = pd.Timestamp(s.tradingday(tradeDatestr, -2)[0]).strftime('%Y-%m-%d')
        # environment_lst =['prod', 'UAT', 'SZEX', 'SHEX']
        # environment_lst =['UAT']
        # environment_lst =['prod', 'SHEX']
        # environment_lst =['test']
        # environment_lst =['thread']
        # environment_lst =['UAT']
        environment_lst =['xdev3']
        for environment in environment_lst:
            print(tradeDate, environment, '\n')
            # ------------ 按环境加载日志的目录 ---------------
            import gzip
            file_name = f'/data/group/800463/StrategyLog/prd/{environment}.EventDrivenCpp-{tradeDate}.log.gz'
            if environment == 'UAT':
                # file_name = f'/data/group/800463/StrategyLog/sim/CeresStrategy-{tradeDate}.log.gz'
                file_name = f'/data/group/800463/日内强势股/ceres_log/sim/CeresStrategy-{tradeDate}.log.gz'
            if 'night' in environment:
                file_name = '/data/group/800463/StrategyLog/sim/StrongStrategy.log.gz/EventDrivenCpp-%s.log.gz' % tradeDate
            if environment == 'prod':
                file_name = '/data/group/800463/StrategyLog/prd/StrongStrategy-%s.log.gz' % tradeDate
            if environment == 'SHEX':
                file_name = '/data/group/800463/StrategyLog/prd/SHEX.EventDrivenCpp-' + tradeDate + '.log.gz'
            if environment == 'SZEX':
                file_name = '/data/group/800463/StrategyLog/prd/SZEX.EventDrivenCpp-' + tradeDate + '.log.gz'
            if environment == 'test':
                # file_name = '/data/group/800463/xiely/save-file/forFc/log/log_local_20230629.txt'
                file_name = f'/data/group/800463/日内强势股/ceres_log/sim/EventDrivenStrategy-{tradeDate}.gz'
            if environment in ['thread', 'xdev', 'xdev2', 'xdev3']:
                # file_name = f'/data/user/013551/forXT/log/local_log/eventdriven_log/20231108-xdev38-ceres.log'
                # file_name = f'/data/user/013551/forXT/log/local_log/ceres/ceres_log_xdev_20240119.log'
                # file_name = f'/data/group/800463/xiely/save-file/log/{tradeDate.replace("-", "")}_shsz.log'
                # file_name = f'/data/user/013551/forXT/Ceres/log/20250319/ceres_{tradeDatestr}_shsz.log'
                # file_name = f'/data/user/013551/forXT/Ceres/log/20250320/xdev_ceres_{tradeDatestr}.log'
                # file_name = f'/data/user/013551/forXT/Ceres/log/{nowdate}_type1.log'
                file_name = f'/data/user/013551/forXT/Ceres/log/{nowdate}_type1.log'

            print(file_name)

            # while not os.path.exists(file_name):
            #     print('等待%s日志中'%environment)
            #     time.sleep(60)

            sz_log_fpath = f'/data/group/800463/StrategyLog/prd/SZEX.CeresStrategy-{tradeDate}.log.gz'
            sh_log_fpath = f'/data/group/800463/StrategyLog/prd/SHEX.CeresStrategy-{tradeDate}.log.gz'
            if environment == 'prod' and os.path.exists(sz_log_fpath):
                sz_file = gzip.GzipFile(sz_log_fpath)
                sz_lines = sz_file.readlines()
                copyfile(sz_log_fpath, '/data/group/800463/日内强势股/ceres_log/SZEX.CeresStrategy-%s.log.gz' % tradeDate)
                print(f'from {sz_log_fpath} to /data/group/800463/日内强势股/ceres_log/SZEX.CeresStrategy-{tradeDate}.log.gz 上传成功')
            else:
                sz_lines = []

            if environment == 'prod' and os.path.exists(sh_log_fpath):
                sh_file = gzip.GzipFile(sh_log_fpath)
                sh_lines = sh_file.readlines()
                copyfile(sh_log_fpath, f'/data/group/800463/日内强势股/ceres_log/SHEX.CeresStrategy-{tradeDate}.log.gz')
                print(f'from {sh_log_fpath} to /data/group/800463/日内强势股/ceres_log/SHEX.CeresStrategy-{tradeDate}.log.gz 上传成功')
            else:
                sh_lines = []

            # if environment == 'UAT' and os.path.exists(file_name):
            #     uat_file = gzip.GzipFile(file_name)
            #     uat_lines = uat_file.readlines()
            #     copyfile(file_name, '/data/group/800463/日内强势股/ceres_log/sim/CeresStrategy-%s.log.gz' % tradeDate)
            #     print('from %s to /data/group/800463/日内强势股/ceres_log/sim/CeresStrategy-%s.log.gz 上传成功' % (file_name, tradeDate))

            if environment not in ['prod']:
                if file_name.endswith('gz'):
                    other_file = gzip.GzipFile(file_name)
                    other_lines = other_file.readlines()
                else:
                    other_file = open(file_name)
                    other_lines = other_file.readlines()
                    # other_lines = list(filter(lambda x: str(x).startswith(f"2024-01-31") and 'INFO' in str(x), other_lines))
                    # other_lines = list(filter(lambda x: 'info' in str(x) and 'Thread' in str(x), other_lines))
                    other_lines = list(filter(lambda x: 'INFO' in str(x) and 'algo' in str(x), other_lines))
                    # other_lines = list(filter(lambda x: 'thread' in str(x), other_lines))
                # other_lines = list(filter(lambda x: str(x).startswith("b'2024-"), other_lines))
                # other_lines = list(filter(lambda x: 'thread' in str(x), other_lines))
            else:
                other_lines = []

            lines = other_lines + sh_lines + sz_lines
            lp_inst = LogParse(environment, tradeDatestr, lines)
            print('日志数据读取完毕\n', len(lp_inst.lines))

            # 拆分日志
            log_split_path = f'/data/group/800463/日内强势股/ceres_log_parse/日志拆分/{tradeDatestr}_{environment}环境/'
            if os.path.exists(log_split_path):
                shutil.rmtree(log_split_path)   # NOTE: 删除路径下所有文件，注意路径是否写错！！！
            os.makedirs(log_split_path, exist_ok=True)
            for code, log in lp_inst.log_dic.items():
                if code in lp_inst.algo_code_dict.keys():
                    code_code = lp_inst.algo_code_dict[code]
                    if os.path.exists(log_split_path + f'{tradeDatestr}-{code_code}-{environment}环境.txt'):
                        write_mode = 'a+'
                    else:
                        write_mode = 'w'
                    with open(log_split_path + f'{tradeDatestr}-{code_code}-{environment}环境.txt', write_mode) as file_handle:
                        for line in log:
                            file_handle.write(str(line))

            # 解析日志开始
            inf_df_ceres, trade_dic, now_trade_dic, order_info_df, unfilled_info_df, new_trade_dic, factor_df_ceres, \
            factor_df_ceres930, daily_zt_df_ceres, all_code_model_data_ceres = lp_inst.start_parsing()

            except_df = lp_inst.get_except_df()
            save_index_ceres = list(set(factor_df_ceres.index.tolist()))

            # TODO: 因为没有isSkip和isMock两个key，先注释掉以下4行
            inf_df_ceres = inf_df_ceres.copy()
            inf_df_ceres = inf_df_ceres.loc[list(set(inf_df_ceres.index.tolist()) & set(save_index_ceres))].sort_index()
            save_index_ceres = inf_df_ceres.index.tolist()
            daily_zt_df_ceres = daily_zt_df_ceres.loc[list(set(daily_zt_df_ceres.index.tolist()) & set(save_index_ceres))].sort_index()

            excel_saver({'930': factor_df_ceres930.loc[save_index_ceres].sort_index(),
                         '931': factor_df_ceres.loc[save_index_ceres].sort_index()},
                        '/data/group/800463/日内强势股/ceres_log_parse/因子数据/因子数据Ceres_%s_%s.xlsx' % (tradeDate, environment))
            print('create file %s' % '/data/group/800463/日内强势股/ceres_log_parse/因子数据/因子数据Ceres_%s_%s.xlsx' % (tradeDate, environment))

            if len(except_df) > 0:
                except_df.to_excel('/data/group/800463/日内强势股/ceres_log_parse/异常报错/异常报错_%s_%s.xlsx' % (tradeDate, environment))
                print('create file %s' % '/data/group/800463/日内强势股/ceres_log_parse/异常报错/异常报错_%s_%s.xlsx' % (tradeDate, environment))
            md_data_path = '/data/group/800463/日内强势股/ceres_log_parse/行情数据/%s_%s/' % (tradeDate, environment)
            model_factor_data_path = '/data/group/800463/日内强势股/ceres_log_parse/模型数据/%s_%s/' % (tradeDate, environment)

            if not os.path.exists(md_data_path):
                os.makedirs(md_data_path)
            if not os.path.exists(model_factor_data_path):
                os.makedirs(model_factor_data_path)
            if len(trade_dic.keys()) != len(now_trade_dic.keys()):
                print('trade_dic和now_trade_dic长度不一致')

            model_total_keys_ceres = []
            for model_dict in all_code_model_data_ceres.values():
                model_total_keys_ceres += list(model_dict.keys())
            model_total_keys_ceres = list(np.unique(np.array(model_total_keys_ceres)))
            total_keys_ceres = list(set(trade_dic.keys()).union(set(now_trade_dic.keys())).union(set(model_total_keys_ceres)))

            if 'ZT_Time' in inf_df_ceres.columns.tolist():
                inf_df_ceres = inf_df_ceres.sort_values('ZT_Time')
                inf_df_ceres['ZT_Time_str'] = inf_df_ceres['ZT_Time'].apply(inttime2str)
                daily_zt_df_ceres['ZT_Time'] = inf_df_ceres['ZT_Time'].loc[daily_zt_df_ceres.index]
            inf_df_ceres['machine_code'] = pd.Series(lp_inst.machine_code_dict).loc[inf_df_ceres.index].values

            tupo_excel_dic = {'每日突破Ceres': daily_zt_df_ceres,
                              '每日订单': order_info_df,
                              '每日拒绝': unfilled_info_df}
            excel_saver(tupo_excel_dic, '/data/group/800463/日内强势股/ceres_log_parse/每日突破/每日突破_%s_%s.xlsx' % (tradeDatestr, environment))

            if (environment == 'prod') | (environment == 'SHEX') | (environment =='SZEX'):
                if len(order_info_df) == 0:
                    buy_guadan_num = pd.DataFrame()
                    buy_chengjiao_num = pd.DataFrame()
                    sell_guadan_num = pd.DataFrame()
                    sell_chengjiao_num = pd.DataFrame()
                    sell_time_start = pd.DataFrame()
                    sell_time_end = pd.DataFrame()
                else:
                    buy_order_info_df = order_info_df[(order_info_df['orderType'] == 'SplitLastShot')|
                                                      (order_info_df['orderType']  == 'MRiskSplitShot')|
                                                      (order_info_df['orderType'] == 'JupiterFirstOrder')|
                                                      (order_info_df['orderType'] == 'MRiskSplitLastShotBuy')|
                                                      (order_info_df['orderType'] == 'MRiskSplitShotBuy')]
                    if len(buy_order_info_df) == 0:
                        buy_guadan_num = pd.DataFrame()
                        buy_chengjiao_num = pd.DataFrame()
                    else:
                        buy_guadan_num = buy_order_info_df.groupby('stockcode').apply(lambda x: sum(x['ordStatus'] == 'PENDING_NEW'))
                        buy_chengjiao_num = buy_order_info_df.groupby('stockcode').apply(lambda x: sum(x['ordStatus'].apply(lambda x: 'FILLED' in x)))
                    sell_order_info_df = order_info_df[(order_info_df['orderType'] == 'OpenSell') | \
                                                       (order_info_df['orderType'] == 'CommonSell') | \
                                                       (order_info_df['orderType'] == 'HighLimitSell')]
                    if len(sell_order_info_df) == 0:
                        sell_guadan_num = pd.DataFrame()
                        sell_chengjiao_num = pd.DataFrame()
                        sell_time_start = pd.DataFrame()
                        sell_time_end = pd.DataFrame()
                    else:
                        sell_guadan_num = sell_order_info_df.groupby('stockcode').apply(lambda x: sum(x['ordStatus'] == 'PENDING_NEW'))
                        sell_chengjiao_num = sell_order_info_df.groupby('stockcode').apply(lambda x: sum(x['ordStatus'].apply(lambda x: 'FILLED' in x)))
                        sell_time_start = sell_order_info_df.groupby('stockcode').apply(cal_sell_start_time)
                        sell_time_end = sell_order_info_df.groupby('stockcode').apply(cal_sell_end_time)
                buy_statistics = pd.concat([buy_guadan_num, buy_chengjiao_num], axis=1).rename(columns={0: '买入当日挂单笔数', 1: '买入当日成交笔数'})

                sell_statistics = pd.concat([sell_guadan_num, sell_chengjiao_num, sell_time_start, sell_time_end], axis=1) \
                    .rename(columns={0: '卖出挂单笔数', 1: '卖出成交笔数', 2: '卖出开始时间', 3: '卖出结束时间'})

                inf_df_dic = {'因子耗时Ceres': inf_df_ceres,
                              '买单统计': buy_statistics,
                              '卖单统计': sell_statistics,
                              '机器统计': pd.Series(lp_inst.machine_counter_dict)}

                # -------------- 生产上才分析未成交的原因 -------------------
                if environment == 'prod':
                    hist_non_trade = pd.read_excel('/data/group/800463/日内强势股/ceres_log_parse/因子耗时/因子耗时_%s_%s.xlsx'% (lastdate_h, environment), sheetname='未成交统计')
                    hnt_need_col = list(hist_non_trade.columns)
                    hnt_need_col.remove('Unnamed: 0')
                    hist_non_trade = hist_non_trade[hnt_need_col]
                    if len(buy_statistics) != 0:    # 当天可能没有任何成交
                        buy_no_deal_stock_list = list(buy_statistics[(buy_statistics['买入当日成交笔数'] == 0) & (buy_statistics['买入当日挂单笔数'] != 0)].index)
                        if len(unfilled_info_df) != 0:
                            remove_list = list(unfilled_info_df[unfilled_info_df['riskSummary'].apply(lambda x: ('对敲' in x) | ('隔离' in x))]['stockcode'])
                            for stockcode in remove_list:
                                if stockcode in buy_no_deal_stock_list:
                                    buy_no_deal_stock_list.remove(stockcode)

                        for stock in buy_no_deal_stock_list:
                            # 取涨停价格
                            print('未成交样本:%s' % stock)
                            df = mdp.get_data_by_date("Transaction", stock, tradeDatestr)
                            df_need = df[
                                ['MDDate', 'MDTime', 'SecurityID', 'TradeIndex', 'TradeType', 'TradeBuyNo', 'TradeSellNo', 'TradeBSFlag', 'TradePrice',
                                 'TradeQty','TradeMoney', 'ReceiveDateTime']].sort_values(['TradeIndex'])
                            df_need_normal = df_need[df_need['TradePrice'] != 0]
                            ZT_price = df_need['TradePrice'].max()
                            ZT_Time = df_need[df_need['TradePrice'] == ZT_price]['MDTime'].min()

                            print('ZTTime', ZT_Time)
                            data_lag = cal_time_delta(int(ZT_Time), int(str(df_need[df_need['MDTime'] == ZT_Time]['ReceiveDateTime'].min())[8:]))
                            print('%s~%s，行情延迟时长:%s ms'%(str(ZT_Time),str(df_need[df_need['MDTime'] == ZT_Time]['ReceiveDateTime'].min())[8:],str(data_lag)))
                            dummy_index = len(hist_non_trade)
                            hist_non_trade.loc[dummy_index,'发生日期'] = pd.Timestamp(tradeDate)
                            hist_non_trade.loc[dummy_index,'ZT_Time'] = ZT_Time
                            hist_non_trade.loc[dummy_index,'证券代码'] = stock
                            name_data = IO.read_data([lastdate, lastdate]
                                                     , alt='/data/group/800080/warehouse/prod/FCD/CHINA_STOCK/DAILY/SUNTIME/FCD_CHINA_STOCK_DAILY_SUNTIME.h5')
                            hist_non_trade.loc[dummy_index,'证券名称'] = name_data.loc[lastdate,stock]['STOCK_NAME'].values[~0]
                            hist_non_trade.loc[dummy_index,'行情延迟'] = data_lag
                        if tradeDatestr == '20210526':
                            label_TN_o2ul = get_TN_o2ul('20200318',tradeDatestr)['label_TN_o2ul']
                            hist_non_trade['o2ul'] = label_TN_o2ul.reindex(hist_non_trade.rename(columns = {'发生日期':'dt','证券代码':'Ticker'}).set_index(['dt','Ticker']).sort_index().index).values
                        else:
                            if len(hist_non_trade[hist_non_trade['o2ul'].isnull()]) == 0:
                                pass
                            elif hist_non_trade[hist_non_trade['o2ul'].isnull()]['发生日期'].min().strftime('%Y%m%d') != tradeDatestr:
                                label_TN_o2ul = get_TN_o2ul(hist_non_trade[hist_non_trade['o2ul'].isnull()]['发生日期'].min().strftime('%Y%m%d'),tradeDatestr)['label_TN_o2ul']
                                o2ul_nan_sample = hist_non_trade[hist_non_trade['o2ul'].isnull()].index
                                hist_non_trade.loc[o2ul_nan_sample,'o2ul'] = label_TN_o2ul.reindex(hist_non_trade[hist_non_trade['o2ul'].isnull()]\
                                                                                                   .rename(columns = {'发生日期':'dt','证券代码':'Ticker'})\
                                                                                                   .set_index(['dt','Ticker']).sort_index().index).values
                    inf_df_dic['未成交统计'] = hist_non_trade
            else:
                inf_df_dic = {'因子耗时Ceres': inf_df_ceres,
                              '机器统计': pd.Series(pd.Series(lp_inst.machine_counter_dict))}

            excel_saver(inf_df_dic, '/data/group/800463/日内强势股/ceres_log_parse/因子耗时/因子耗时_%s_%s.xlsx' % (tradeDate, environment))

