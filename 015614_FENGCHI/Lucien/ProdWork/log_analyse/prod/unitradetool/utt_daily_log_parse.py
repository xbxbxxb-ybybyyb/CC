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
from ProdWork.log_analyse.prod.unitradetool.LogParse import LogParse



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
        # environment_lst =['night']
        # environment_lst =['night2']
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
            file_name = f'/data/group/800463/StrategyLog/prd/{environment}.UniTradeTool-{tradeDate}.log.gz'
            if environment == 'UAT':
                file_list = list(sorted(list(filter(lambda x: f'{tradeDate}' in x and 'UniTradeTool' in x, os.listdir('/data/group/800463/StrategyLog/xsim/')))))
                # file_list = list(sorted(list(filter(lambda x: f'20250723' in x and 'UniTradeTool' in x, os.listdir('/data/group/800463/StrategyLog/xsim/')))))
                file_name = '/data/group/800463/StrategyLog/xsim/' + file_list[0]
                # file_name = f'/data/group/800463/StrategyLog/sim/UniTradeTool-{tradeDate}.log.gz'
                # file_name = f'/data/group/800463/日内强势股/utt_log/sim/UniTradeTool-{tradeDate}.log.gz'
            if 'night' in environment:
                file_list = list(sorted(list(filter(lambda x: f'{tradeDate}' in x and 'UniTradeTool' in x, os.listdir('/data/group/800463/StrategyLog/xsim/')))))
                file_name = '/data/group/800463/StrategyLog/xsim/' + file_list[-1]
                # file_name = '/data/group/800463/StrategyLog/sim/StrongStrategy.log.gz/EventDrivenCpp-%s.log.gz' % tradeDate
            if environment == 'SHEX':
                file_name = '/data/group/800463/StrategyLog/prd/SHEX.UniTradeTool-' + tradeDate + '.log.gz'
            if environment == 'SZEX':
                file_name = '/data/group/800463/StrategyLog/prd/SZEX.UniTradeTool-' + tradeDate + '.log.gz'
            if environment == 'test':
                # file_name = '/data/group/800463/xiely/save-file/forFc/log/log_local_20230629.txt'
                # file_name = f'/data/group/800463/日内强势股/utt_log/sim/UniTradeTool-{tradeDate}.gz'
                file_name = f'/data/user/015614/shared/for_XT/Ceres/logs/20250722/utt-20241009.log'

            if environment in ['thread', 'xdev', 'xdev2', 'xdev3']:
                # file_name = f'/data/user/013551/forXT/log/local_log/eventdriven_log/20231108-xdev38-utt.log'
                # file_name = f'/data/user/013551/forXT/log/local_log/utt/utt_log_xdev_20240119.log'
                # file_name = f'/data/group/800463/xiely/save-file/log/{tradeDate.replace("-", "")}_shsz.log'
                # file_name = f'/data/user/013551/forXT/Ceres/log/20250319/utt_{tradeDatestr}_shsz.log'
                # file_name = f'/data/user/013551/forXT/Ceres/log/20250320/xdev_utt_{tradeDatestr}.log'
                # file_name = f'/data/user/013551/forXT/Ceres/log/{nowdate}_type1.log'
                file_name = f'/data/group/800463/StrategyLog/sim/UniTradeTool-{tradeDate}.log.gz'

            print(file_name)

            # while not os.path.exists(file_name):
            #     print('等待%s日志中'%environment)
            #     time.sleep(60)

            sz_log_fpath = f'/data/group/800463/StrategyLog/prd/SZEX.UniTradeTool-{tradeDate}.log.gz'
            sh_log_fpath = f'/data/group/800463/StrategyLog/prd/SHEX.UniTradeTool-{tradeDate}.log.gz'
            if environment == 'prod' and os.path.exists(sz_log_fpath):
                sz_file = gzip.GzipFile(sz_log_fpath)
                sz_lines = sz_file.readlines()
            else:
                sz_lines = []

            if environment == 'prod' and os.path.exists(sh_log_fpath):
                sh_file = gzip.GzipFile(sh_log_fpath)
                sh_lines = sh_file.readlines()
            else:
                sh_lines = []

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
                # other_lines = list(filter(lambda x: 'INFO' in str(x) and 'algo' in str(x), other_lines))
            else:
                other_lines = []

            lines = other_lines + sh_lines + sz_lines
            lp_inst = LogParse(environment, tradeDatestr, lines)
            print('日志数据读取完毕\n', len(lp_inst.lines))

            # 拆分日志
            log_split_path = f'/data/group/800463/日内强势股/utt_log_parse/日志拆分/{tradeDatestr}_{environment}环境/'
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
            inf_df_utt, order_info_df, unfilled_info_df, daily_zt_df_utt = lp_inst.start_parsing()

            except_df = lp_inst.get_except_df()

            if len(except_df) > 0:
                except_df.to_excel('/data/group/800463/日内强势股/utt_log_parse/异常报错/异常报错_%s_%s.xlsx' % (tradeDate, environment))
                print('create file %s' % '/data/group/800463/日内强势股/utt_log_parse/异常报错/异常报错_%s_%s.xlsx' % (tradeDate, environment))


            tupo_excel_dic = {'每日突破': daily_zt_df_utt,
                              '每日订单': order_info_df,
                              '每日拒绝': unfilled_info_df,
                              '每日目标': inf_df_utt}
            excel_saver(tupo_excel_dic, '/data/group/800463/日内强势股/utt_log_parse/每日突破/每日突破_%s_%s.xlsx' % (tradeDatestr, environment))

            if len(daily_zt_df_utt) == 0:
                daily_zt_df_utt['subject'] = 0
            if len(order_info_df) == 0:
                order_info_df['actionSource'] = 0

            # NOTE：by fengc: 保存到各个低频策略中
            daily_zt_df_utt1 = daily_zt_df_utt.query('subject == "ceres1"')
            order_info_df1 = order_info_df.query('actionSource == "Ceres1"')
            inf_df_utt1 = inf_df_utt.query('subject == "ceres1"')
            order_info_df1['actionSource'] = 'Ceres'
            order_info_df1['orderType'] = 'CeresBuy'
            unfilled_info_df1 = unfilled_info_df
            tupo_excel_dic1 = {'每日突破Ceres': daily_zt_df_utt1,
                              '每日订单': order_info_df1,
                              '每日拒绝': unfilled_info_df1,
                               '每日目标': inf_df_utt1}
            excel_saver(tupo_excel_dic1, '/data/group/800463/日内强势股/ceres_log_parse/每日突破/每日突破_%s_%s.xlsx' % (tradeDatestr, environment))

            daily_zt_df_utt2 = daily_zt_df_utt.query('subject == "ceres2"')
            order_info_df2 = order_info_df.query('actionSource == "Ceres2"')
            inf_df_utt2 = inf_df_utt.query('subject == "ceres2"')
            order_info_df2['actionSource'] = 'P4'
            order_info_df2['orderType'] = 'CeresBuy'
            unfilled_info_df2 = unfilled_info_df
            tupo_excel_dic2 = {'每日突破P4': daily_zt_df_utt2,
                              '每日订单': order_info_df2,
                              '每日拒绝': unfilled_info_df2,
                               '每日目标': inf_df_utt2}
            excel_saver(tupo_excel_dic2, '/data/group/800463/日内强势股/p4_log_parse/每日突破/每日突破_%s_%s.xlsx' % (tradeDatestr, environment))

            daily_zt_df_utt3 = daily_zt_df_utt.query('subject == "mimas"')
            order_info_df3 = order_info_df.query('actionSource == "Mimas"')
            inf_df_utt3 = inf_df_utt.query('subject == "mimas"')
            order_info_df3['actionSource'] = 'Mimas'
            order_info_df3['orderType'] = 'MimasBuy'
            unfilled_info_df3 = unfilled_info_df
            tupo_excel_dic3 = {'每日突破Mimas': daily_zt_df_utt3,
                               '每日订单': order_info_df3,
                               '每日拒绝': unfilled_info_df3,
                               '每日目标': inf_df_utt3}
            excel_saver(tupo_excel_dic3, '/data/group/800463/日内强势股/mimas_log_parse/每日突破/每日突破_%s_%s.xlsx' % (tradeDatestr, environment))

