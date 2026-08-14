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
from ProdWork.log_analyse.prod.p4.LogParse import LogParse


if __name__ == "__main__":
    if len(sys.argv) > 1:
        nowdate = sys.argv[1]
        tradeDate = nowdate[:4] + '-' + nowdate[5:7] + '-' + nowdate[8:]
        begindate, enddate = nowdate, nowdate
    else:
        tradeDate = dt.datetime.now().strftime('%Y-%m-%d')
        # tradeDate = '2025-09-08'    # 当天即可
        nowdate = tradeDate[:4] + tradeDate[5:7] + tradeDate[8:]
        begindate, enddate = nowdate, nowdate

    if sys.argv[2:]:
        environment_lst = sys.argv[2:]
    else:
        environment_lst = ['prod', 'UAT']
        # environment_lst =['UAT']
        # environment_lst =['night3']
        # environment_lst =['test']
        # environment_lst =['thread']
        # environment_lst =['UAT']
        # environment_lst =['xdev']

    for date in s.tradingday(begindate, enddate):
        tradeDate = f'{date[:4]}-{date[4:6]}-{date[6:]}'
        tradeDatestr = tradeDate[:4] + tradeDate[5:7] + tradeDate[-2:]
        lastdate = s.tradingday(tradeDatestr, -2)[0]
        lastdate_h = pd.Timestamp(s.tradingday(tradeDatestr, -2)[0]).strftime('%Y-%m-%d')
        for environment in environment_lst:
            print(tradeDate, environment, '\n')
            # ------------ 按环境加载日志的目录 ---------------
            import gzip
            file_name = f'/data/group/800463/StrategyLog/prd/{environment}.CeresStrategy-{tradeDate}.log.gz'
            if environment == 'UAT':
                file_list = list(sorted(list(filter(lambda x: f'{tradeDate}' in x and 'CeresStrategy' in x, os.listdir('/data/group/800463/StrategyLog/xsim/')))))
                # file_list = list(sorted(list(filter(lambda x: f'20250723' in x and 'CeresStrategy' in x, os.listdir('/data/group/800463/StrategyLog/xsim/')))))
                file_name = '/data/group/800463/StrategyLog/xsim/' + file_list[0]
                # file_name = f'/data/group/800463/StrategyLog/sim/CeresStrategy-{tradeDate}.log.gz'
                # file_name = f'/data/group/800463/日内强势股/p4_log/sim/P4Strategy-{tradeDate}.log.gz'
            if 'night' in environment:
                file_list = list(sorted(list(filter(lambda x: f'{tradeDate}' in x and 'CeresStrategy' in x, os.listdir('/data/group/800463/StrategyLog/xsim/')))))
                file_name = '/data/group/800463/StrategyLog/xsim/' + file_list[-1]
                # file_name = f'/data/group/800463/StrategyLog/sim/CeresStrategy-{tradeDate}.log.gz'
            if environment == 'prod':
                file_name = '/data/group/800463/StrategyLog/prd/StrongStrategy-%s.log.gz' % tradeDate
            if environment == 'SHEX':
                file_name = '/data/group/800463/StrategyLog/prd/SHEX.EventDrivenCpp-' + tradeDate + '.log.gz'
            if environment == 'SZEX':
                file_name = '/data/group/800463/StrategyLog/prd/SZEX.EventDrivenCpp-' + tradeDate + '.log.gz'
            if environment == 'test':
                # file_name = '/data/group/800463/xiely/save-file/forFc/log/log_local_20230629.txt'
                file_name = f'/data/group/800463/日内强势股/p4_log/sim/EventDrivenStrategy-{tradeDate}.gz'
            if environment in ['thread', 'xdev', 'xdev2', 'xdev3']:
                # file_name = f'/data/user/013551/forXT/log/local_log/eventdriven_log/20231108-xdev38-p4.log'
                # file_name = f'/data/user/013551/forXT/log/local_log/p4/p4_log_xdev_20240119.log'
                # file_name = f'/data/group/800463/xiely/save-file/log/{tradeDate.replace("-", "")}_shsz.log'
                # file_name = f'/data/user/013551/forXT/P4/log/20250319/p4_{tradeDatestr}_shsz.log'
                # file_name = f'/data/user/013551/forXT/P4/log/20250320/xdev_p4_{tradeDatestr}.log'
                # file_name = f'/data/user/013551/forXT/P4/log/{nowdate}_type1.log'
                # file_name = f'/data/user/013551/forXT/Ceres/log/{nowdate}_type1.log'
                file_name = f'/data/user/015614/shared/for_XT/Ceres/logs/ceres_20250722.log'

            print(file_name)

            # while not os.path.exists(file_name):
            #     print('等待%s日志中'%environment)
            #     time.sleep(60)

            sz_log_fpath = f'/data/group/800463/StrategyLog/prd/SZEX.CeresStrategy-{tradeDate}.log.gz'
            sh_log_fpath = f'/data/group/800463/StrategyLog/prd/SHEX.CeresStrategy-{tradeDate}.log.gz'
            if environment == 'prod' and os.path.exists(sz_log_fpath):
                sz_file = gzip.GzipFile(sz_log_fpath)
                sz_lines = sz_file.readlines()
                # copyfile(sz_log_fpath, '/data/group/800463/日内强势股/p4_log/SZEX.P4Strategy-%s.log.gz' % tradeDate)
                # print(f'from {sz_log_fpath} to /data/group/800463/日内强势股/p4_log/SZEX.P4Strategy-{tradeDate}.log.gz 上传成功')
            else:
                sz_lines = []

            if environment == 'prod' and os.path.exists(sh_log_fpath):
                sh_file = gzip.GzipFile(sh_log_fpath)
                sh_lines = sh_file.readlines()
                # copyfile(sh_log_fpath, f'/data/group/800463/日内强势股/p4_log/SHEX.P4Strategy-{tradeDate}.log.gz')
                # print(f'from {sh_log_fpath} to /data/group/800463/日内强势股/p4_log/SHEX.P4Strategy-{tradeDate}.log.gz 上传成功')
            else:
                sh_lines = []

            # if environment == 'UAT' and os.path.exists(file_name):
            #     uat_file = gzip.GzipFile(file_name)
            #     uat_lines = uat_file.readlines()
            #     copyfile(file_name, '/data/group/800463/日内强势股/p4_log/sim/P4Strategy-%s.log.gz' % tradeDate)
            #     print('from %s to /data/group/800463/日内强势股/p4_log/sim/P4Strategy-%s.log.gz 上传成功' % (file_name, tradeDate))

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
                other_lines = list(filter(lambda x: 'INFO' in str(x) and 'algo' in str(x), other_lines))
            else:
                other_lines = []

            lines = other_lines + sh_lines + sz_lines
            lp_inst = LogParse(environment, tradeDatestr, lines)
            print('日志数据读取完毕\n', len(lp_inst.lines))

            # 拆分日志
            log_split_path = f'/data/group/800463/日内强势股/p4_log_parse/日志拆分/{tradeDatestr}_{environment}环境/'
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
            inf_df_p4, trade_dic, now_trade_dic, order_info_df, unfilled_info_df, new_trade_dic, factor_df_p4, \
            factor_df_p4930, daily_zt_df_p4, all_code_model_data_p4 = lp_inst.start_parsing()

            except_df = lp_inst.get_except_df()
            save_index_p4 = list(set(factor_df_p4.index.tolist()))

            # TODO: 因为没有isSkip和isMock两个key，先注释掉以下4行
            inf_df_p4 = inf_df_p4.copy()
            inf_df_p4 = inf_df_p4.loc[list(set(inf_df_p4.index.tolist()) & set(save_index_p4))].sort_index()
            save_index_p4 = inf_df_p4.index.tolist()
            daily_zt_df_p4 = daily_zt_df_p4.loc[list(set(daily_zt_df_p4.index.tolist()) & set(save_index_p4))].sort_index()

            excel_saver({'930': factor_df_p4930.loc[save_index_p4].sort_index(),
                         '931': factor_df_p4.loc[save_index_p4].sort_index()},
                        '/data/group/800463/日内强势股/p4_log_parse/因子数据/因子数据P4_%s_%s.xlsx' % (tradeDate, environment))
            print('create file %s' % '/data/group/800463/日内强势股/p4_log_parse/因子数据/因子数据P4_%s_%s.xlsx' % (tradeDate, environment))

            if len(except_df) > 0:
                except_df.to_excel('/data/group/800463/日内强势股/p4_log_parse/异常报错/异常报错_%s_%s.xlsx' % (tradeDate, environment))
                print('create file %s' % '/data/group/800463/日内强势股/p4_log_parse/异常报错/异常报错_%s_%s.xlsx' % (tradeDate, environment))
            md_data_path = '/data/group/800463/日内强势股/p4_log_parse/行情数据/%s_%s/' % (tradeDate, environment)
            model_factor_data_path = '/data/group/800463/日内强势股/p4_log_parse/模型数据/%s_%s/' % (tradeDate, environment)

            if not os.path.exists(md_data_path):
                os.makedirs(md_data_path)
            if not os.path.exists(model_factor_data_path):
                os.makedirs(model_factor_data_path)
            if len(trade_dic.keys()) != len(now_trade_dic.keys()):
                print('trade_dic和now_trade_dic长度不一致')

            model_total_keys_p4 = []
            for model_dict in all_code_model_data_p4.values():
                model_total_keys_p4 += list(model_dict.keys())
            model_total_keys_p4 = list(np.unique(np.array(model_total_keys_p4)))
            total_keys_p4 = list(set(trade_dic.keys()).union(set(now_trade_dic.keys())).union(set(model_total_keys_p4)))

            if 'ZT_Time' in inf_df_p4.columns.tolist():
                inf_df_p4 = inf_df_p4.sort_values('ZT_Time')
                inf_df_p4['ZT_Time_str'] = inf_df_p4['ZT_Time'].apply(inttime2str)
                daily_zt_df_p4['ZT_Time'] = inf_df_p4['ZT_Time'].loc[daily_zt_df_p4.index]
            inf_df_p4['machine_code'] = pd.Series(lp_inst.machine_code_dict).loc[inf_df_p4.index].values

            # tupo_excel_dic = {'每日突破P4': daily_zt_df_p4,
            #                   '每日订单': order_info_df,
            #                   '每日拒绝': unfilled_info_df}
            # excel_saver(tupo_excel_dic, '/data/group/800463/日内强势股/p4_log_parse/每日突破/每日突破_%s_%s.xlsx' % (tradeDatestr, environment))

            daily_tupo = pd.read_excel('/data/group/800463/日内强势股/p4_log_parse/每日突破/每日突破_%s_%s.xlsx' % (tradeDatestr, environment), sheet_name='每日目标', index_col=0)
            daily_tupo = daily_tupo.set_index('index')
            inf_df_p4['target_amt'] = inf_df_p4.index.map(lambda x: daily_tupo.loc[x, 'target_amt'].max() if x in daily_tupo.index else 0)

            inf_df_dic = {'因子耗时P4': inf_df_p4,
                          '机器统计': pd.Series(pd.Series(lp_inst.machine_counter_dict))}

            excel_saver(inf_df_dic, '/data/group/800463/日内强势股/p4_log_parse/因子耗时/因子耗时_%s_%s.xlsx' % (tradeDate, environment))

