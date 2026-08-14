import sys
import os
sys.path.append('/data/user/015614/Lucien')

import pandas as pd
import re
import numpy as np
import os
import datetime as dt
from xquant.factordata import FactorData
s = FactorData()
from xquant.marketdata import MarketData
mdp = MarketData()
import time
import warnings
from shutil import copyfile
warnings.filterwarnings('ignore')
from LucienUtil import IO
from ProdWork.CommonTools import excel_saver, cal_time_delta,inttime2str
from ProdWork.log_analyse.cpp_local_log_parse.local_cpp_log_parse20240628.LogParse_Tool import LogParse_Tool
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
    # 当前版本只能用于20230602 单实例模式以后
    tradeDate = dt.datetime.now().strftime('%Y-%m-%d')
    tradeDate = '2025-03-10'    # 当天即可
    nowdate = tradeDate[:4] + tradeDate[5:7] + tradeDate[8:]
    begindate, enddate = '20250310','20250310'

    for date in s.tradingday(begindate, enddate):
        tradeDate = '%s-%s-%s'%(date[:4],date[4:6],date[6:])
        tradeDatestr = tradeDate[:4]+tradeDate[5:7] + tradeDate[-2:]#dt.datetime.now().strftime('%Y%m%d')
        lastdate = s.tradingday(tradeDatestr, -2)[0]
        lastdate_h = pd.Timestamp(s.tradingday(tradeDatestr, -2)[0]).strftime('%Y-%m-%d')
        # environment_lst = ['prod', 'SZEX', 'SHEX', 'UAT_49_53', 'UAT_50_51', 'UAT']  # ,'UAT_75_77_78','UAT_79_81_82','UAT_50_51_83','UAT_lite','UAT_other']# ['prod','UAT','night','test1','SZEX','SHEX','UAT_49_53','UAT_50_51','UAT_lite','UAT_other']#[:1]#
        # environment_lst =['prod', 'SZEX', 'SHEX', 'UAT_49_53']
        # environment_lst =['night']
        # environment_lst =['UAT_lite']
        # environment_lst =['prod', 'UAT']
        # environment_lst =['UAT']
        # environment_lst =['prod', 'SHEX']
        environment_lst =['test']
        # environment_lst =['SZEX']
        for environment in environment_lst:
            print(tradeDate, environment, '\n')
            # ------------ 按环境加载日志的目录 ---------------
            import gzip
            file_name = f'/data/group/800463/StrategyLog/prd/{environment}.EventDrivenCpp-{tradeDate}.log.gz'
            if environment == 'UAT':
                file_name = '/data/group/800463/StrategyLog/sim/EventDrivenCpp-%s.log.gz' % tradeDate
                # file_name = '/data/group/800463/日内强势股/log/StrongStrategy-' + tradeDate + '-uat.log.gz'
                # file_name = f'/data/group/800463/日内强势股/cpp_log/sim/EventDrivenCpp-{tradeDate}.log.gz'
            if environment == 'UAT_lite':
                #file_name = '/data/group/800463/StrategyLog/sim/StrongStrategy-%s.log.gz' % tradeDate
                file_name = '/data/group/800463/日内强势股/log/StrongStrategy-' + tradeDate + '-uat_lite.log.gz'
            if environment == 'night':
                #file_name = '/data/group/800463/StrategyLog/sim/StrongStrategy-%s.log.gz' % tradeDate
                file_name = '/data/group/800463/StrategyLog/sim/EventDrivenCpp-%s.log.gz' % tradeDate
            if 'night' in environment:
                # log_file_path = '/data/group/800463/日内强势股/log/StrongStrategy-' + tradeDate + '-night.log'
                # file_name = '/data/group/800463/日内强势股/log/StrongStrategy-' + tradeDate + '-%s.log.gz'%environment
                file_name = '/data/group/800463/StrategyLog/sim/StrongStrategy.log.gz/EventDrivenCpp-%s.log.gz' % tradeDate
            if environment == 'prod':
                # log_file_path = '/data/group/800463/日内强势股/log/StrongStrategy-' + tradeDate + '.log'
                file_name = '/data/group/800463/StrategyLog/prd/StrongStrategy-%s.log.gz' % tradeDate
                # file_name = '/data/group/800463/StrategyLog/prd/StrongStrategy-%s-1515.log.gz' % tradeDate
            if environment == 'prod_test':
                log_file_path = '/data/group/800463/日内强势股/log/StrongStrategy2-' + tradeDate + '.log'
            if environment == 'SHEX':
                # file_name = '/data/group/800463/日内强势股/log/StrongStrategy-' + tradeDate + '-SHEX.log.gz'
                file_name = '/data/group/800463/StrategyLog/prd/SHEX.EventDrivenCpp-' + tradeDate + '.log.gz'
            if environment == 'SZEX':
                # file_name = '/data/group/800463/日内强势股/log/StrongStrategy-' + tradeDate + '-SZEX.log.gz'
                file_name = '/data/group/800463/StrategyLog/prd/SZEX.EventDrivenCpp-' + tradeDate + '.log.gz'
            if environment == 'test':
                # file_name = '/data/group/800463/xiely/save-file/forFc/log/log_local_20230629.txt'
                # file_name = '/data/user/013551/forXT/Europa/v3_kcb_local_log/'
                # file_name = '/data/user/013551/forXT/Europa/202410110002/20241008_shsz.log'
                file_name = f'/data/user/013551/forXT/202503120004/europa/for_cmp/1_3_20250310_688680.SH.log'
            print(file_name)
            '''while (os.path.exists(file_name) == False):
                print('等待%s日志中'%environment)
                time.sleep(60)
            time.sleep(60)'''
            #file_name ='/data/user/013550/ceress1_20211111.log.gz'#'/data/user/013550/ceress1_20211115_night3.log.gz'#
            #file_name = '/data/group/800463/xiely/save-file/StrongStrategy-2021-11-25-hf.log.gz'
            # FIXME：分别是IT传进来和谢璐遥传进来的
            o45file_name = '/data/group/800463/StrategyLog/prd/SZEX.EventDrivenCpp-' + tradeDate + '.log.gz' # '/data/group/800463/日内强势股/log/StrongStrategy-%s-SZEX.log.gz'#
            # o45file_name = '/data/group/800463/xiely/日内强势股/log/StrongStrategy-' + tradeDate + '-SZEX.log.gz'
            o45file_SHname = '/data/group/800463/StrategyLog/prd/SHEX.EventDrivenCpp-' + tradeDate + '.log.gz'
            if environment == 'prod' and os.path.exists(o45file_name):
                print('提取o45日志')
                o45_g_file = gzip.GzipFile(o45file_name)
                o45_lines = o45_g_file.readlines()
                #o45_lines = list(filter(lambda x: str(x).find("2022-02-14T"), o45_lines))
                print('SZ',len(o45_lines))
                copyfile(o45file_name,'/data/group/800463/日内强势股/cpp_log/SZEX.EventDrivenCpp-%s.log.gz' % tradeDate)
                print('from %s to /data/group/800463/日内强势股/cpp_log/SZEX.EventDrivenCpp-%s.log.gz 上传成功' % (o45file_name, tradeDate))
            else:
                o45_lines = []
            if environment == 'prod' and os.path.exists(o45file_SHname):
                print('提取o45SH日志')
                o45_g_SHfile = gzip.GzipFile(o45file_SHname)
                o45_SHlines = o45_g_SHfile.readlines()
                print('SH', len(o45_SHlines))
                copyfile(o45file_SHname, '/data/group/800463/日内强势股/cpp_log/SHEX.EventDrivenCpp-%s.log.gz' % tradeDate)
                print('from %s to /data/group/800463/日内强势股/cpp_log/SHEX.EventDrivenCpp-%s.log.gz 上传成功' % (o45file_SHname, tradeDate))
            else:
                o45_SHlines = []
            if environment == 'UAT' and os.path.exists(file_name):
                uat_file = gzip.GzipFile(file_name)
                uat_lines = uat_file.readlines()
                copyfile(file_name, '/data/group/800463/日内强势股/cpp_log/sim/EventDrivenCpp-%s.log.gz' % tradeDate)
                print('from %s to /data/group/800463/日内强势股/cpp_log/sim/EventDrivenCpp-%s.log.gz 上传成功' % (file_name, tradeDate))

            # if environment not in  ['prod']:
            #     # g_file = gzip.GzipFile(file_name)
            #     log_file_list = os.listdir(file_name)
            #     log_file_list = list(filter(lambda x: x.startswith(tradeDatestr), log_file_list))
            #     lines = []
            #     for filename in log_file_list:
            #         g_file = open(file_name + filename)
            #         tmp_lines = g_file.readlines()
            #         lines += tmp_lines
            #     # lines = list(filter(lambda x: str(x).find("2022-02-14T"), lines))
            if environment not in  ['prod']:
                g_file = open(file_name)
                lines = g_file.readlines()
                # lines = list(filter(lambda x: str(x).find("2022-02-14T"), lines))
            else:
                lines = []
            lines = lines + o45_lines + o45_SHlines
            lines = list(filter(lambda x: str(x).startswith('[2025-'), lines))  # TODO: 2024年要更换一下吧?
            # file_name = '/data/group/800463/xiely/save-file/big_log_20211112.txt'  #
            # with open(file_name, encoding='UTF-8') as f: lines = f.readlines()
            # with open(log_file_path_2, encoding='UTF-8') as f: lines_2 = f.readlines()
            # lines = lines_1 + lines_2
            # with open(log_file_path, encoding='UTF-8') as f: lines_raw = f.readlines()
            # lines = list(np.array(lines_raw)[np.array(list(map(lambda x:int(x[11:13]) >= 17,lines_raw)))])
            # logpath = '/data/group/800463/日内强势股/log/2023-04-20_21-06-29/2023-04-20_21-06-29/'
            # logfiles = list(filter(lambda x: x.find('.log')>=0,os.listdir(logpath)))
            # for date in s.tradingday('20230327','20230412'):
            #     cur_files = list(filter(lambda x: x.find(date)>=0,logfiles))
            #     line = ''
            #     for file in cur_files:
            #         with open(logpath+file,'r', encoding='utf-8') as f:
            #             #lines_2 = f.read()
            #             line = line + f.read()
            #             f.close()
            #     with open(logpath + 'StrongStrategy-%s-%s-%s-uat.log' % (date[:4], date[4:6], date[6:]),'a',encoding='utf-8') as f:
            #         f.write(line)
            #         f.close()
            '''
            import gzip
            for date in hfactor.tradingday('20230327','20230412'):
                f_in = open('/data/group/800463/xiely/save-file/for_wj/log/log_sim_%s.txt'%date, 'rb')
                f_out = gzip.open('/data/group/800463/日内强势股/log/StrongStrategy-%s-%s-%s-uat_lite.log.gz'% (date[:4], date[4:6], date[6:]), 'wb')
                f_out.writelines(f_in)
                f_out.close()
                f_in.close()
            import gzip
            f_in = open('/data/group/800463/xiely/save-file/big_log_20211112.txt', 'rb')
            f_out = gzip.open('/data/user/013550/ceress1_20211112.log.gz', 'wb')
            f_out.writelines(f_in)
            f_out.close()
            f_in.close()
            import gzip
            f_in = open('/data/user/015614/shared/for_wj/log/StrongStrategy-2023-03-06-uat_lite-20230328.txt', 'rb')
            f_out = gzip.open('/data/group/800463/日内强势股/log/StrongStrategy-2023-03-06-uat_lite.log.gz', 'wb')
            f_out.writelines(f_in)
            f_out.close()
            f_in.close()
            '''
            logparse = LogParse_Tool(environment, tradeDatestr, lines)
            print('日志数据读取完毕\n', len(logparse.lines))

            # 拆分日志
            log_split_file_path = '/data/group/800463/日内强势股/cpp_log_parse/日志拆分/%s_%s环境/' % (tradeDatestr, environment)
            # TODO: 这里要先删除这个文件夹中的所有内容，防止在上次的结果上追加
            if not os.path.exists(log_split_file_path):
                os.makedirs(log_split_file_path)
            for code, log in logparse.log_dic.items():
                if code in logparse.algo_code_dict.keys():
                    code_code = logparse.algo_code_dict[code]
                    with open(log_split_file_path + '%s-%s-%s环境.txt' % (tradeDatestr, code_code, environment), 'a+') as file_handle:
                        for line in log:
                            file_handle.write(str(line))

            zuhe_list = []

            # 解析日志
            use_zuhe = False
            # inf_df_,inf_df_pj2_930,inf_df_pj2_931, factor_df, trade_dic, now_trade_dic, all_code_model_data,all_code_model_data_pj2_930,all_code_model_data_pj2_931, daily_zt_df, daily_pj2_df, order_info_df, unfilled_info_df,factor_df_pj2_930,factor_df_pj2_931, \
            # new_trade_dic,factor_df_pj3_931,inf_df_pj3_931,factor_df_pj3_930,inf_df_pj3_930,daily_pj3_df, \
            # inf_df001_, factor_df001, all_code_model_data001, daily_zt_df001  = logparse.get_inf_from_log(use_zuhe, zuhe_list)
            # TODO: 很多返回变量
            inf_df_, inf_df_pj2_930, inf_df_pj2_931, \
            factor_df, trade_dic, now_trade_dic, all_code_model_data, all_code_model_data_pj2_930, all_code_model_data_pj2_931, \
            daily_zt_df, daily_pj2_df, \
            order_info_df, unfilled_info_df, factor_df_pj2_930, factor_df_pj2_931, \
            new_trade_dic, factor_df_pj3_931, inf_df_pj3_931, factor_df_pj3_930, inf_df_pj3_930, daily_pj3_df, \
            inf_df001_, factor_df001, all_code_model_data001, daily_zt_df001, \
            inf_df_pj2_931_sellv1, inf_df_pj2_931_sellv3, all_code_model_data_pj2_931_sellv1, all_code_model_data_pj2_931_sellv3, \
            factor_df_pj2_931_sell, factor_df_pj2_930_sell, \
            inf_df_metis_, factor_df_metis, daily_zt_df_metis, all_code_model_data_metis = logparse.get_inf_from_log(use_zuhe, zuhe_list)

            except_df = logparse.get_except_df()

            # inf_df.to_excel('A:/wangwd/日内强势股/log_parse/因子耗时/因子耗时_io_fixed_%s_%s.xlsx'%(tradeDate, environment))
            #print(factor_df.head())
            skipdf = pd.DataFrame()
            dropindex_df = pd.DataFrame(columns=[0])
            if environment=='UAT_lite' :
                dropindex_path = '/data/group/800463/xiely/save-file/for_wj/daily_mock_stockList/daily_mock_hf_%s_20230505.xlsx' % tradeDatestr
                dropindex_df = pd.read_excel(dropindex_path).set_index(['Unnamed: 0'])
            elif environment.find('UAT') >= 0 :
                dropindex_path = '/data/group/800463/xiely/save-file/for_wj/daily_mock_stockList/daily_mock_fz_%s.xlsx' % tradeDatestr
                dropindex_df = pd.read_excel(dropindex_path).set_index(['Unnamed: 0'])
                # skipdf = pd.read_excel(
                #     '/data/group/800463/xiely/save-file/for_sss/CumAmt/LiftRatio_df_eur_jpt_%s_uat.xlsx'%tradeDatestr).set_index(['stock'])
            elif environment in ['prod','SHEX','SZEX']:
                dropindex_path = '/data/group/800463/xiely/save-file/for_wj/daily_mock_stockList/daily_mock_sp_%s.xlsx'%tradeDatestr
                # skipdf0 = pd.read_excel('/data/group/800463/xiely/save-file/for_sss/CumAmt/LiftRatio_df_eur_jpt_%s_SHEX.xlsx'%tradeDatestr).set_index(['stock'])
                # skipdf1 = pd.read_excel( '/data/group/800463/xiely/save-file/for_sss/CumAmt/LiftRatio_df_eur_jpt_%s_SZEX.xlsx'%tradeDatestr).set_index(['stock'])
                # skipdf = pd.concat([skipdf0,skipdf1])
                dropindex_df = pd.read_excel(dropindex_path).set_index(['Unnamed: 0'])
            elif environment.find('test1') >= 0 or environment.find('night') >= 0:
                # TODO: 对应夜间回放的mock文件路径，主要是修改最后的日期
                dropindex_path = '/data/group/800463/xiely/save-file/for_wj/daily_mock_stockList/daily_mock_hf_%s_20230504.xlsx'%tradeDatestr
                dropindex_df = pd.read_excel(dropindex_path).set_index(['Unnamed: 0'])

            dropindex = list(set(dropindex_df[0].tolist() + skipdf.index.tolist()))
            save_index = list(set(factor_df.index.tolist())-set(dropindex))
            save_index001 = list(set(factor_df001.index.tolist()) - set(dropindex))

            #print(inf_df.head())
            # TODO: 因为没有isSkip和isMock两个key，先注释掉以下4行
            inf_df = inf_df_.copy()
            inf_df001 = inf_df001_.copy()
            # if len(inf_df_) > 0:
            #     inf_df = inf_df_[(inf_df_['isSkip']=='false') & (inf_df_['isMock']=='0')] # .loc[list(set(inf_df.index.tolist())&set(save_index))].sort_index()
            # if len(inf_df001_) > 0:
            #     inf_df001 = inf_df001_[(inf_df001_['isSkip']=='false') & (inf_df001_['isMock']=='0')] # .loc[list(set(inf_df001.index.tolist()) & set(save_index001))].sort_index()
            inf_df = inf_df.loc[list(set(inf_df.index.tolist())&set(save_index))].sort_index()
            inf_df001 = inf_df001.loc[list(set(inf_df001.index.tolist()) & set(save_index001))].sort_index()
            save_index = inf_df.index.tolist()
            save_index001 = inf_df001.index.tolist()
            daily_zt_df = daily_zt_df.loc[list(set(daily_zt_df.index.tolist()) & set(save_index))].sort_index()
            daily_zt_df001 = daily_zt_df001.loc[list(set(daily_zt_df001.index.tolist()) & set(save_index001))].sort_index()
            factor_df.loc[save_index].sort_index().to_excel('/data/group/800463/日内强势股/cpp_log_parse/因子数据/因子数据_%s_%s.xlsx' % (tradeDate, environment))
            print('create file %s' % '/data/group/800463/日内强势股/cpp_log_parse/因子数据/因子数据_%s_%s.xlsx' % (tradeDate, environment))
            factor_df001.loc[save_index001].sort_index().to_excel('/data/group/800463/日内强势股/cpp_log_parse/因子数据/因子数据New_%s_%s.xlsx' % (tradeDate, environment))
            print('create file %s'%'/data/group/800463/日内强势股/cpp_log_parse/因子数据/因子数据New_%s_%s.xlsx' % (tradeDate, environment))
            excel_saver({'930':factor_df_pj2_930,
                     '931':factor_df_pj2_931},'/data/group/800463/日内强势股/cpp_log_parse/因子数据/项目二因子数据_%s_%s.xlsx' % (tradeDate, environment))
            excel_saver({'931sell': factor_df_pj2_931_sell,
                         '930sell': factor_df_pj2_930_sell},
                        '/data/group/800463/日内强势股/cpp_log_parse/因子数据/卖出Sell13因子数据_%s_%s.xlsx' % (tradeDate, environment))
            excel_saver({'930':factor_df_pj3_930,
                         '931': factor_df_pj3_931},
                        '/data/group/800463/日内强势股/cpp_log_parse/因子数据/项目三因子数据_%s_%s.xlsx' % (tradeDate, environment))
            # factor_df_all.to_excel('/data/group/800463/日内强势股/cpp_log_parse/因子数据/全部因子数据_%s_%s.xlsx' % (tradeDate, environment))
            # factor_df_all.to_pickle('/data/group/800463/日内强势股/cpp_log_parse/因子数据/全部因子数据_%s_%s.pkl' % (tradeDate, environment))

            if len(except_df) > 0:
                except_df.to_excel('/data/group/800463/日内强势股/cpp_log_parse/异常报错/异常报错_%s_%s.xlsx' % (tradeDate, environment))
                print('create file %s' % '/data/group/800463/日内强势股/cpp_log_parse/异常报错/异常报错_%s_%s.xlsx' % (tradeDate, environment))
            md_data_path = '/data/group/800463/日内强势股/cpp_log_parse/行情数据/%s_%s/' % (tradeDate, environment)

            model_factor_data_path = '/data/group/800463/日内强势股/cpp_log_parse/模型数据/%s_%s/' % (tradeDate, environment)
            if not os.path.exists(md_data_path):
                os.makedirs(md_data_path)
            if not os.path.exists(model_factor_data_path):
                os.makedirs(model_factor_data_path)
            if len(trade_dic.keys()) != len(now_trade_dic.keys()):
                print('trade_dic和now_trade_dic长度不一致')

            model_total_keys = []
            for model_dict in all_code_model_data.values():
                model_total_keys += list(model_dict.keys())
            model_total_keys = list(np.unique(np.array(model_total_keys)))
            total_keys = list(set(trade_dic.keys()).union(set(now_trade_dic.keys())).union(set(model_total_keys)))

            model_total_keys001 = []
            for model_dict in all_code_model_data001.values():
                model_total_keys001 += list(model_dict.keys())
            model_total_keys001 = list(np.unique(np.array(model_total_keys001)))
            total_keys001 = list(set(trade_dic.keys()).union(set(now_trade_dic.keys())).union(set(model_total_keys001)))

            Total_Trans_dic = {}
            Unique_Buy_dic = {}
            Unique_Sell_dic = {}
            for code in total_keys:
                MD_data, now_trade_data = pd.DataFrame(), pd.DataFrame()
                if code in trade_dic.keys():
                    MD_data = trade_dic[code]
                if code in now_trade_dic.keys():
                    now_trade_data = now_trade_dic[code]
                if code in all_code_model_data.keys():
                    code_model_data = all_code_model_data[code]
                output_dict = {'MD_data': MD_data,
                               'now_trade_data': now_trade_data}
                if len(MD_data)>0:
                    excel_saver(output_dict, '%s%s.xlsx' % (md_data_path, code))
                else:
                    print(code,' not in trade_dic!!!')
                if len(MD_data) == 0:
                    Total_Trans, Unique_Buy, Unique_Sell = 0, 0, 0
                else:
                    Total_Trans, Unique_Buy, Unique_Sell = len(MD_data), len(np.unique(MD_data['TradeBuyNo'])), len(np.unique(MD_data['TradeSellNo']))
                Total_Trans_dic[code] = Total_Trans
                Unique_Buy_dic[code] = Unique_Buy
                Unique_Sell_dic[code] = Unique_Sell
            inf_df['Total_Trans'] = pd.Series(Total_Trans_dic)
            inf_df['Unique_Buy'] = pd.Series(Unique_Buy_dic)
            inf_df['Unique_Sell'] = pd.Series(Unique_Sell_dic)
            # inf_df = inf_df[~inf_df['ZT_Time'].isna()]
            # inf_df001 = inf_df001[~inf_df001['ZT_Time'].isna()]
            if 'ZT_Time' in inf_df.columns.tolist(): # and logparse.environment not in [ 'UAT']:
                inf_df = inf_df.sort_values('ZT_Time')
                print(inf_df['ZT_Time'])
                inf_df['ZT_Time_str'] = inf_df['ZT_Time'].apply(inttime2str)
                daily_zt_df['ZT_Time'] = inf_df['ZT_Time'].loc[daily_zt_df.index]
            inf_df['machine_code'] = pd.Series(logparse.jup_machine_code_dict).loc[inf_df.index].values
            if 'ZT_Time' in inf_df001.columns.tolist():
                inf_df001 = inf_df001.sort_values('ZT_Time')
                inf_df001['ZT_Time_str'] = inf_df001['ZT_Time'].apply(inttime2str)
                daily_zt_df001['ZT_Time'] = inf_df001['ZT_Time'].loc[daily_zt_df001.index]
            inf_df001['machine_code'] = pd.Series(logparse.eur_machine_code_dict).loc[inf_df001.index].values

            tupo_excel_dic = {'每日突破': daily_zt_df,
                              '每日突破New': daily_zt_df001,
                              '每日项目二':daily_pj2_df,
                              '每日项目三': daily_pj3_df,
                              '每日订单': order_info_df,
                              '每日拒绝': unfilled_info_df}
            excel_saver(tupo_excel_dic, '/data/group/800463/日内强势股/cpp_实盘分析记录/每日突破/每日突破_%s_%s.xlsx' % (tradeDatestr, environment))

            if (environment == 'prod') | (environment == 'SHEX') | (environment in [ 'SZEX','SZEX_udp', 'SHEX_beta']):
                if len(order_info_df) == 0:
                    buy_guadan_num = pd.DataFrame()
                    buy_chengjiao_num = pd.DataFrame()
                    sell_guadan_num = pd.DataFrame()
                    sell_chengjiao_num = pd.DataFrame()
                    sell_time_start = pd.DataFrame()
                    sell_time_end = pd.DataFrame()
                else:
                    buy_order_info_df = order_info_df[(order_info_df['orderType'] == 'SplitLastShot')|(order_info_df['orderType']  == 'MRiskSplitShot')|
                                                      (order_info_df['orderType'] == 'JupiterFirstOrder')|(order_info_df['orderType'] == 'MRiskSplitLastShotBuy')|(order_info_df['orderType'] == 'MRiskSplitShotBuy')]
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

                inf_df_dic = {'因子耗时': inf_df,
                              '因子耗时New': inf_df001,
                              '买单统计': buy_statistics,
                              '卖单统计': sell_statistics,
                              '机器统计': pd.Series(logparse.machine_counter_dict),
                              '项目二930样本': inf_df_pj2_930,
                              '项目二931样本': inf_df_pj2_931,
                              'Sell1样本': inf_df_pj2_931_sellv1,
                              'Sell3样本': inf_df_pj2_931_sellv3,
                             # 'Ceres930样本': inf_df_pj3_930,
                              'Ceres931样本': inf_df_pj3_931}
                # -------------- 生产上才分析未成交的原因 -------------------
                if environment == 'prod':
                    hist_non_trade = pd.read_excel('/data/group/800463/日内强势股/cpp_log_parse/因子耗时/因子耗时_%s_%s.xlsx'% (lastdate_h, environment),sheetname = '未成交统计')
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
                            print('未成交样本:%s'%stock)
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
                            # daily_zt_df = pd.read_excel('/data/group/800463/日内强势股/实盘分析记录/每日突破/每日突破_%s_%s.xlsx' % (tradeDatestr, 'prod')).set_index(['Unnamed: 0']) # 目前是jupiter的统计，后续修改jupiter001
                            #Our_qty = daily_zt_df.loc[stock, 'quantity']
                            dummy_index = len(hist_non_trade)
                            hist_non_trade.loc[dummy_index,'发生日期'] = pd.Timestamp(tradeDate)
                            hist_non_trade.loc[dummy_index,'ZT_Time'] = ZT_Time
                            hist_non_trade.loc[dummy_index,'证券代码'] = stock
                            name_data = IO.read_data([lastdate, lastdate]
                                                     , alt='/data/group/800080/warehouse/prod/FCD/CHINA_STOCK/DAILY/SUNTIME/FCD_CHINA_STOCK_DAILY_SUNTIME.h5')
                            hist_non_trade.loc[dummy_index,'证券名称'] = name_data.loc[lastdate,stock]['STOCK_NAME'].values[~0]
                            hist_non_trade.loc[dummy_index,'行情延迟'] = data_lag
                            try:
                                hist_non_trade.loc[dummy_index,'因子模型耗时'] = inf_df.loc[stock][['factor_time_cost','model_time_cost']].sum()
                            except: # 20230713 by fengc 查到原来的代码的bug
                                if stock in inf_df001.index:
                                    hist_non_trade.loc[dummy_index, '因子模型耗时'] = inf_df001.loc[stock][['factor_time_cost', 'model_time_cost']].sum()
                                else:
                                    hist_non_trade.loc[dummy_index, '因子模型耗时'] = 0
                            '''if stock[0] != '6':
                                df_order = mdp.get_data_by_date("Order", stock, tradeDatestr)
                                df_order_need = df_order[
                                    ['MDDate', 'MDTime', 'SecurityID', 'ReceiveDateTime', 'OrderType', 'OrderPrice', 'OrderQty', 'OrderBSFlag', 'OrderIndex']]
                                df_order_need_ZT_check_maybe_we = df_order_need[(df_order_need['OrderQty'] == Our_qty) & \
                                                                                (df_order_need['MDTime'] >= ZT_Time) & \
                                                                                (df_order_need['OrderPrice'] == ZT_price)]
                                print('our order is :',df_order_need_ZT_check_maybe_we.shape[0],df_order_need_ZT_check_maybe_we)
                                if len(df_order_need_ZT_check_maybe_we)>0:
                                    print('MDTime = %s, ZTTime = %s'%(df_order_need_ZT_check_maybe_we.MDTime.values[0],ZT_Time))
                                last_order_time = df_order_need[df_order_need['OrderIndex'] == df_need_normal['TradeBuyNo'].max()]['MDTime'].values[0]
                                last_order_time_cost = cal_time_delta(int(ZT_Time),int(last_order_time))
                                our_time_cost = cal_time_delta(int(ZT_Time), int(df_order_need_ZT_check_maybe_we['MDTime'].values[0]))
                                hist_non_trade.loc[dummy_index, '我方总耗时'] = our_time_cost
                                if  last_order_time_cost== 0:
                                    hist_non_trade.loc[dummy_index, '至少需要加速时间'] = '涨停瞬间封死'
                                    hist_non_trade.loc[dummy_index, '成交理论最小耗时'] = '涨停瞬间封死'
                                elif last_order_time_cost <= 20:
                                    hist_non_trade.loc[dummy_index, '至少需要加速时间'] = '%sms封死'%str(int(last_order_time_cost))
                                    hist_non_trade.loc[dummy_index, '成交理论最小耗时'] = '%sms封死'%str(int(last_order_time_cost))
                                elif our_time_cost >= 3000:
                                    hist_non_trade.loc[dummy_index, '至少需要加速时间'] = '等待风控过久'
                                    hist_non_trade.loc[dummy_index, '成交理论最小耗时'] = '等待风控过久'
                                else:
                                    hist_non_trade.loc[dummy_index, '至少需要加速时间'] = our_time_cost - last_order_time_cost
                                    hist_non_trade.loc[dummy_index, '成交理论最小耗时'] = inf_df.loc[stock][['factor_time_cost','model_time_cost']].sum() - (our_time_cost - last_order_time_cost)'''
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
            elif environment == 'prod_test':
                inf_df_dic = {'因子耗时': inf_df,
                              '机器统计': pd.Series(logparse.machine_counter_dict)}
            elif ('UAT' in environment) | ('night' in environment)|('test' in environment):
                inf_df_dic = {'因子耗时': inf_df,
                              '因子耗时New': inf_df001,
                              '项目二930样本': inf_df_pj2_930,
                              '项目二931样本': inf_df_pj2_931,
                              #'Ceres930样本': inf_df_pj3_930,
                              'Sell1样本': inf_df_pj2_931_sellv1,
                              'Sell3样本': inf_df_pj2_931_sellv3,
                              'Ceres931样本': inf_df_pj3_931,
                              '机器统计': pd.Series(pd.Series(logparse.machine_counter_dict))}

            excel_saver(inf_df_dic, '/data/group/800463/日内强势股/cpp_log_parse/因子耗时/因子耗时_%s_%s.xlsx' % (tradeDate, environment))

            '''if logparse.environment in ['prod','UAT']:
                import ftplib
    
                host = '168.8.2.68'
                username = 'xquant'
                password = 'Xquant-32'
    
                f = ftplib.FTP(host)  # 实例化FTP对象
                f.login(username, password)  # 登录
                f.encoding = 'GB2312'
                ftp_upload(f,'XQuant/013550/temp/因子耗时_%s_%s.xlsx'%(tradeDate,environment),
                           '/data/group/800463/日内强势股/cpp_log_parse/因子耗时/因子耗时_%s_%s.xlsx'%(tradeDate,environment))
                ftp_upload(f,'XQuant/013550/temp/每日突破_%s_%s.xlsx'%(tradeDatestr,environment),
                           '/data/group/800463/日内强势股/实盘分析记录/每日突破/每日突破_%s_%s.xlsx'%(tradeDatestr,environment))'''

            if environment == 'prod':
                from dataApi.sendInfo import send_message
                send_message(f'{tradeDate} 实盘cpp日志已解析')